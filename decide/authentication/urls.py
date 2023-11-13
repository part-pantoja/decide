from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views
from .views import GetUserView, LogoutView, RegisterView


app_name = 'authentication'

urlpatterns = [
    path('login/', obtain_auth_token),
    #path('logout/', LogoutView.as_view()),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
]
