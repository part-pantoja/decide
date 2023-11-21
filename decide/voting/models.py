from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

from base import mods
from base.models import Auth, Key

class Question(models.Model):

    class TypeChoices(models.TextChoices):
        SINGLE_CHOICE = 'single_choice', 'Single Choice'
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
        POINTS_OPTIONS = 'points_options', 'Points Options'
        OPEN_RESPONSE = 'open_response', 'Open Response'

    desc = models.TextField()
    weight = models.PositiveIntegerField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TypeChoices.choices, default=TypeChoices.SINGLE_CHOICE)

    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()
    points_given = models.PositiveIntegerField(blank=True, null=True)


    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

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
        '''
        The tally is a shuffle and then a decrypt
        '''

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
        else:
            self.do_postproc()

    '''
    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        opts = []
        for opt in options:
            if isinstance(tally, list):
                votes = tally.count(opt.number)
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
    '''

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        opts = []
        if self.question.type == 'open_response':
            # Si es una pregunta de respuesta abierta, agrupa las respuestas
            response_counts = {}
            for vote in tally:
                if vote is not None:
                    response_counts[vote] = response_counts.get(vote, 0) + 1

            for vote, count in response_counts.items():
                opts.append({
                    'option': vote,
                    'votes': count
                })
        else:
            # Para otros tipos de pregunta, realiza el recuento normal
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })

        data = {'type': 'IDENTITY', 'options': opts}
        postp = mods.post('postproc', json=data)

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
        return self.names