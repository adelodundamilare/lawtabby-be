from django.urls import path
from . import views

urlpatterns = [
    path('super_admin_create/', views.create_admin, name='create_subscriptions'),
    path('list/', views.list_subscriptions, name='subscription_list'),

    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('create-portal-session/', views.create_portal_session, name='create_portal_session'),
    path('webhook/', views.stripe_webhook),
]