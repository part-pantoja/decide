from django import forms
from django.forms import DateInput
from .models import *

class VotingForm(forms.ModelForm):    
    name = forms.CharField(max_length=100)
    desc = forms.CharField(max_length=50)
    question = forms.ModelChoiceField(queryset=Question.objects.all())  # Campo para las preguntas existentes

    class Meta:
        model = Voting
        fields = ['name','desc', 'question', 'auths']

    def save(self, commit=True):
        voting = super(VotingForm, self).save(commit=False)
        if commit:
            voting.save()
        return voting