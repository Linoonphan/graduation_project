from django.contrib import admin

# Register your models here.
from yingping.models import Movieinfo,Moviescritic,Movielcritic

admin.site.register(Movieinfo)
admin.site.register(Moviescritic)
admin.site.register(Movielcritic)