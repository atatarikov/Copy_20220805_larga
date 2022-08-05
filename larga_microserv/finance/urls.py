"""cis_larga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include

from finance import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plan', views.plan, name='plan'),
    path('plan_per', views.plan_per, name='plan_per'),
    path('plan_act', views.plan_act, name='plan_act'),
    path('default_list/<str:object_name>', views.default_list),
    path('default_add/<str:object_name>', views.default_add),
    path('default_edit/<str:object_name>/<int:id_obj>', views.default_edit),
    path('copy/<str:object_name>/<int:id_obj>', views.copy),
    path('accounts/', include('django.contrib.auth.urls')),
]
