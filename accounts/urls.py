from django.urls import path
from .views import RegisterView, LoginView, EmailVerificationView, LogoutView, HomeView, PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/', EmailVerificationView.as_view(), name='email_verification'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', HomeView.as_view(), name='home'),
    path('password/forgot/', PasswordResetView.as_view(), name='password_forgot'),
    path('password/reset/', PasswordResetConfirmView.as_view(), name='password_reset'),

]
