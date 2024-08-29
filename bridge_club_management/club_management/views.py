# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .models import Configuration, Substitutliste, Afmeldingsliste, Week, DayResponsibility, UserSubstitutAssignment, Day, CustomUser
from django.contrib.auth.models import User
from django.utils.dateformat import DateFormat
import logging
from django.db.models import Prefetch
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def append_afbud(request, afmeldingsliste_id):
    afmeldingsliste = get_object_or_404(Afmeldingsliste, id=afmeldingsliste_id)

    if request.method == 'POST':
        afbud_name = request.POST.get('afbud_name', '').strip()

        if afbud_name:
            if afmeldingsliste.afbud:
                afmeldingsliste.afbud += ', ' + afbud_name
            else:
                afmeldingsliste.afbud = afbud_name

            afmeldingsliste.save()
            return redirect('front_page')
        else:
            # Pass an error message to the template
            context = {
                'afmeldingsliste': afmeldingsliste,
                'error_message': 'Navnet kan ikke være tomt. Prøv igen.'
            }
            return render(request, 'front_page.html', context)


def front_page(request):
    configuration = Configuration.objects.first()
    welcome_text = configuration.welcome_text if configuration else ''
    
    substitutlister = Substitutliste.objects.prefetch_related(
        Prefetch(
            'usersubstitutassignment_set',
            queryset=UserSubstitutAssignment.objects.select_related('user'),
            to_attr='assignments'
        )
    ).all()
    afmeldingslister = Afmeldingsliste.objects.all()
    weeks = Week.objects.all()

    responsibilities = DayResponsibility.objects.select_related('day', 'coordinator').all()
    responsibility_dict = {resp.day.name.lower(): resp.coordinator for resp in responsibilities}

    for substitutliste in substitutlister:
        substitutliste.day_of_week = substitutliste.day.strftime("%A")
        day = Day.objects.get(english_name=substitutliste.day_of_week)
        responsible_coordinator = responsibility_dict.get(day.name.lower())
        if responsible_coordinator:
            substitutliste.responsible_name = responsible_coordinator.get_full_name() or responsible_coordinator.username
            substitutliste.responsible_email = responsible_coordinator.email
        else:
            substitutliste.responsible_name = "Not assigned"
            substitutliste.responsible_email = ""

        substitutliste.assigned_substitutter = [
            {
                'name': assignment.user.get_full_name() or assignment.user.username,
                'phone': assignment.user.phone_number,
                'note': assignment.user.custom_note,
                'email': assignment.user.email,
                'id': assignment.user.id,
                'status': assignment.status
            }
            for assignment in substitutliste.assignments
        ]

    context = {
        'substitutlister': substitutlister,
        'afmeldingslister': afmeldingslister,
        'weeks': weeks,
        'welcome_text': welcome_text,
        'days': Day.objects.all(),
    }

    return render(request, 'front_page.html', context)

def select_substitut(request):
    if request.method == 'POST':
        list_id = request.POST.get('list_id')
        substitut_id = request.POST.get('substitut_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pre_arranged = request.POST.get('pre_arranged') == 'on'
        responsible_email = request.POST.get('responsible_email')
        
        try:
            assignment = UserSubstitutAssignment.objects.get(
                substitutliste_id=list_id,
                user_id=substitut_id
            )
            assignment.status = 'Taken'
            assignment.save()
            
            substitutliste = get_object_or_404(Substitutliste, id=list_id)
            substitut = get_object_or_404(CustomUser, id=substitut_id)
            
            substitut_name = substitut.get_full_name() or substitut.username
            
            # Send email to responsible person
            subject = 'Ny substitut valgt'
            message = f"""
            {name} har valgt substitut {substitut_name} for listen {substitutliste.name} ({substitutliste.day}).

            Kontaktoplysninger på {name}:
            Email: {email}
            Telefon: {phone}

            Aftale lavet på forhånd: {'Ja' if pre_arranged else 'Nej'}
            """
            send_mail(subject, message, 'from@example.com', [responsible_email])
            
            return JsonResponse({'success': True})
        except UserSubstitutAssignment.DoesNotExist:
            logger.error(f"UserSubstitutAssignment not found for list_id={list_id}, substitut_id={substitut_id}")
            return JsonResponse({'success': False, 'error': 'Substitut assignment not found.'})
        except Exception as e:
            logger.error(f"Unexpected error in select_substitut: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def login(request):
    # Logic for handling login functionality
    return render(request, 'login.html')

def afmeldingsliste_detail(request, afmeldingsliste_id):
    afmeldingsliste = get_object_or_404(Afmeldingsliste, id=afmeldingsliste_id)
    return render(request, 'afmeldingsliste_detail.html', {'afmeldingsliste': afmeldingsliste})
