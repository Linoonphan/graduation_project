from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from yingping.models import Moviescritic,Movieinfo,Movielcritic


import jieba
import jieba.analyse

from pyecharts import WordCloud
from yingping.forms import MovieForm

import re

LOC_HOST = "/static/ets/js"


def cdview(request):
    template = loader.get_template('worldcloud.html')
    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            movieshname = form.cleaned_data['moviename']
            yearnum = re.match(r'^[0-9]{4}$',movieshname)
            if yearnum:
                yearnum = yearnum.group()
                year = Movieinfo.objects.filter(movie_release_time=yearnum)
                movieyear = []
                for y in year:
                    movieyear.append(y.movie_release_time)
                movieyr = ''.join(movieyear[0])
                try:
                    if movieyr:
                        movie_fc = movie_fenci(movieyr)
                        cwm = gencwm(movie_fc)
                        content = dict(
                            myechart=cwm.render_embed(),
                            host=LOC_HOST,
                            script_list=cwm.get_js_dependencies()
                        )
                        return HttpResponse(template.render(content, request))
                    else:
                        message = '电影不存在！'
                        return render(request, 'worldcloud.html', locals())
                except:
                    message = "电影...！"
                    return render(request, 'worldcloud.html', locals())
            else:
                movienm = Movieinfo.objects.filter(movie_name=movieshname)
                moviesn = []
                for x in movienm:
                    moviesn.append(x.movie_name)
                movienm = ''.join(moviesn)
                try:
                    if movienm:
                        movie_fc = movie_fenci(movienm)
                        cwm = gencwm(movie_fc)
                        content = dict(
                            myechart=cwm.render_embed(),
                            host=LOC_HOST,
                            script_list=cwm.get_js_dependencies()
                        )
                        return HttpResponse(template.render(content, request))
                    else:
                        message = '电影不存在！'
                        return render(request,'worldcloud.html',locals())
                except:
                    message = "电影...！"
                    return render(request, 'worldcloud.html', locals())

    else:
        movie_fc = movie_fenci("2001太空漫游")
        cwm = gencwm(movie_fc)
        content = dict(
            myechart=cwm.render_embed(),
            host=LOC_HOST,
            script_list=cwm.get_js_dependencies()
        )
        return HttpResponse(template.render(content, request))



def movie_fenci(*args):
    fstr = ''.join(args)
    movie_sjustice = Moviescritic.objects.filter(Q(movieinfo__movie_name=fstr)|Q(movieinfo__movie_release_time=fstr))
    movie_ljustice = Movielcritic.objects.filter(Q(movieinfo__movie_name=fstr)|Q(movieinfo__movie_release_time=fstr))
    movie_ju_list = []
    for msc in movie_sjustice:
        movie_ju_list.append(msc.movie_critic)
    for lsc in movie_ljustice:
        movie_ju_list.append(lsc.movie_critic)
    movie_ju_str = '。'.join(movie_ju_list)
    movie_fc = jieba.analyse.extract_tags(movie_ju_str, topK=100, withWeight=True, allowPOS=())
    cloudworldresult = []
    for mlt in movie_fc:
        #fcinfo = set(Movieinfo.objects.values_list('movie_name', 'movie_release_time', 'movie_type').filter(
        #    (Q(moviescritic__movie_critic__contains=mlt[0]) | Q(movielcritic__movie_critic__contains=mlt[0])),(Q(movie_name=fstr)|Q(movie_release_time=fstr))))
        cloudworldresult.append([mlt[0],mlt[1]])
    return cloudworldresult,fstr

def gencwm(result):
    name = []
    value = []

    for cdr in result[0]:
        name.append(cdr[0])
        value.append(cdr[1])

    wordcloud = WordCloud(width=1300,height=620)
    wordcloud.add(result[1],name,value,word_size_range=[20, 100])

    return wordcloud
