from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.views.generic import TemplateView
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from .serializers import UserSerializer
from django.contrib.auth import logout

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
            Token.objects.get_or_create(user=user)
            login(request, user)
            return redirect('bienvenida', username=user.username)
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos')
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
                    Token.objects.get_or_create(user=usuario)
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
    def post(self, request, *args, **kwargs):
        form = UserCreationForm2(request.data)
        errors = []
        if form.is_valid():

            userPost = request.POST.get('email')
            usuarios_con_correo = User.objects.filter(email=userPost)

            if usuarios_con_correo.exists():
                mensaje = "El correo seleccionado ya existe"
                errors = form.errors
                return render(request, 'registro/registry.html', {'form': form, 'errors': errors, 'mensaje':mensaje})
            else:


                user = form.save()

                Token.objects.get_or_create(user=user)
                #Marcar como False el campo is_active
                user.is_active = False
                user.save()

                #token, _ = Token.objects.get_or_create(user=user)
                #return Response({'user_pk': user.pk, 'token': token.key}, status=status.HTTP_201_CREATED)
                return redirect('enviar_correo', username=user.username)
        else:
            #return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
            errors = form.errors
            return render(request, 'registro/registry.html', {'form': form, 'errors': errors})
    def get(self, request):
        form = UserCreationForm2()
        return render(request, 'registro/registry.html', {'form':form})

class SendEmail(APIView):
    def enviar_correo(request, username):
        if request.method == 'GET':
            return render(request, 'registro/sendEmail.html', {'username':username})
        if request.method == 'POST':
            
                
            user = User.objects.filter(username=username).first()
            token2 = default_token_generator.make_token(user)
            #Guardar el token en el campo de first_name del user
            user.first_name = token2
            user.save()
            name = user.username
            email = user.email
            emailCorporativo = settings.EMAIL_HOST_USER
            subject = 'Registro en decide'
            message = 'Bienvenido a decide, gracias por registrarse en nuestra aplicación. Estamos emocionados de tenerte a bordo, ' + name + '.'
            message2 = 'Por favor introduce el codigo en la página que le ha redirigido o ' \
            'http://127.0.0.1:8000/authentication/verificar-correo/' + name + \
            '/ para verificar su identidad: ' + token2
            message3 = 'Si tienes alguna pregunta o necesitas asistencias, no dudes en contactarnos ' + emailCorporativo + '.'
            template = render_to_string('registro/email_template.html', {
                'name':name,
                'email':email,
                'emailCorporativo':emailCorporativo,
                'message':message,
                'message2':message2,
                'message3':message3
            })

            email = EmailMessage(
                subject,
                template,
                settings.EMAIL_HOST_USER,
                [email]
            )

            email.fail_silently = False
            email.send()
            #token, _ = Token.objects.get_or_create(user=user)
            #return Response({'user_pk': user.pk, 'token': token.key}, status=status.HTTP_201_CREATED)
            return redirect('verificar_correo', username=user.username)

class VerifyEmailView(APIView):
    def verificar_codigo(request, username):
        if request.method == 'GET':
            return render(request, 'registro/verification_code.html', {'username':username})
        if request.method == 'POST':
            code = request.POST.get('verification_code')

            usuario_es_token = User.objects.filter(username=username)

            if usuario_es_token.exists():
                usuario = usuario_es_token.first()

                if usuario.first_name == code:
                    usuario.is_active = True
                    usuario.first_name = ''
                    usuario.save()
                    
                    login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, '¡Te has registrado con éxito!')
                    return redirect('bienvenida', username=usuario.username)
                else:
                    messages.error(request, 'Codigo incorrecto, revisa tu email')
                    return render(request, 'registro/verification_code.html')
            else:
                messages.error(request, 'Usuario no registrado')
                return render(request, 'registro/verification_code.html')


class WelcomeView(APIView):
    def get(self, request, username):
        return redirect('home:index')

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

def logout_app(request):
    logout(request)
    return redirect("home:index")
