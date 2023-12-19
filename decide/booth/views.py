import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from census.models import Census
from voting.models import Voting
from django.shortcuts import render

from base import mods


# TODO: check permissions and census
class BoothViewEN(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        return context

def booth_home(request):
    user_votings = list(votaciones_del_usuario(request)) if votaciones_del_usuario(request) else False
    votos = []

    if user_votings:
        filtro = request.GET.get('filtro', None)
        if filtro == 'disponibles' or filtro is None:
            for voting in user_votings:
                for v in voting:
                    if v['start_date'] and not v['end_date']:
                        votos.append(v)
                    elif v['start_date'] and v['end_date']:
                        if v['start_date'] > v['end_date']:
                            votos.append(v)
        elif filtro == 'no_iniciadas':
            for voting in user_votings:
                for v in voting:
                    if not v['start_date']:
                        votos.append(v)
        else:
            for voting in user_votings:
                for v in voting:
                    votos.append(v)

    return render(request, 'booth/booth_home.html', {
        'votings': votos,
        'filtro': request.GET.get('filtro', None)
    })


def votaciones_del_usuario(request):
    usuario = request.user.id
    if usuario is None:
        return False
    censos_lista = list(Census.objects.filter(voter_id=usuario).values())
    voting_ids = []
    for censo in censos_lista:
        voting_ids.append(censo.get("voting_id"))

    votings_list = []
    for voting_id in voting_ids:
        votings_list.append((Voting.objects.filter(id=voting_id).values()))

    return votings_list

def booth_home(request):
    user_votings = list(votaciones_del_usuario(request)) if votaciones_del_usuario(request) else False
    votos = []

    if user_votings:
        filtro = request.GET.get('filtro', None)
        if filtro == 'disponibles' or filtro is None:
            for voting in user_votings:
                for v in voting:
                    if v['start_date'] and not v['end_date']:
                        votos.append(v)
                    elif v['start_date'] and v['end_date']:
                        if v['start_date'] > v['end_date']:
                            votos.append(v)
        elif filtro == 'no_iniciadas':
            for voting in user_votings:
                for v in voting:
                    if not v['start_date']:
                        votos.append(v)
        else:
            for voting in user_votings:
                for v in voting:
                    votos.append(v)

    return render(request, 'booth/booth_home.html', {
        'votings': votos,
        'filtro': request.GET.get('filtro', None)
    })


def votaciones_del_usuario(request):
    usuario = request.user.id
    if usuario is None:
        return False
    censos_lista = list(Census.objects.filter(voter_id=usuario).values())
    voting_ids = []
    for censo in censos_lista:
        voting_ids.append(censo.get("voting_id"))

    votings_list = []
    for voting_id in voting_ids:
        votings_list.append((Voting.objects.filter(id=voting_id).values()))

    return votings_list


class BoothViewES(TemplateView):
    template_name = 'booth/booth_es.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])
        except:
            raise Http404
        
        context['KEYBITS'] = settings.KEYBITS

        return context
    
    
class BoothViewDE(TemplateView):
    template_name = 'booth/booth_de.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])
        except:
            raise Http404
        
        context['KEYBITS'] = settings.KEYBITS
        
        return context