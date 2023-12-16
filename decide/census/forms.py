# forms.py
from django import forms
from .models import Census

class CensusForm(forms.ModelForm):
    class Meta:
        model = Census
        fields = ['voting_id', 'voter_id']
