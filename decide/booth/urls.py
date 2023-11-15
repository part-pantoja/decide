from django.urls import path
from .views import BoothView, booth_home
from django.views.generic import TemplateView


urlpatterns = [
    path('', booth_home, name='booth_home'),
    path('<int:voting_id>/', BoothView.as_view()),
]
