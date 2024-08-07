import os
import shutil
import traceback
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader, PdfWriter
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse

from .models import PdfModel, ProtectedPDF, PDFImageConversion, WordToPdfConversion, WordToPdf, OrganizedPdf, MergedPDF,CompressedPDF, SplitPDF, UnlockPdf
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site
from .utils import convert_other_to_pdf, convert_pdf_to_other, pdf_to_ocr, protect_pdf, merge_pdf, compress_pdf, split_pdf, convert_pdf_to_image, create_zip_file, stamp_pdf_with_text,  organize_pdf, summarize_pdf, unlock_pdf
from .serializers import PDFSerializer, OcrPdfSerializer, ProtectedPDFSerializer, MergedPDFSerializer, CompressedPDFSerializer, SplitPDFSerializer, PDFImageConversionSerializer, StampPdfSerializer, WordToPdfConversionSerializer, OrganizedPdfSerializer, UnlockPdfSerializer

from history.utils import add_to_downloads, add_to_uploads

class ProtectPDFView(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        input_file = request.data.get('input_pdf', None)
        pdf_password = request.data.get('pdf_password', None)

        if not input_file or not pdf_password:
            return Response({'error': 'Incomplete data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            add_to_uploads(request.user, input_file)
            protected_file, full_url = protect_pdf(request, input_file, pdf_password, request.user)
            serializer = ProtectedPDFSerializer(protected_file)

            response_data = {
                'message': 'PDF protection completed',
                'split_pdf': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'protected_file': full_url,
                    },
                }
            return Response(response_data)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadProtectedPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pdf_id, format=None):
        protected_pdf = get_object_or_404(ProtectedPDF, id=pdf_id, user=request.user)
        file_path = protected_pdf.protected_file.path
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{protected_pdf.protected_file.name}"'
        return response



class ProtectedPDFDeleteView(generics.DestroyAPIView):
    queryset = ProtectedPDF.objects.all()
    serializer_class = ProtectedPDFSerializer
    permission_classes = [IsAuthenticated]


class MergePDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        pdf_files = request.FILES.getlist('pdf_files')

        if len(pdf_files) < 2:
            return Response({'error': 'At least two PDFs are required for merging.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user if request.user.is_authenticated else None
            for input_file in pdf_files:
                add_to_uploads(user, input_file)
            merged_pdf, full_url = merge_pdf(request, user, pdf_files)
            serializer = MergedPDFSerializer(merged_pdf)

            response_data = {
                'message': 'PDFs merged and saved successfully',
                'split_pdf': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'merged_file': full_url,
                    },
                }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MergePDFDeleteView(generics.DestroyAPIView):
    queryset = MergedPDF.objects.all()
    serializer_class = MergedPDFSerializer
    permission_classes = [IsAuthenticated]

class CompressPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
            input_pdf = request.FILES.get('input_pdf', None)
            print(input_pdf, 'input_pdf')
            compression_quality = request.data.get('compression_quality', 'recommended')
            print(compression_quality, 'compression_quality')

            if not input_pdf:
                return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = request.user
                add_to_uploads(user, input_pdf)
                compressed_pdf, full_url = compress_pdf(request, user, input_pdf, compression_quality)
                serializer = CompressedPDFSerializer(compressed_pdf)


                response_data = {
                'message': 'PDF compression completed',
                'split_pdf': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'compressed_file': full_url,
                    },
                }
                return Response(response_data)

            except Exception as e:
                return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompressPDFDeleteView(generics.DestroyAPIView):
    queryset = CompressedPDF.objects.all()
    serializer_class = CompressedPDFSerializer
    permission_classes = [IsAuthenticated]



class SplitPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        start_page = int(request.data.get('start_page', 0))- 1
        end_page = int(request.data.get('end_page', 0))- 1

        print(start_page, end_page, 'print')

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            add_to_uploads(user, input_pdf)
            split_pdf_instance, full_url= split_pdf(request, input_pdf, start_page, end_page, user)
            serializer = SplitPDFSerializer(split_pdf_instance)

            response_data = {
                'message': 'PDF splitting completed.',
                'split_pdf': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'split_pdf': full_url,
                },
            }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SplitPDFDeleteView(generics.DestroyAPIView):
    queryset = SplitPDF.objects.all()
    serializer_class = SplitPDFSerializer
    permission_classes = [IsAuthenticated]




class PdfToOtherConversionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        input_file = request.FILES.get('input_pdf')
        format = request.data.get('format', '')

        if not input_file:
            return Response({'error': 'No input file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if not format:
            return Response({'error': 'Conversion format input not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # add_to_uploads(request.user, input_file)
            output_file = convert_pdf_to_other(format, input_file)

            instance = PdfModel(user=request.user)
            instance.pdf.save(output_file.name, output_file)
            instance.save()

            serializer = PDFSerializer(instance, context={'request': request})
            return Response({'message': 'Conversion successful.', 'data': serializer.data})
        except Exception as e:
            traceback.print_exc()
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PDFToImageConversionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            # output_folder = 'pdf_images'
            add_to_uploads(user, input_pdf)
            image_paths = convert_pdf_to_image(input_pdf)

            if len(image_paths) == 1:
                print('working')
                # Only one image, save it directly
                pdf_image_conversion = PDFImageConversion(user=user)
                pdf_image_conversion.zip_file.save(f'page_1.jpeg', ContentFile(image_paths[0]))
                pdf_image_conversion.save()
            else:
                # Multiple images, create a zip file
                # zip_file_path = create_zip_file(image_paths, user)

                zip_file_relative_path, zip_content = create_zip_file(image_paths, user)
                pdf_image_conversion = PDFImageConversion(user=user)
                pdf_image_conversion.zip_file.save(zip_file_relative_path, ContentFile(zip_content))
                pdf_image_conversion.save()

                shutil.rmtree(os.path.dirname(zip_file_relative_path))


            # Construct the full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            zip_file_full_url = f'{base_url}{pdf_image_conversion.zip_file.url}'

            serializer = PDFImageConversionSerializer(pdf_image_conversion)
            response_data = {
                'message': 'PDF to image conversion completed.',
                'conversion_data': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'zip_file': zip_file_full_url,
                },
            }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PDFToImageDeleteView(generics.DestroyAPIView):
    queryset = PDFImageConversion.objects.all()
    serializer_class = PDFImageConversionSerializer
    permission_classes = [IsAuthenticated]






class OtherToPdfConversionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        input_file = request.FILES.get('input_file')

        if not input_file:
            return Response({'error': 'No input file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            add_to_uploads(request.user, input_file)
            buffer_output = convert_other_to_pdf(input_file)

            instance = PdfModel(user=request.user)
            instance.pdf.save(f"output.pdf", ContentFile(buffer_output))
            instance.save()

            serializer = PDFSerializer(instance, context={'request': request})
            return Response({'message': 'Conversion successful.', 'data': serializer.data})
        except Exception as e:
            traceback.print_exc()
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OtherToPdfConversionDeleteView(generics.DestroyAPIView):
    queryset = WordToPdfConversion.objects.all()
    serializer_class = WordToPdfConversionSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        # Perform any additional logic here if needed
        instance.word_to_pdfs.all().delete()  # Delete related WordToPdf instances
        instance.delete()


class OrganizePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        user_order = request.data.get('user_order', '')
        pages_to_exclude = request.data.get('pages_to_exclude', [])
        try:
            # Convert the string to a list
            user_order = list(map(int, user_order.strip('[]').split(',')))
        except ValueError:
            return Response({'error': 'Invalid user order format.'}, status=status.HTTP_400_BAD_REQUEST)


        if not input_pdf or not user_order:
            return Response({'error': 'No input PDF file or user order provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            user_order = list(map(int, user_order))
            add_to_uploads(user, input_pdf)
            converted_file = organize_pdf(input_pdf, user_order, pages_to_exclude, user)

            serializer = OrganizedPdfSerializer(converted_file, context={'request': request}).data

            # add_to_downloads(user, converted_file, f"{input_pdf.name}")

            return Response({'message': 'PDF pages organized successfully.', 'organized_data': serializer})
        except Exception as e:
            traceback.print_exc()
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UnlockPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        password = request.data.get('password', '')

        if not input_pdf or not password:
            return Response({'error': 'Incomplete data. Please provide input PDF,  and password.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            add_to_uploads(request.user, input_pdf)
            unlock_file = unlock_pdf(input_pdf, password, user)
            serializer = UnlockPdfSerializer(unlock_file, context={'request': request})
            return Response({'message': 'PDF unlocked successfully.', 'unlocked_pdf': serializer.data})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UnlockPDFDeleteView(generics.DestroyAPIView):
    queryset = UnlockPdf.objects.all()
    serializer_class = UnlockPdfSerializer
    permission_classes = [IsAuthenticated]



class StampPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        text = request.data.get('text', '')

        if not input_pdf:
            return Response({'error': 'No input PDF file.'}, status=status.HTTP_400_BAD_REQUEST)

        if not text:
            return Response({'error': 'No stamp text provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            add_to_uploads(request.user, input_pdf)
            new_file = stamp_pdf_with_text(input_pdf, text, request.user)


            serializer = StampPdfSerializer(new_file, context={'request': request})
            return Response({'message': 'PDF pages stamped successfully.', 'data': serializer.data})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OcrPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)

        if not input_pdf:
            return Response({'error': 'No input PDF file.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            add_to_uploads(request.user, input_pdf)
            new_file = pdf_to_ocr(input_pdf, request.user)
            print(new_file,'new_file')


            serializer = OcrPdfSerializer(new_file, context={'request': request})
            return Response({'message': 'OCR to PDF conversion successful.', 'data': serializer.data})
        except Exception as e:
            traceback.print_exc()
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SummarizePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)

        if not input_pdf:
            return Response({'error': 'No input PDF file.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            add_to_uploads(request.user, input_pdf)
            response = summarize_pdf(input_pdf, request.user)


            # serializer = PDFSerializer(response, context={'request': request})
            return Response({'message': 'PDF Summary generation successful.', 'data': response})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)