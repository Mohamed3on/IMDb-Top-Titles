from django.db import models
import tmdbsimple as tmdb
from django.shortcuts import redirect

tmdb.API_KEY = '8a028520a2cbcd629af75f08ac266313'


class Title(models.Model):
    id = models.CharField(max_length=200)
    id.primary_key = True
    name = models.CharField(max_length=250)
    score = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def imdb_link(self):
        return 'www.imdb.com/title/' + self.id + '/'

    def API_KEY(self):
        return tmdb.API_KEY
