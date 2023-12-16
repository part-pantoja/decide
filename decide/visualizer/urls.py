from django.urls import path
from .views import VisualizerView, votings

app_name = 'visualizer'

urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view(), name="voting_detail"),
    path('',votings, name='votings')
]
