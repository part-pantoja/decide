import django_filters.rest_framework
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render, redirect

from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth
from .forms import VotingForm

@user_passes_test(lambda u: u.is_staff)
def create_voting(request):
    
    if request.method == 'POST':
        form = VotingForm(request.POST)
        if form.is_valid():
            voting = form.save(commit=False)
            voting.save()
            form.save_m2m()
            return redirect("visualizer:votings")
    else:
        form = VotingForm()
        
    return render(request, "voting/create_voting.html", {"form": form})

@user_passes_test(lambda u: u.is_staff)
def voting_details(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    return render(request, "voting/voting_details.html", {"voting": voting})

def start_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    voting.create_pubkey()
    voting.start_date = timezone.now()
    voting.save()
    return redirect('voting:voting_details', voting_id=voting_id)

def stop_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    voting.end_date = timezone.now()
    voting.save()
    return redirect('voting:voting_details', voting_id=voting_id)

def tally_votes(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id, end_date__lt=timezone.now())
    token = request.session.get('auth-token', '')
    voting.tally_votes(token)
    return redirect('voting:voting_details', voting_id=voting_id)

class VotingView(generics.ListCreateAPIView):
    
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('id', )

    def get(self, request, *args, **kwargs):
        
        idpath = kwargs.get('voting_id')
        self.queryset = Voting.objects.all()
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION
        if version == 'v2':
            self.serializer_class = SimpleVotingSerializer
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'questions', 'question_opt']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        questions_data = request.data['questions']
        
        # Validar que haya al menos una pregunta
        if not questions_data:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear una votación con múltiples preguntas
        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'))

        voting.save()
        
        if questions_data:
            for question_data in questions_data:
                
                if question_data:
                    return Response({}, status=status.HTTP_400_BAD_REQUEST)
                # Validar que 'options' esté presente en los datos de la pregunta
                if 'options' not in question_data:
                    voting.delete()  # Eliminar la votación si hay un error en los datos
                    return Response({}, status=status.HTTP_400_BAD_REQUEST)

                question = Question(desc=question_data['desc'])
                question.save()

                for idx, option_data in enumerate(question_data['options']):
                    option = QuestionOption(question=question, option=option_data, number=idx)
                    option.save()

                voting.questions.add(question)
        else:
            for question_data in questions_data:
                if 'options' not in question_data:
                    voting.delete()  # Eliminar la votación si hay un error en los datos
                    return Response({}, status=status.HTTP_400_BAD_REQUEST)

                question = Question(desc=question_data['desc'])
                question.save()

                for idx, option_data in enumerate(question_data['options']):
                    option = QuestionOption(question=question, option=option_data, number=idx)
                    option.save()

                voting.questions.add(question)

        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        auth.save()
        voting.auths.add(auth)
        return Response({}, status=status.HTTP_201_CREATED)

class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)
    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)

