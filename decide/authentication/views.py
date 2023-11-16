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
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.text import capfirst
from rest_framework import status
from django.http import HttpResponse
from django.views.generic import TemplateView
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.views import LoginView


from allauth.account.auth_backends import AuthenticationBackend
from django.contrib import messages


from .serializers import UserSerializer

UserModel = get_user_model()


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
        

class EmailLoginView(APIView):
    def login_correo(request):
        if request.method == 'GET':
            return render(request, 'registro/loginSinGoogleEmail.html')

        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            usuarios_con_correo = User.objects.filter(email=email)

            if usuarios_con_correo.exists():
                usuario = usuarios_con_correo.first()

                if usuario.check_password(password):
                    login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect('bienvenida', username=usuario.username)
                else:
                    messages.error(request, 'Contraseña incorrecta')
                    return render(request, 'registro/loginSinGoogleEmail.html')

            else:
                messages.error(request, 'Correo no encontrado')
                return render(request, 'registro/loginSinGoogleEmail.html')
        


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
        form = UserCreationForm2(request.data)
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
        form = UserCreationForm2()
        return render(request, 'registro/registry.html', {'form':form})

class WelcomeView(APIView):
    def get(self, request, username):
        return render(request, 'registro/welcome.html', {'username': username})
    


class UserCreationForm2(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }

    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


