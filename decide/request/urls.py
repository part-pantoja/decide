from django.urls import path
from . import views

app_name = 'request'

urlpatterns = [    
    path('create_request/<int:votacion_id>', views.create_request, name="create_request")
]