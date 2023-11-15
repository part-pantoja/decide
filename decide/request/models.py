from django.db import models
from enum import Enum
# Create your models here.

class RequestStatus(Enum):
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    PENDING = 'PENDING'

class Request(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10,
        choices=[(tag, tag.value) for tag in RequestStatus],
        default=RequestStatus.PENDING.value
    )
    
    class Meta:
        unique_together = (('voting_id', 'voter_id'),)

    def __str__(self):
        return f"Request Votacion: {self.voting_id} - Votante: {self.voter_id} ({self.status})"