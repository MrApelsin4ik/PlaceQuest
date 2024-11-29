from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


handler400 = views.disallowed_host_view
handler404 = views.custom_404_view
handler403 = views.custom_403_view
handler500 = views.custom_500_view

urlpatterns = [
    path('', views.main, name='main'),
    path('register_and_login/', views.register_and_login, name='register_and_login'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('edit_attr/<int:id>/', views.edit_attr, name='edit_attr'),
    path('edit_task/<int:id>/', views.edit_task, name='edit_task'),
    path('add_attr/', views.add_attr, name='add_attr'),
    path('add_task/', views.add_task, name='add_task'),
    path('delete_task_file/<int:id>/', views.delete_task_file, name='delete_task_file'),
    path('delete_attr_file/<int:id>/', views.delete_attr_file, name='delete_attr_file'),
    path('attr/<int:id>/', views.attr, name='attr'),
    path('task/<int:id>/', views.task, name='task'),
    path('game', views.game, name='game'),

    path('logout', views.logout_view, name='logout')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)