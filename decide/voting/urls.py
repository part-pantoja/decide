from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('create_voting/', views.create_voting, name='create_voting'),
    path('details/<int:voting_id>', views.voting_details, name='voting_details'),
    path('start/<int:voting_id>', views.start_voting, name='start_voting'),
    path('stop/<int:voting_id>', views.stop_voting, name='stop_voting'),
    path('tally/<int:voting_id>', views.tally_votes, name='tally_votes'),
]
