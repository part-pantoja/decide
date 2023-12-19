from django.urls import path, include
from . import views

app_name = 'census'

urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('add_censo/', views.add_to_census, name='add_to_census')
]
