# forms.py
from django import forms
from .models import Census
from django.core.exceptions import ValidationError
from voting.models import Voting
from django.contrib.auth.models import User

class CensusForm(forms.ModelForm):
    class Meta:
        model = Census
        fields = ['voting_id', 'voter_id']

    
    def clean(self):
        cleaned_data = super().clean()
        voting_id = cleaned_data.get('voting_id')
        voter_id = cleaned_data.get('voter_id')

        # Validar si la votación existe
        try:
            voting = Voting.objects.get(id=voting_id)
        except Voting.DoesNotExist:
            raise ValidationError('This voting does not exist.')

        # Validar si el usuario existe
        try:
            user = User.objects.get(id=voter_id)
        except User.DoesNotExist:
            raise ValidationError('This user does not exist.')
