from django.contrib import admin
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import QuestionOption
from .models import Question
from .models import Voting

from .filters import StartedFilter


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]

class CustomVotingAdminForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomVotingAdminForm, self).__init__(*args, **kwargs)
        # Filtrar las preguntas por tipo solo si hay más de una pregunta seleccionada
        if 'instance' in kwargs and kwargs['instance'] and len(kwargs['instance'].questions.all()) > 1:
            self.fields['questions'].queryset = Question.objects.filter(type='single_choice')

    def clean(self):
        cleaned_data = super().clean()
        questions = cleaned_data.get('questions')

        # Verificar que todas las preguntas sean del tipo 'single_choice' si hay más de una pregunta
        if questions and len(questions) > 1 and not all(q.type == 'single_choice' for q in questions):
            raise ValidationError("Si hay más de una pregunta, todas deben ser del tipo 'single_choice'")

class VotingAdmin(admin.ModelAdmin):
    form = CustomVotingAdminForm
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]

    def add_view(self, request, form_url='', extra_context=None):
        # Puedes agregar lógica personalizada antes de mostrar el formulario de creación aquí
        return super().add_view(request, form_url=form_url, extra_context=extra_context)


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
