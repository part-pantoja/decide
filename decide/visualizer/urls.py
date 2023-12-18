from django.urls import path
from .views import VisualizerView, VisualizerViewDE, VisualizerViewEN


urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('<int:voting_id>/es', VisualizerView.as_view()),
    path('<int:voting_id>/de', VisualizerViewDE.as_view()),
    path('<int:voting_id>/en', VisualizerViewEN.as_view()),
]