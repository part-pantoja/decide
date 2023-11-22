from django.urls import path
from .views import BoothView, booth_home
from django.views.generic import TemplateView

app_name = 'booth'

urlpatterns = [
    path('', booth_home, name='booth_home'),
    path('<int:voting_id>/', BoothView.as_view(), name='booth_detail'),
]
