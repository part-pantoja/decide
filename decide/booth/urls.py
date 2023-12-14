from django.urls import path
from .views import BoothViewES, BoothViewEN, BoothViewDE


urlpatterns = [
    path('<int:voting_id>/', BoothView.as_view()),
    path('<int:voting_id>/es', BoothViewES.as_view()),
    path('<int:voting_id>/', BoothViewEN.as_view()),
    path('<int:voting_id>/de', BoothViewDE.as_view()),
]
