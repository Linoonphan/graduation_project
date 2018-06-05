#-*- coding:utf-8 -*-
from django.db import models

# Create your models here.
#电影列表
class Movieinfo(models.Model):
    movie_num = models.IntegerField(primary_key=True)
    movie_name = models.CharField(max_length=100)
    movie_release_time = models.CharField(max_length=20)
    movie_type = models.CharField(max_length=100)

    class Meta:
        ordering = ["movie_num"]
    def __str__(self):
        return self.movie_name

#短评论
class Moviescritic(models.Model):
    movieinfo = models.ForeignKey(Movieinfo,to_field='movie_num',blank=True,null=True)
    movie_num = models.IntegerField()
    movie_critic = models.TextField()

    class Meta:
        ordering = ["movie_num"]
    def __str__(self):
        return self.movie_critic

#长影评
class Movielcritic(models.Model):
    movieinfo = models.ForeignKey(Movieinfo,to_field='movie_num',blank=True,null=True)
    movie_num = models.IntegerField()
    movie_lcritic_title = models.TextField()
    movie_critic = models.TextField()

    class Meta:
        ordering = ["movie_num"]
    def __str__(self):
        return self.movie_critic
