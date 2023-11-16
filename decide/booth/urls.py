from django.urls import path
from .views import BoothView


urlpatterns = [
    path('<int:pk>/', BoothView.as_view()),
]
