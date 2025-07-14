from django.urls import path
from . import views

urlpatterns = [
    # Dashboard displaying all tasks
    path('', views.dashboard, name='home'),

    # Add a new task
    path('add-task/', views.add_task, name='add_task'),

    # Pomodoro timer start / stop / restart + completion POST
    path('start/<int:task_id>/', views.start_pomodoro, name='start_pomodoro'),

    # (Optional) keep your earlier daily‑note page
    # path('checkin-note/', views.daily_checkin, name='daily_checkin'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),

    # NEW simplified username invite
    path('invite-buddy/', views.invite_buddy, name='invite_buddy'),
    path('signup/', views.signup, name='signup'),

]
