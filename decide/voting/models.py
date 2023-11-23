from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

from base import mods
from base.models import Auth, Key


class Question(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    desc = models.TextField()

    def __str__(self):
        return f"{self.id}: {self.desc}"


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def get_question_identifier(self):
        return f"question_{self.question.id}" if self.question and self.question.id else None
    

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    questions = models.ManyToManyField(Question, related_name='votings')

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

    # def get_votes(self, token='', question=None):
    #     # gettings votes from store
    #     votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
    #     all_votes = []
    
    #     for question in self.questions.all():
    #         question_votes = []
    #         for vote in votes:
    #             print(vote)
    #             if 'question_id' in vote and vote['question_id'] == question.id:
    #                 question_votes.append(vote)

    #         all_votes.append({
    #             'question': question.desc,
    #             'votes': question_votes
    #         })
    #         print("Contenido de los votos:",all_votes)
    #     anon_votes = []
    #     for vote in votes:
    #         # Asumiendo que 'a' y 'b' son las claves que deseas obtener de cada voto
    #         a = vote.get('a', None)
    #         b = vote.get('b', None)

    #         if a is not None and b is not None:
    #             anon_votes.append([a, b])
    #     print("Contenido de los votos:",anon_votes)
    #     # anon votes
    #     votes_format = []
    #     vote_list = []
    #     for vote in votes:
    #         for info in vote:
    #             if info == 'a':
    #                 votes_format.append(vote[info])
    #             if info == 'b':
    #                 votes_format.append(vote[info])
    #         vote_list.append(votes_format)
    #         votes_format = []
    #     print("--------------------------------------", vote_list)
    #     return all_votes

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

    # def tally_votes(self, token=''):
    #     '''
    #     The tally is a shuffle and then a decrypt
    #     '''
    #     all_votes = {}
    #     for question in self.questions.all():
    #         votes = self.get_votes(token, question)
    #         votes_mix=[]
            
    #         for vote_dict in votes:
    #             # Itera sobre el valor asociado a la clave 'votes' en cada diccionario
    #             for votes in vote_dict.get('votes', []):
    #                 print("///////////////////////////////////////", votes)
    #                 if votes['question_id'] == question.id:
    #                     votes_format = []
    #                     for info in votes:
    #                         if info == 'a':
    #                             votes_format.append(votes[info])
    #                         if info == 'b':
    #                             votes_format.append(votes[info])
    #                     votes_mix.append(votes_format)
                        
    #             print("///////////////////////////////////////", votes_mix)

    #         auth = self.auths.first()
    #         shuffle_url = "/shuffle/{}/".format(self.id)
    #         decrypt_url = "/decrypt/{}/".format(self.id)
    #         auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

                        
    #         # first, we do the shuffle
    #         data = { "msgs": votes_mix }
    #         response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
    #                 response=True)
                        
    #         if response.status_code != 200:
    #             data = {"msgs": response.json()}
    #         else:
    #                         # Manejar el error de manera apropiada
    #             print(f"Error: {response.status_code}")

    #         # then, we can decrypt that
    #         print("-------------------------///////////////", votes_mix)
    #         data = {"msgs": response.json()}
    #         response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
    #                 response=True)

    #         if response.status_code != 200:
    #                         # TODO: manage error
    #             pass
                        
    #         all_votes[question.id] = {
    #         'question_id': question.id,
    #         'tally': response.json()  # Store the tally for each question
    #         }

            

    #     self.tally = all_votes
    #     self.save()

    #     self.do_postproc()

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

        # if self.question.type == 'multiple_choice':
        #     self.do_postproc_multiple_choice()
        # elif self.question.type == 'points_options':
        #     self.do_postproc_points_options()
        # else:
        self.do_postproc()

    # def do_postproc(self):
    #     tally = self.tally
    #     print("-------------------------///////////////", tally)
    #     postproc_data = []

    #     for question_key, question_data in tally.items():
    #         print("-------------------------///////////////", question_data)
    #         question_id = question_data['question_id']
    #         question_tally = question_data['tally']

    #         questions = self.questions.all()

    #         opts = []
    #         for question in questions:
    #             if question.id==question_id: 
    #                 options = question.options.all()
    #                 for opt in options:
    #                     if isinstance(question_tally, list):
    #                         votes = question_tally.count(opt.number)
    #                     else:
    #                         votes = 0
    #                     opts.append({
    #                         'option': opt.option,
    #                         'number': opt.number,
    #                         'votes': votes
    #                     })
    #                     print("--------------------------------", opts)
    #             postproc_data.append({
    #                 'question': question.desc,
    #                 'options': opts
    #             })

    #         data = { 'type': 'IDENTITY', 'options': opts , 'postproc_data': postproc_data}
    #         postp = mods.post('postproc', json=data)

    #         self.postproc = postp
    #         self.save()

    def do_postproc(self):
        tally = self.tally
        
        print("este es el tally:", tally)
        votos_unitarios = []

        for voto in tally:
            voto = str(voto)[:-5]
            votos = voto.split('63789')
            
            for voto in votos:
                votos_unitarios.append(int(voto))

        print("Esos son los votos unitarios", votos_unitarios)
        
        dicc_opciones_valores = {}
        indice = -1
        for voto in votos_unitarios:
            indice += 1
            if indice%2==0:
                if voto in dicc_opciones_valores:
                    dicc_opciones_valores[voto].append(votos_unitarios[indice+1])
                else:
                    dicc_opciones_valores[voto]= [votos_unitarios[indice+1]]

        print("Este es el Dic", dicc_opciones_valores) 
        questions = self.questions.all()           
        opts = []
        for question in questions:
            for key, value in dicc_opciones_valores.items():
                if question.id==key: 
                    options = question.options.all()
                    for opt in options:
                        if opt.number in value:
                            votes = value.count(opt.number)
                        else:
                            votes = 0
                        opts.append({
                            'question_id': question.id,
                            'option': opt.option,
                            'number': opt.number,
                            'votes': votes
                        })
                        
        print("Lo que pasamos: ",opts)
        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name