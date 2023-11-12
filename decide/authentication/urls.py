from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

from .views import GetUserView, LogoutView, RegisterView
from django.views.generic import TemplateView 


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path("accounts/", include("allauth.urls")),
    path('google/', TemplateView.as_view(template_name='google/login.html'), name='google-login'),


]
