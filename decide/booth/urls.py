from django.urls import path
from .views import BoothViewES, BoothViewEN, BoothViewDE
from .views import BoothView, booth_home

app_name = 'booth'

urlpatterns = [
    path('<int:voting_id>/', BoothViewEN.as_view()),
    path('<int:voting_id>/es', BoothViewES.as_view()),
    path('<int:voting_id>/en', BoothViewEN.as_view()),
    path('<int:voting_id>/de', BoothViewDE.as_view()),

    path('', booth_home, name='booth_home'),
    path('<int:voting_id>/', BoothView.as_view(), name='booth_detail'),

]
