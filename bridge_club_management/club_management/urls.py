from django.urls import path
from . import views

urlpatterns = [
    path('', views.front_page, name='front_page'),
    path('substitutlister/', views.substitutlister, name='substitutlister'),
    path('afmeldingslister/', views.afmeldingslister, name='afmeldingslister'),
    path('tilmeldingslister/', views.tilmeldingslister_view, name='tilmeldingslister'),
    path('append_afbud/<int:afmeldingsliste_id>/', views.append_afbud, name='append_afbud'),
]
