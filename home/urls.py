from django.urls import path
from .views import HomeView
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='index')
    
]
