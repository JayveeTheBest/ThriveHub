"""
URL configuration for ThriveHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include
from . import views
from .views import search_results, caller_detail, referral_detail


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('referrals/', views.referrals, name='referrals'),
    path('add/', views.add_referral, name='add_referral'),
    path('edit/<int:pk>/', views.edit_referral, name='edit_referral'),
    path('delete/<int:pk>/', views.delete_referral, name='delete_referral'),
    path('form/', include('form.urls')),
    path('responder/', include(('responder.urls', 'responder'), namespace='responder')),
    path('settings/', views.settings, name='settings',),
    path('search/', search_results, name='search_results'),
    path('caller/<int:callerID>/', caller_detail, name='caller_detail'),
    path('referral/<int:id>/', referral_detail, name='referral_detail'),
]
