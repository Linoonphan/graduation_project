#-*- ecoding:utf-8 -*-
import heapq
import json
import re
from collections import defaultdict

from django.http import HttpResponse
from django.template import loader
from yingping.models import Moviescritic,Movieinfo,Movielcritic
from yingping.views.top_view import get_movie_type,filewr
from yingping.forms import MovieTypeForm
from aip import AipNlp
from pyecharts import Scatter, Pie, Bar, Page

LOC_HOST = "/static/ets/js"

APP_ID = '11153995'
API_KEY = 'B53hlQ84NgkxXoCmSOE0vcBL'
SECRET_KEY = 'W9iBPGLk45ko95UFH4Sd58CGFnRMxNsu'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
filename = "scritic_list_json.json"

def emotionview(request):
    template = loader.get_template('emotion.html')
    if request.method == "POST":
        form = MovieTypeForm(request.POST)
        if form.is_valid():
            movie_type = form.cleaned_data['movietype']
            if movie_type:
                st = scat()
                tmv = typemovievisual(movie_type)
                content = dict(
                    host=LOC_HOST,
                    stechart=st.render_embed(),
                    script_list=st.get_js_dependencies(),
                    tmechart=tmv.render_embed(),
                    script_tmv=tmv.get_js_dependencies()
                )
                return HttpResponse(template.render(content, request))
    elif request.method == "GET":
        movie_type = "传记"
        st = scat()
        tmv = typemovievisual(movie_type)
        content = dict(
            host=LOC_HOST,
            stechart=st.render_embed(),
            script_list=st.get_js_dependencies(),
            tmechart=tmv.render_embed(),
            script_tmv=tmv.get_js_dependencies()
        )
        return HttpResponse(template.render(content,request))


'''
# 好评/差评电影对比结果图
def all_movie_name():
    alldata = filewr(emotion_movie_type, filename)
    print(alldata)
    allmovie = defaultdict(list)
    for ad in alldata:
        moviename = ad[1][0][0]
        allmovie[moviename].append(ad[3])
    moviegba = defaultdict(list)
    for key,values in allmovie.items():
        gmamt = values.count(2)
        bmamt = values.count(0)
        moviegba[key].append(gmamt)
        moviegba[key].append(bmamt)
        moviegba[key].append(len(values))
    moviecriticrate = defaultdict(list)
    for key,values in moviegba.items():
        mgr = values[0]/values[2]
        mbr = values[1]/values[2]
        moviecriticrate[key].append(mgr)
        moviecriticrate[key].append(mbr)
    return moviecriticrate
'''

#好/差评电影类型对比结果图
def all_movie_type():
    alldata = filewr(emotion_movie_type, filename)
    mvty_list = sorted(list(set(get_movie_type())))
    del mvty_list[0]
    all_type_num = []
    good_type_num = []
    bad_type_num = []
    all_type_movie = defaultdict(list)
    for tyli in mvty_list:
        for oni in alldata:
            for mvt in oni[1]:
                pipei = re.compile(tyli)
                finmvty = re.search(pipei,mvt[2])
                if finmvty :
                    typeresult = finmvty.group()
                    if typeresult:
                        all_type_num.append(typeresult)
                        if oni[3]==2:
                            good_type_num.append(typeresult)
                            all_type_gmovie = {}
                            all_type_gmovie[oni[1][0][0]] = 2
                            all_type_movie[typeresult].append(all_type_gmovie)
                        elif oni[3]==0:
                            bad_type_num.append(typeresult)
                            all_type_bmovie = {}
                            all_type_bmovie[oni[1][0][0]] = 0
                            all_type_movie[typeresult].append(all_type_bmovie)
                        else:
                            all_type_mmovie = {}
                            all_type_mmovie[oni[1][0][0]] = 1
                            all_type_movie[typeresult].append(all_type_mmovie)
    result_movie_cc = defaultdict(list)#电影类型中每部电影评论总数
    for tkey,tyvalues in all_type_movie.items():
        movienm_list = []
        for mvoieem in tyvalues:
            for key in mvoieem:
                movienm_list.append(key)
        setmovienm_list = set(movienm_list)
        result_movie_nm = defaultdict(list)
        for mvoieem in tyvalues:
            for mvnm in setmovienm_list:
                for key,value in mvoieem.items():
                    if key == mvnm:
                        result_movie_nm[mvnm].append(value)
        for key,values in result_movie_nm.items():
            result_movie_me = []
            mva = len(values)
            if 2 in values:
                mvg = values.count(2)
            else:
                mvg = 0
            if 1 in values:
                mvm  = values.count(1)
            else:
                mvm = 0
            if 0 in values:
                mvb = values.count(0)
            else:
                mvb = 0
            result_movie_me.append(key)
            mvgr = mvg/mva
            result_movie_me.append(mvgr)
            mvmr = mvm/mva
            result_movie_me.append(mvmr)
            mvbr = mvb/mva
            result_movie_me.append(mvbr)
            result_movie_me.append(mva)
            result_movie_cc[tkey].append(result_movie_me)

    type_movie_top_rate = defaultdict(list) #对应电影类型的情感比例
    for rkey,rvalue in result_movie_cc.items():
        movie_type_cirtic_sort = heapq.nlargest(10,rvalue,key=lambda x:x[4])
        type_movie_top_rate[rkey].append(movie_type_cirtic_sort)


    allall_type_num = {} #总评论数
    setall_type_num = set(all_type_num)
    for atnum in setall_type_num:
        allall_type_num[atnum] = all_type_num.count(atnum)



    allgood_type_num = {} #好评电影类型
    setgood_type_num = set(good_type_num)
    for gtnum in setgood_type_num:
        allgood_type_num[gtnum]=good_type_num.count(gtnum)


    allbad_type_num = {} #差评电影类型
    setbad_type_num = set(bad_type_num)
    for btnum in setbad_type_num:
        allbad_type_num[btnum]=bad_type_num.count(btnum)

    for name in allall_type_num.keys():
        if name not in allgood_type_num.keys():
            allgood_type_num[name] = 0
    for name in allall_type_num.keys():
        if name not in allbad_type_num.keys():
            allbad_type_num[name] = 0

    all_movie_type_amt = defaultdict(list)
    for key, value in allgood_type_num.items():
        all_movie_type_amt[key].append(value)
    for key, value in allbad_type_num.items():
        all_movie_type_amt[key].append(value)
    for key,value in allall_type_num.items():
        all_movie_type_amt[key].append(value)
        all_movie_type_amt[key].append(sum(allall_type_num.values()))

    all_movie_type_rate = defaultdict(list)
    for key,value in all_movie_type_amt.items():
        gmtr = value[0]/value[2]
        bmtr = value[1]/value[2]
        mmtr = (value[2]-value[0]-value[1])/value[2]
        tyinall =value[2]/value[3]
        all_movie_type_rate[key].append(gmtr)
        all_movie_type_rate[key].append(mmtr)
        all_movie_type_rate[key].append(bmtr)
        all_movie_type_rate[key].append(tyinall)
    return type_movie_top_rate,all_movie_type_rate



def scat():

    scatter = Scatter("电影评论评分对比")
    gde = [6.6,7.5,7.4,7.3,7.5,6.7,7.2,6.4,6.1,8.2]
    bde = [8.2,8.3,8.6,8.7,8.0,7.7,9.1,8.0,6.5,8.1]
    mvne = ["诺斯法拉图", "战舰波将金号", "将军号", "大都会", "棕榈滩的故事", "疯狂世界", "教父", "夺宝奇兵", "霸王别姬", "海底总动员"]
    scatter.add("", gde, bde, mvne, is_visualmap=True, xaxis_name="情感分析结果评分", yaxis_name="影片真实评分",xaxis_min =5,yaxis_min=5,is_label_show=True,label_formatter="{c}")
    return scatter



def typemovievisual(movietye):
    page = Page()
    type_movie_critic_all = all_movie_type()
    mtcrresult = type_movie_critic_all[1]
    typemovie = re.compile(movietye)
    pie = Pie("电影类型评论对比图")
    for tkey, tvalue in mtcrresult.items():
        type = re.match(typemovie, tkey)
        if type:
            pie.add(tkey, ["好评", "中评", "差评"], [ tvalue[0], tvalue[1], tvalue[2]], is_label_show=True)
    page.add(pie)

    tmtresult = type_movie_critic_all[0]
    moviename = []
    mvgr = []
    mvmr = []
    mvbr = []
    for key, values in tmtresult.items():
        type = re.match(typemovie, key)
        if type:
            for value in values[0]:
                moviename.append(value[0])
                mvgr.append(value[1])
                mvmr.append(value[2])
                mvbr.append(value[3])
    bar = Bar(movietye)
    bar.add("好评率", moviename, mvgr, mark_point=["average"])
    bar.add("中评率", moviename, mvmr)
    bar.add("差评率", moviename, mvbr)
    page.add(bar)
    return page


def emotion_movie_type():
    #获取电影id
    mve_nm = Movieinfo.objects.values_list('movie_num').order_by('movie_release_time')
    print(mve_nm)
    movie_nums =[]
    for mr in mve_nm:
        for mn in mr:
            movie_nums.append(mn)
    type_cr_list = [] #最终结果
        #获取情感分析结果
    for mov_nm in movie_nums:
        movie_ju_list = []
        movie_info = Movieinfo.objects.values_list('movie_name','movie_release_time','movie_type').filter(movie_num=mov_nm)
        movie_info = list(movie_info)
        type_critic = Moviescritic.objects.filter(movie_num=mov_nm)
        if type_critic.exists():
            for msc in type_critic:
                movie_ju_list.append(msc.movie_critic)
        for mjs in movie_ju_list:
            try:
                if mjs:
                    result = client.sentimentClassify(mjs)
                    for jc in result['items']:
                        jcm = jc['sentiment']
                        if jcm == 0:
                            emoproport = jc['negative_prob']
                        elif jcm == 2:
                            emoproport = jc['positive_prob']
                        else:
                            if jc['positive_prob'] >= jc['negative_prob']:
                                emoproport = jc['positive_prob']
                            else:
                                emoproport = jc['negative_prob']
                        onelist = [mov_nm,movie_info,emoproport,jcm]
                        print(onelist)
                        type_cr_list.append(onelist)
            except:
                continue
    with open(filename,"w") as f:
        json.dump(type_cr_list,f)



'''
def emvisal():
    style = Style()
    type_movie_critic_all = all_movie_type()
    mtcrresult = type_movie_critic_all[1]
    pie = Pie("电影类型评论对比图",**style.init_style)
    pie_style = style.add(
        radius=[8,11],
        label_pos="center",
        is_label_show=True,
        label_text_color=None,
    )
    dict_slice = lambda adict, start, end: {k: adict[k] for k in list(adict.keys())[start:end]}
    d1 = dict_slice(mtcrresult,0,5)
    d2 = dict_slice(mtcrresult,5,10)
    d3 = dict_slice(mtcrresult,10,15)
    d4 = dict_slice(mtcrresult,15,20)
    d5 = dict_slice(mtcrresult,20,25)
    d6 = dict_slice(mtcrresult,25,30)
    x = 0
    for key, value in d1.items():
        x += 15
        pie.add("", [key, "好评", "中评", "差评"], [value[3], value[0], value[1], value[2]], center=[x, 10], **pie_style)
    x = 0
    for key, value in d2.items():
        x += 15
        pie.add("", [key, "好评", "中评", "差评"], [value[3], value[0], value[1], value[2]], center=[x, 25], **pie_style)
    x = 0
    for key, value in d3.items():
        x += 15
        pie.add("", [key, "好评", "中评", "差评"], [value[3], value[0], value[1], value[2]], center=[x, 40], **pie_style)
    x = 0
    for key, value in d4.items():
        x += 15
        pie.add("", [key, "好评", "中评", "差评"], [value[3], value[0], value[1], value[2]], center=[x, 55], **pie_style)
    x = 0
    for key, value in d5.items():
        x += 15
        pie.add("", [key, "好评", "中评", "差评"], [value[3], value[0], value[1], value[2]], center=[x, 70], **pie_style)
    x = 0
    for key, value in d6.items():
        x += 15
        pie.add("", [key, "好评", "中评", "差评"], [value[3], value[0], value[1], value[2]], center=[x, 85],legend_top="bottom", **pie_style)
    return pie
'''




