from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

from base import mods
from base.models import Auth, Key
import math

class Question(models.Model):

    class TypeChoices(models.TextChoices):
        SINGLE_CHOICE = 'single_choice', 'Single Choice'
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
        POINTS_OPTIONS = 'points_options', 'Points Options'
        OPEN_RESPONSE = 'open_response', 'Open Response'
        YESNO_RESPONSE = 'yesno_response', 'YesNo Response'

    desc = models.TextField()
    weight = models.PositiveIntegerField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TypeChoices.choices, default=TypeChoices.SINGLE_CHOICE)
    is_blank_vote_allowed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        is_there_blank_vote = QuestionOption.objects.filter(question=self, option="Blank Vote").exists()
        if self.is_blank_vote_allowed and not is_there_blank_vote:
            opt = QuestionOption(question=self, option='Blank Vote', number=1)
            opt.save()
        elif not self.is_blank_vote_allowed and is_there_blank_vote:
            try:
                opt = QuestionOption.objects.get(question=self, option="Blank Vote")
                opt.delete()
            except QuestionOption.DoesNotExist:
                pass

    def __str__(self):
        return self.desc

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()
    points_given = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save(*args, **kwargs)

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)

class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        votes_format = []
        vote_list = []
        for vote in votes:
            for info in vote:
                if info == 'a':
                    votes_format.append(vote[info])
                if info == 'b':
                    votes_format.append(vote[info])
            vote_list.append(votes_format)
            votes_format = []
        return vote_list

    def tally_votes(self, token=''):

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
            response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        if self.question.type == 'multiple_choice':
            self.do_postproc_multiple_choice()
        elif self.question.type == 'points_options':
            self.do_postproc_points_options()
        elif self.question.type == 'yesno_response':
            self.do_postproc_yesno()
        else:
            self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()
        opts = []
        if self.question.type == 'open_response':
            # Si es una pregunta de respuesta abierta, agrupa las respuestas
            response_counts = {}
            list_votes=[]
            for vote in tally:
                list_votes.append(vote)
                if vote is not None:
                    response_counts[vote] = response_counts.get(vote, 0) + 1

            sorted_votes = sorted(list_votes)

            value = 0
            num_votes = len(list_votes)
            variance = 0
            standard_deviation = 0
            media = 0
            median = 0
            if num_votes != 0:
                #Cálculo de la media
                for vote, count in response_counts.items():
                    value += vote * count
                media = value/num_votes
                # Calcular la varianza
                variance = sum((vote - media) ** 2 * count for vote, count in response_counts.items()) / num_votes

                # Calcular la desviación estándar (raíz cuadrada de la varianza)
                standard_deviation = math.sqrt(variance)

                median_index = len(sorted_votes) // 2

                if len(sorted_votes) % 2 == 1:
                    # Si la cantidad de votos es impar
                    median = sorted_votes[median_index]
                else:
                    # Si la cantidad de votos es par
                    median = (sorted_votes[median_index - 1] + sorted_votes[median_index]) / 2

            for vote, count in response_counts.items():
                opts.append({
                    'option': vote,
                    'votes': count,
                    'media': media,
                    'median': median,
                    'standard_deviation': standard_deviation,
                    'variance': variance,
                })
        else:
            # Para otros tipos de pregunta, realiza el recuento normal
            total = 0
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                    total += votes
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                if total == 0:
                    opts.append({
                        'option': opt.option,
                        'number': opt.number,
                        'votes': votes,
                        'percentage': 0
                    })
                else:
                    opts.append({
                        'option': opt.option,
                        'number': opt.number,
                        'votes': votes,
                        'percentage': (votes/total)*100
                    })
        data = {'type': 'IDENTITY', 'options': opts}
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def do_postproc_yesno(self):

        tally = self.tally
        opts = []

        yes_votes = tally.count(1)
        no_votes = tally.count(2)
        total_votes = yes_votes + no_votes

        yes_ratio = (yes_votes/total_votes) if total_votes > 0 else 0
        no_ratio = (no_votes/total_votes) if total_votes > 0 else 0


        ratio_para_si = 0
        ratio_para_no = 0

        if no_votes != 0 and no_ratio != 0:
            ratio_para_si = yes_ratio/no_ratio
        else:
            ratio_para_si = 1.0

        if yes_votes != 0 and yes_ratio != 0:
            ratio_para_no = no_ratio/yes_ratio
        else:
            ratio_para_no = 1.0

        opts.append({
            'option': 'Si',
            'votes': yes_votes,
            'percentage': (yes_ratio * 100) if total_votes > 0 else 0,
            'ratio': ratio_para_si,
        })

        opts.append({
            'option': 'No',
            'votes': no_votes,
            'percentage': (no_ratio * 100) if total_votes > 0 else 0,
            'ratio': ratio_para_no,
        })

        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        print(opts)

        self.postproc = postp
        self.save()

    def do_postproc_multiple_choice(self):

        tally = self.tally
        options = self.question.options.all()
        votos_unitarios = []

        for voto in tally:
            voto = str(voto)
            votos = voto.split('63789')
            for voto in votos:
                votos_unitarios.append(int(voto))

        opts = []
        for opt in options:
            if isinstance(votos_unitarios, list):
                votes = votos_unitarios.count(opt.number)
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })

        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)


        self.postproc = postp
        self.save()


    def do_postproc_points_options(self):
        tally = self.tally
        options = self.question.options.all()
        votos_unitarios = []

        for voto in tally:
            voto = str(voto)[:-5]
            votos = voto.split('63789')
            for voto in votos:
                votos_unitarios.append(int(voto))

        dicc_opciones_valores = {}
        indice = -1
        for voto in votos_unitarios:
            indice += 1
            if indice%2==0:
                if voto in dicc_opciones_valores:
                    dicc_opciones_valores[voto]+=votos_unitarios[indice+1]
                else:
                    dicc_opciones_valores[voto]=votos_unitarios[indice+1]
        opts = []
        for opt in options:
            if opt.number in dicc_opciones_valores:
                votes = dicc_opciones_valores[opt.number]
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })
        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()
    def __str__(self):
        return self.name