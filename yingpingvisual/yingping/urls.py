from django.conf.urls import url
from .views import emotion_view,cloud_view,top_view
urlpatterns = [
    url(r'^worldcloud/$', cloud_view.cdview, name='worldcloud'),
    url(r'^emotion/$', emotion_view.emotionview, name='emotion'),
    url(r'top/$', top_view.toplistview,name='top')

]