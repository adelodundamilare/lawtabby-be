# views.py in your_app

import json
import traceback
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from .models import PromptSubmission
from rest_framework import status
from .serializers import PromptSubmissionSerializer
from rest_framework.decorators import api_view, permission_classes
from decouple import config
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import openai
import base64
import base64
import requests

from . import utils

class PromptSubmissionViewSet(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PromptSubmissionSerializer

    def post(self, request):

        try:
            prompt = request.data.get('prompt')

            if(prompt is None):
                return Response({'error': '"prompt" field is required'}, status=status.HTTP_400_BAD_REQUEST)

            image = request.data.get('image', None)

            serializer = PromptSubmissionSerializer()

            # print(image, 'image')

            def encode_image(image):
                return base64.b64encode(image.read()).decode('utf-8')

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                    ],
                }
            ]

            if image:
                base64_image = encode_image(image)

                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            payload = {
                "model": "gpt-4-vision-preview",
                "messages": messages,
                "max_tokens": 300
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config('OPENAI_API_KEY')}"
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            print(response.json(), 'okokok')

            content = response.json()['choices'][0]['message']
            # serializer.save(user=self.request.user, response=content)
            return Response({ 'success': True, 'data': content })
        except Exception as e:
            print(e)
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def perform_update(self, serializer):
        prompt = serializer.validated_data['prompt']
        print(prompt, 'pp')
        image = serializer.validated_data.get('image', None)

        print(image, 'image')
        def encode_image(image):
          return base64.b64encode(image.read()).decode('utf-8')

        client = openai(
            api_key=config('OPENAI_API_KEY')
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                ],
            }
        ]

        if image:
            base64_image = encode_image(image)

            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": messages,
            "max_tokens": 300
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config('OPENAI_API_KEY')}"
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        content = response.json()['choices'][0]['message']['content']

        serializer.save(user=self.request.user, response=content)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)



    # def perform_create(self, serializer):
    #     prompt = serializer.validated_data['prompt']
    #     image = serializer.validated_data.get('image', None)

    #     client = OpenAI(
    #         # This is the default and can be omitted
    #         api_key=config('OPENAI_API_KEY')
    #     )

    #     response = client.chat.completions.create(
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": prompt
    #             }
    #         ],
    #         model="gpt-3.5-turbo",

    #     )
    #     print(response, 'response')

    #     content = response.choices[0].message.content

    #     serializer.save(user=self.request.user, response=content)


    # def perform_create(self, serializer):
    #     prompt = serializer.validated_data['prompt']
    #     image = serializer.validated_data.get('image', None)
    #     print(image, 'image')

    #     client = OpenAI(
    #         api_key=config('OPENAI_API_KEY')
    #     )

    #     messages = [
    #         {
    #             "role": "user",
    #             "content": prompt,
    #         }
    #     ]

    #     if image:
    #         # Encode the image in base64
    #         base64_image = base64.b64encode(image.read()).decode('utf-8')

    #         messages[0]["content"].append({
    #             "type": "image",
    #             "data": base64_image
    #         })

    #     response = client.chat.completions.create(
    #         messages=messages,
    #         model="gpt-4-vision-preview",  # Use the appropriate model
    #     )

    #     content = response.choices[0].message['content']

    #     serializer.save(user=self.request.user, response=content)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def summarize(request):

    try:
        note = request.data.get('prompt')
        if not note:
            return Response({'error': 'Prompt is required'}, status=400)

        prompt = f"""
            Summarize the main points of the following text in 150-200 words, focusing on the key ideas, arguments, and conclusions:

            {note}

            Please condense the text into a concise and clear summary, highlighting the most important information and omitting unnecessary details. Use your own words and avoid quoting the original text. Aim for a summary that is accurate, informative, and easy to understand.
        """

        summary = utils.chat_ai(prompt)

        return Response({'message': 'Summary generated successfully','data': summary}, status=200)


    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)