from django.db import models

# Create your models here.
class Satistics(models.Model):
    option = models.ForeignKey('voting.QuestionOption', related_name='vote_statistics', on_delete=models.CASCADE)
    voting = models.ForeignKey('voting.Voting', related_name='vote_statistics', on_delete=models.CASCADE)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.option} - Votes: {self.vote_count}"

    def get_vote_statistics(self):
        update_option_vote_statistics(self)
        return OptionVoteStatistic.objects.filter(voting=self)
