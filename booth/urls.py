from django.urls import path
from .views import BoothView

app_name = 'booth'

urlpatterns = [
    path('<int:voting_id>/', BoothView.as_view(), name='booth_detail'),
    
]
