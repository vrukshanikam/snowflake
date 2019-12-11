from django.urls import path
from . import views
urlpatterns = [
     path('', views.homepage, name='homepage'),
     path('accounts/profile/', views.homepage, name='homepage'),
     path('account/logout/', views.Logout, name='Logout'),
     path('messages/', views.messages, name='messages'),
     path('gmailAuthenticate/', views.gmail_authenticate, name='gmail_authenticate'),
     path('dashboard/', views.dashboard, name='dashboard'),
     path('oauth2callback', views.auth_return),
]