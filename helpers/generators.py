from functools import wraps
from django.http import JsonResponse
import stripe

# def subscription_required(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         try:
#             # Assuming you have the user's email in the request
#             customer = stripe.Customer.list(email=request.user.email).data
#             if customer:
#                 subscriptions = stripe.Subscription.list(customer=customer[0].id, status='active')
#                 if subscriptions.data:
#                     return view_func(request, *args, **kwargs)

#             return JsonResponse({'error': 'Subscription required'}, status=403)
#         except stripe.error.StripeError as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return _wrapped_view

# Usage in your views
# @subscription_required
# def protected_view(request):
#     # Your view logic here
#     return JsonResponse({'data': 'This is protected content'})