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

    assignments = UserSubstitutAssignment.objects.select_related('substitutliste', 'user')
    assignments_by_substitutliste = {substitutliste.id: [] for substitutliste in substitutlister}
    
    for assignment in assignments:
        assignments_by_substitutliste[assignment.substitutliste.id].append(assignment)

    for substitutliste in substitutlister:
        substitutliste.day_of_week = DateFormat(substitutliste.day).format('l')
        day_name = substitutliste.day_of_week.lower()
        responsible_coordinator = responsibility_dict.get(day_name)
        if responsible_coordinator:
            substitutliste.responsible_name = responsible_coordinator.get_full_name() or responsible_coordinator.username
            substitutliste.responsible_email = responsible_coordinator.email
        else:
            substitutliste.responsible_name = "Ikke tildelt"
            substitutliste.responsible_email = ""

        # Add assigned substitutter to each substitutliste
        substitutliste.assigned_substitutter = [
            {
                'name': assignment.user.get_full_name() or assignment.user.username,
                'phone': assignment.user.phone_number,
                'note': assignment.user.custom_note,
                'email': assignment.user.email,
                'id': assignment.user.id,
                'status': assignment.status  # Add this line to include the status
            }
            for assignment in getattr(substitutliste, 'assignments', [])
        ]

    context = {
        'substitutlister': substitutlister,
        'afmeldingslister': afmeldingslister,
        'weeks': weeks,
        'welcome_text': welcome_text,
        'assignments_by_substitutliste': assignments_by_substitutliste,
        'days': Day.objects.all(),
    }

    return render(request, 'front_page.html', context)

def select_substitut(request):
    if request.method == 'POST':
        list_id = request.POST.get('list_id')
        substitut_id = request.POST.get('substitut_id')
        selected_week = request.POST.get('selected_week')
        selected_day = request.POST.get('selected_day')
        
        try:
            assignment = UserSubstitutAssignment.objects.get(
                substitutliste_id=list_id,
                user_id=substitut_id
            )
            assignment.status = 'Taken'
            assignment.save()
            
            messages.success(request, 'Substitut er blevet valgt.')
        except UserSubstitutAssignment.DoesNotExist:
            messages.error(request, 'Der opstod en fejl ved valg af substitut.')
        
        # Construct the redirect URL with query parameters
        base_url = reverse('front_page')
        redirect_url = f'{base_url}?week={selected_week}&day={selected_day}'
        return redirect(redirect_url)
    
    return redirect('front_page')

def login(request):
    # Logic for handling login functionality
    return render(request, 'login.html')

def afmeldingsliste_detail(request, afmeldingsliste_id):
    afmeldingsliste = get_object_or_404(Afmeldingsliste, id=afmeldingsliste_id)
    return render(request, 'afmeldingsliste_detail.html', {'afmeldingsliste': afmeldingsliste})
