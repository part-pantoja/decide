from django.urls import path
from .views import StatisticsView

urlpatterns = [
    path('',StatisticsView.as_view()),
]
