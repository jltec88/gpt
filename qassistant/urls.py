#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views

app_name = 'qassistant'

urlpatterns = [
    path('', views.index, name='qassistant_index'),
]
