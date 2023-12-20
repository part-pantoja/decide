from django.urls import path
from .views import VisualizerView, votings, VisualizerViewDE, VisualizerViewEN


app_name = 'visualizer'

urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view(), name="voting_detail"),
    path('',votings, name='votings')
    path('<int:voting_id>/es', VisualizerView.as_view()),
    path('<int:voting_id>/de', VisualizerViewDE.as_view()),
    path('<int:voting_id>/en', VisualizerViewEN.as_view()),
