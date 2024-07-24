import traceback
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decouple import config
import stripe
from . import utils

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_admin(request):
    try:
        products_data = [
            {
                "name": "Basic",
                "type": "service",
                "price": [
                    {"amount": 10, "currency": 'usd', "recurring": {'interval': 'month'}},
                    {"amount": 100, "currency": 'usd', "recurring": {'interval': 'year'}}
                ]
            },
            {
                "name": "Premium",
                "type": "service",
                "price": [
                    {"amount": 12, "currency": 'usd', "recurring": {'interval': 'month'}},
                    {"amount": 120, "currency": 'usd', "recurring": {'interval': 'year'}}
                ]
            },
            {
                "name": "Enterprise",
                "type": "service",
                "price": [
                    {"amount": 100, "currency": 'usd', "recurring": {'interval': 'month'}},
                    {"amount": 1000, "currency": 'usd', "recurring": {'interval': 'year'}}
                ]
            }
        ]

        result = utils.create_subscriptions(products_data)

        if not result:
            return Response({'error': 'Failed to create subscriptions'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            'message': 'PDF protection completed',
            'data': result,
        }
        return Response(response_data)
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_subscriptions(request):
    try:
        result = utils.get_products()

        if not result:
            return Response({'error': 'Failed to get products'}, status=400)

        response_data = {
            'message': 'Products retrieved successfully',
            'data': result,
        }
        return JsonResponse(response_data)
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        price_id = request.data.get('price_id')
        page_url = request.data.get('page_url')

        if not price_id:
            return Response({'error': 'Price ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not page_url:
            return Response({'error': 'Page URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        result = utils.create_checkout_session(user=request.user,page_url=page_url, price_id=price_id)

        if not result:
            return Response({'error': 'Failed to subscribe'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            'message': 'Subscription completed',
            'data': result,
        }
        return Response(response_data)
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_portal_session(request):
    try:
        page_url = request.data.get('page_url')

        if not page_url:
            return Response({'error': 'Page URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        result = utils.create_portal_session(user=request.user, page_url=page_url)

        response_data = {'message': 'Success', 'data': result}

        return Response(response_data)
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def stripe_webhook(request):
    endpoint_secret = config('STRIPE_WEBHOOK_SECRET')
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'success': False, 'error': str(e)})

    # Handle the checkout.session.completed event
    session = event['data']['object']


    if event['type'] == 'checkout.session.completed':
        utils.on_checkout_session_completed(session)
    elif event['type'] == 'customer.subscription.deleted':
        utils.on_checkout_session_deleted(session)

    return JsonResponse({'status': 'success'}, status=200)
