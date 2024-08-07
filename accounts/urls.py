from django.urls import path, include
from accounts import views

urlpatterns = [
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('verify_email/<str:verification_code>/', views.EmailVerificationAPIView.as_view(), name='email-verification'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('profile/', views.profile, name='profile'),
    path('update-name/', views.put_update_name, name='put_update_name'),
    path('update-avatar/', views.put_update_avatar, name='put_update_avatar'),

    path("dj-rest-auth/google/login/", views.post_google_login, name="google_login"),
    path("~redirect/", views.UserRedirectView.as_view(), name="redirect"),
    path("dj-rest-auth/microsoft/login/", views.MicrosoftLoginView.as_view(), name="microsoft_login"),
    path("dj-rest-auth/apple/login/", views.AppleLoginView.as_view(), name="apple_login"),

]