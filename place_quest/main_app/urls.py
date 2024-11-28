from django.contrib import admin
from django.urls import path, include
from . import views

handler400 = views.disallowed_host_view
handler404 = views.custom_404_view
handler403 = views.custom_403_view
handler500 = views.custom_500_view

urlpatterns = [
    path('', views.main, name='main'),
    path('register_and_login/', views.register_and_login, name='register_and_login'),
    path('logout', views.logout_view, name='logout')
]