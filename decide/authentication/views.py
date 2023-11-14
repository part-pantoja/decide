from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.views.generic import TemplateView


from .serializers import UserSerializer



def login2(request):
    return render(request, "login.html")



class GoogleView(TemplateView):

    template_name = 'registro/welcome.html'

    def get_context_data(self, **kwargs):
        # Obtén el nombre de usuario del usuario autenticado
        username = self.request.user.username if self.request.user.is_authenticated else None

        # Agrega el nombre de usuario al contexto
        context = super().get_context_data(**kwargs)
        context['username'] = username
        return context
        
        



class LoginView(APIView):
    def get(self, request):
        form = AuthenticationForm() 
        return render(request, 'registro/loginSinGoogle.html', {'form':form})
    
    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            return redirect('bienvenida', username=user.username)
        else:
            
            return render(request, 'registro/loginSinGoogle.html', {'form': form})


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    '''
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)
    '''
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.data)
        errors = []
        if form.is_valid():
            user = form.save()
            token, _ = Token.objects.get_or_create(user=user)
            #return Response({'user_pk': user.pk, 'token': token.key}, status=status.HTTP_201_CREATED)
            return redirect('bienvenida', username=user.username)
        else:
            #return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
            errors = form.errors
            return render(request, 'registro/registry.html', {'form': form, 'errors': errors})
    
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registro/registry.html', {'form':form})

class WelcomeView(APIView):
    def get(self, request, username):
        return render(request, 'registro/welcome.html', {'username': username})

