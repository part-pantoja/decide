from django.views.generic import TemplateView
from django.shortcuts import render
# Create your views here.

class HomeView(TemplateView):
    template_name = 'home/home.html'

def home(request):
    return render(request, 'home/home.html')
