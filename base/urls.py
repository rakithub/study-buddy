from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_page, name='register'),
    path('', views.home, name='home'),
    path('room/<int:pk>/', views.room, name="room"),
    path('create_room/', views.create_room, name="create_room"),
    path('update_room/<int:pk>/', views.update_room, name="update_room"),
    path('delete_room/<int:pk>/', views.delete_room, name="delete_room"),
    path('edit_message/<int:pk>', views.edit_message, name='edit_message'),
    path('delete_message/<int:pk>', views.delete_message, name='delete_message'),
    path('user_profile/<int:pk>', views.user_profile, name='user_profile'),
    path('update_user/<int:pk>', views.update_user, name='update_user'),
    path('topics/', views.topics, name='topics'),
    path('activities/', views.activities, name='activities')
]