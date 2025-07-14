from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from checkins import views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    path('accounts/register/', views.signup, name='signup'),

    path('accounts/login/',  auth_views.LoginView.as_view(),                name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'),  name='logout'),

    path('', include('checkins.urls')),
]
