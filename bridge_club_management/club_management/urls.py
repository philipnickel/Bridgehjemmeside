
from django.urls import path
from . import views

urlpatterns = [
    path('', views.front_page, name='front_page'),
    path('select_substitut/', views.select_substitut, name='select_substitut'),
    path('login/', views.login, name='login'),
    path('append-afbud/<int:afmeldingsliste_id>/', views.append_afbud, name='append_afbud'),
]
