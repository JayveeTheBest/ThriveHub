from django.urls import path, include
from . import views


app_name = 'responder'

urlpatterns = [
    path('register/', views.registration, name='registration'),
    path('login/', views.responder_login, name='login'),
    path('logout/', views.responder_logout, name='logout'),
]