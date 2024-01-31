from django.urls import path
from .views import *

urlpatterns = [
    #protected_pdf
    path('protect_pdf/', ProtectPDFView.as_view(), name='protect_pdf'),
    path('download_protected_pdf/<int:pdf_id>/', DownloadProtectedPDFView.as_view(), name='download_protected_pdf'),
    path('protect_pdf/delete/<int:pk>/', ProtectedPDFDeleteView.as_view(), name='protect_pdf_delete'),
    #merge pdf
    path('merge_pdf/', MergePDFView.as_view(), name='merge_pdf'),
    path('merge_pdf/delete/<int:pk>/', MergePDFDeleteView.as_view(), name='merge_pdf_delete'),
    #compress pdf
    path('compress_pdf/', CompressPDFView.as_view(), name='compress_pdf'),
    path('compress_pdf/delete/<int:pk>/', CompressPDFDeleteView.as_view(), name='compress_pdf_delete'),

    #split pdf
    path('split_pdf/', SplitPDFView.as_view(), name='split_pdf'),
     path('split_pdf/delete/<int:pk>/', SplitPDFDeleteView.as_view(), name='split_pdf_delete'),

    #pdf to image/jpg
    path('pdf_to_image/', PDFToImageConversionView.as_view(), name='pdf_to_image'),
    #word to pdf
    path('word_to_pdf/', WordToPdfConversionView.as_view(), name='word_to_pdf'),
    #organize pdf
    path('organize_pdf/', OrganizePDFView.as_view(), name='organize_pdf'),
]
