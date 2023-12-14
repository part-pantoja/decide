from django.urls import path
from .views import BoothView, BoothViewSP, BoothViewDE


urlpatterns = [
    path('<int:voting_id>/', BoothView.as_view()),
    path('<int:voting_id>/sp', BoothViewSP.as_view()),
    path('<int:voting_id>/de', BoothViewDE.as_view()),
]
