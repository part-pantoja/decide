import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from voting.models import Voting
from request.models import Request, RequestStatus
from census.models import Census
from base import mods

def create_request(request, votacion_id):
    votacion = get_object_or_404(Voting, id=votacion_id)
    user = request.user 

    if votacion.end_date:
        return render(request, 'request/next_page.html', {'message': 'Lo sentimos, esta votacion está cerrada.'})

    if Census.objects.filter(voter_id=user.id, voting_id=votacion.id).exists():
        return render(request, 'request/next_page.html', {'message': 'Ya estás en el censo de esta votación.'})

    if Request.objects.filter(voter_id=user.id, voting_id=votacion.id).exists():
        return render(request, 'request/next_page.html', {'message': 'Ya tienes una request para esta votación.'})

    
    request_instance = Request.objects.create(voting_id=votacion.id, voter_id=user.id, status=RequestStatus.PENDING.value)

    return render(request, 'request/next_page.html', {'message': 'Solicitud creada con éxito.'})
