from django.views.generic import TemplateView
from voting.models import Voting
from django.shortcuts import render
# Create your views here.

class HomeView(TemplateView):
    template_name = 'home/home.html'

def home(request):
    votings = list(Voting.objects.values())
    return render(request, 'home/home.html', {
        'votings':votings
    })