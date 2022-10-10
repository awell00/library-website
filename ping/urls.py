from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('liste/', views.liste, name='liste'),
    path('add/', views.add, name='add')
]
