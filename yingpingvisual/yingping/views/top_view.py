import json
from collections import Counter
import itertools
import os
from collections import  defaultdict
import re
import heapq

from django.db.models import Count
from django.http import HttpResponse
from django.template import loader
from yingping.models import Moviescritic,Movieinfo,Movielcritic

import jieba
import jieba.analyse
from pyecharts import Bar,Page


LOC_HOST = "/static/ets/js"

movietype = "movietype.json"
allresultfile = "allresult.json"
mostmoviefile = "mostmovie.json"
moviecritic = "moviecritic.json"


def toplistview(request):
    template = loader.get_template('top.html')
    tpre = top_rend()
    content = dict(
        topechart=tpre.render_embed(),
        host=LOC_HOST,
        script_list=tpre.get_js_dependencies()
    )
    return HttpResponse(template.render(content, request))


#本地文件读取
def filewr(func,*args):
    if os.path.isfile(*args):
        with open(*args)as f:
            data = json.load(f)
    else:
        func()
        with open(*args)as f:
            data = json.load(f)
    return data

def findmoviecirtic():
    movie_scritic = Moviescritic.objects.values('movie_num').annotate(Count('movie_num'))
    movie_lcritic = Movielcritic.objects.values('movie_num').annotate(Count('movie_num'))
    return movie_scritic,movie_lcritic


# 去重后的电影类型
def get_movie_type():
    movie_type_all = Movieinfo.objects.values_list('movie_type')
    movie_type_all = list(movie_type_all)
    mvty_lists = []
    for mvtyl in movie_type_all:
        mvty_lists.append(list(mvtyl))
    mvty_list = list(itertools.chain.from_iterable(mvty_lists))
    mvty_lists = []
    for mvt in mvty_list:
        mvty_lists.append(mvt.split(" "))
    mvty_list_result = list(itertools.chain.from_iterable(mvty_lists))
    return mvty_list_result

# 电影类型的数据结果
def movie_type_top():
    mvty_list = get_movie_type()
    movie_type_num = Counter(mvty_list).most_common()
    movie_type_num = heapq.nlargest(10,movie_type_num,key=lambda x: x[1])
    with open(movietype, "w") as f:
        json.dump(movie_type_num, f)

# 所有电影类型评论评论多的
def all_type_critic_top():
    critic = findmoviecirtic()
    movie_contain = dict(Movieinfo.objects.values_list('movie_num', 'movie_type'))
    typeone = defaultdict(list)
    movie_type_result = list(get_movie_type())
    for onetype in movie_type_result:
        if onetype:
            typepr = re.compile(onetype)
            for key,values in movie_contain.items():
                oneresult = re.search(typepr,values)
                if  oneresult:
                    typeone[onetype].append(key)
    allmtc=dict()
    for mts in  critic[0]:
        for mtl in critic[1]:
            if mts['movie_num']==mtl['movie_num']:
                allmtc[mts['movie_num']]=mts['movie_num__count']+mtl['movie_num__count']
    allresult= dict()
    for mt, mn in typeone.items():
        sum = 0
        for fd in mn:
            for mid, crn in allmtc.items():
                if fd == mid:
                    sum +=crn
        allresult[mt]=sum
    allresult = sorted(allresult.items(),key=lambda x:x[1],reverse=True)
    allresult = heapq.nlargest(10,allresult,key=lambda x: x[1])
    with open(allresultfile, "w") as f:
        json.dump(allresult, f)

# 评论数多电影排行
def movie_name_top():
    critic = findmoviecirtic()
    allmtc = dict()
    for mts in  critic[0]:
        for mtl in critic[1]:
            if mts['movie_num']==mtl['movie_num']:
                allmtc[mts['movie_num']]=mts['movie_num__count']+mtl['movie_num__count']
    most_movie= dict()
    for key,values in allmtc.items():
        movie_name = Movieinfo.objects.filter(movie_num=key)
        for me in movie_name:
            most_movie[str(me)]= values
    most_movie = sorted(most_movie.items(), key=lambda x: x[1], reverse=True)
    most_movie = heapq.nlargest(10, most_movie, key=lambda x: x[1])
    with open(mostmoviefile, "w") as f:
        json.dump(most_movie, f)

# 所有影评数据出现最多的词汇
def movie_critic_top():
    movie_scritic = Moviescritic.objects.values_list('movie_critic')
    movie_lcritic = Movielcritic.objects.values_list('movie_critic')
    movie_scritic = list(movie_scritic)
    movie_critic_list =[]
    for msc in movie_scritic:
        movie_critic_list.append(list(msc))
    for lmc in movie_lcritic:
        movie_critic_list.append(list(lmc))
    movie_critic = list(itertools.chain.from_iterable(movie_critic_list))
    movie_critic_str = ''.join(movie_critic)
    movie_fc_top = jieba.analyse.extract_tags(movie_critic_str,topK=10,withWeight=True,allowPOS=())
    with open (moviecritic,"w") as f:
        json.dump(movie_fc_top,f)

def visual(result,name,xiao):
    ttr = []
    v = []
    for x in result:
        ttr.append(x[0])
        v.append(x[1])
    bar = Bar(name)
    bar.add(xiao,ttr,v)
    return bar

def top_rend():
    page = Page()
    allmovietype = filewr(movie_type_top,movietype)
    allcritic = filewr(all_type_critic_top, allresultfile)
    allmoviecritic = filewr(movie_name_top, mostmoviefile)
    allonecritic = filewr(movie_critic_top,moviecritic)

    mostmovietype = visual(allmovietype,"电影类型数量排行榜","电影数")
    mosttypecritic = visual(allcritic,"电影类型评论排行榜","评论数量")
    mostmoviecritic = visual(allmoviecritic,"电影评论排行榜","评论数量")
    mostonecritic = visual(allonecritic,"评论中词汇排行榜","词语权重")

    page.add(mostmovietype)
    page.add(mosttypecritic)
    page.add(mostmoviecritic)
    page.add(mostonecritic)

    return page
