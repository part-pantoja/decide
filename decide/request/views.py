from django.shortcuts import render, get_object_or_404, redirect
from voting.models import Voting
from django.contrib.auth.decorators import user_passes_test, login_required
from request.models import Request, RequestStatus
from census.models import Census

def es_administrador(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url='login-sin-google')
def create_request(request, votacion_id):
    votacion = get_object_or_404(Voting, id=votacion_id)
    user = request.user

    if votacion.end_date:
        return render(request, 'request/next_page.html', {'message': 'Lo sentimos, esta votacion está cerrada.'})

    if Census.objects.filter(voter_id=user.id, voting_id=votacion.id).exists():
        return render(request, 'request/next_page.html', {'message': 'Ya estás en el censo de esta votación.'})

    if Request.objects.filter(voter_id=user.id, voting_id=votacion.id).exists():
        if Request.objects.filter(voter_id=user.id, voting_id=votacion.id).first().status==RequestStatus.PENDING.value:
            return render(request, 'request/next_page.html', {'message': 'Ya tienes una request para esta votación.'})

        if Request.objects.filter(voter_id=user.id, voting_id=votacion.id).first().status==RequestStatus.DECLINED.value:
            return render(request, 'request/next_page.html', {'message': 'Lo sentimos, tu solicitud ha sido rechazada.'})


    Request.objects.create(voting_id=votacion.id, voter_id=user.id, status=RequestStatus.PENDING.value)

    return render(request, 'request/next_page.html', {'message': 'Solicitud creada con éxito.'})

@user_passes_test(es_administrador)
def manage_request(request):
    requests = Request.objects.filter(status=RequestStatus.PENDING.value).all()
    requests_accepted = Request.objects.filter(status=RequestStatus.ACCEPTED.value).all()
    requests_declined = Request.objects.filter(status=RequestStatus.DECLINED.value).all()


    if request.method == 'POST':
        if 'aceptar' in request.POST:
            solicitud_id = request.POST.get('aceptar')
            print(solicitud_id)
            solicitud = Request.objects.get(pk=solicitud_id)
            solicitud.status = RequestStatus.ACCEPTED.value
            solicitud.save()
            Census.objects.create(voting_id=solicitud.voting_id, voter_id=solicitud.voter_id)

        elif 'declinar' in request.POST:
            solicitud_id = request.POST.get('declinar')
            solicitud = Request.objects.get(pk=solicitud_id)
            solicitud.status = RequestStatus.DECLINED.value
            solicitud.save()

        return redirect('request:manage_request')

    return render(request, 'request/manage_request.html',
                  {'requests': requests,
                    'requests_accepted': requests_accepted,
                    'requests_declined':requests_declined})