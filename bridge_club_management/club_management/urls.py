from django.urls import path
from . import views

urlpatterns = [
    path('', views.front_page, name='front_page'),
    path('login/', views.login, name='login'),
    # Add more URL patterns as needed
]

