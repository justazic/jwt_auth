from django.urls import path
from .views import SignUpView, LoginView, LogoutView, ProfileView, ProfileUpdateView, ForgotView, ResetCodeView


urlpatterns = [
    path('sign-up/', SignUpView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile-update/', ProfileUpdateView.as_view()),
    path('code/', ForgotView.as_view()),
    path('reset-code/', ResetCodeView.as_view()),
]