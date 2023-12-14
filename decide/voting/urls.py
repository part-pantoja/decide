from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('create_voting/', views.create_voting, name='create_voting'),
]
