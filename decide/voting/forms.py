from django import forms
from .models import Question, Voting
from django.core.exceptions import ValidationError

class VotingForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    desc = forms.CharField(max_length=50)

    class Meta:
        model = Voting
        fields = ['name','desc', 'questions', 'auths']

    def __init__(self, *args, **kwargs):
        super(VotingForm, self).__init__(*args, **kwargs)
        # Filtrar las preguntas por tipo solo si hay más de una pregunta seleccionada
        if 'instance' in kwargs and kwargs['instance'] and len(kwargs['instance'].questions.all()) > 1:
            self.fields['questions'].queryset = Question.objects.filter(type='single_choice')

    def clean(self):
        cleaned_data = super().clean()
        questions = cleaned_data.get('questions')

        # Verificar que todas las preguntas sean del tipo 'single_choice' si hay más de una pregunta
        if questions and len(questions) > 1 and not all(q.type == 'single_choice' for q in questions):
            raise ValidationError("Si hay más de una pregunta, todas deben ser del tipo 'single_choice'")
        
    def save(self, commit=True):
        voting = super(VotingForm, self).save(commit=False)
        if commit:
            voting.save()
        return voting