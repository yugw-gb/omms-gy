#-*- coding: utf-8 -*-
'''
    Author: smallmi
    Blog: http://www.smallmi.com
'''
from django.contrib import admin

# Register your models here.
from  .models import history,toolsscript



admin.site.register(history)
admin.site.register(toolsscript)