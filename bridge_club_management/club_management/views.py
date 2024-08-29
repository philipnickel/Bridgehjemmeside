# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .models import Configuration, Substitutliste, Afmeldingsliste, Week, DayResponsibility, UserSubstitutAssignment, Day
from django.contrib.auth.models import User
from django.utils.dateformat import DateFormat
import logging

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
    # Fetch the configuration for the welcome text
    configuration = Configuration.objects.first()
    welcome_text = configuration.welcome_text if configuration else ''
    
    # Retrieve all substitutlister, afmeldingslister, and weeks from the database
    substitutlister = Substitutliste.objects.all()
    afmeldingslister = Afmeldingsliste.objects.all()
    weeks = Week.objects.all()

    # Prepare the responsibility data
    responsibilities = DayResponsibility.objects.select_related('day', 'coordinator').all()
    responsibility_dict = {}
    print("DayResponsibility data:")
    for resp in responsibilities:
        print(f"Day: {resp.day.name}, Coordinator: {resp.coordinator.username} ({resp.coordinator.email})")
        responsibility_dict[resp.day.name.lower()] = resp.coordinator

    # Debugging output to check if responsibilities and coordinators are being retrieved correctly
    responsibility_list = []
    for res in responsibilities:
        coordinator_email = res.coordinator.email if res.coordinator else "ikke tildelt"
        responsibility_list.append((res.day.id, coordinator_email))
        print(f"Day: {res.day.name}, Coordinator: {coordinator_email}")

   
# Prepare assignments list
    assignments = UserSubstitutAssignment.objects.select_related('substitutliste', 'user')
    assignments_by_substitutliste = {}

    for substitutliste in substitutlister:
        assignments_by_substitutliste[substitutliste.id] = []
    
    for assignment in assignments:
        assignments_by_substitutliste[assignment.substitutliste.id].append(assignment)
    # Add the day of the week to each substitutliste
    for substitutliste in substitutlister:
        substitutliste.day_of_week = DateFormat(substitutliste.day).format('l')
        logger.debug(f"Substitutliste: id={substitutliste.id}, week={substitutliste.week.id}, day={substitutliste.day}, day_of_week={substitutliste.day_of_week}")

    # Prepare the responsibility data
    responsibilities = DayResponsibility.objects.select_related('day', 'coordinator').all()
    responsibility_dict = {resp.day.name: resp.coordinator for resp in responsibilities}

    # Add responsibility information to each substitutliste
    for substitutliste in substitutlister:
        substitutliste.day_of_week = DateFormat(substitutliste.day).format('l')
        day_name = substitutliste.day_of_week
        responsible_coordinator = responsibility_dict.get(day_name.lower())
        print(f"Substitutliste: Day={substitutliste.day}, Day of week={day_name}, Responsible={responsible_coordinator}")
        if responsible_coordinator:
            substitutliste.responsible_name = responsible_coordinator.get_full_name() or responsible_coordinator.username
            substitutliste.responsible_email = responsible_coordinator.email
        else:
            substitutliste.responsible_name = "Ikke tildelt"
            substitutliste.responsible_email = ""

    # Fetch all DayResponsibility objects
    day_responsibilities = DayResponsibility.objects.select_related('day', 'coordinator')
    
    # Create a dictionary mapping day names to coordinators
    responsibility_dict = {resp.day.name.lower(): resp.coordinator for resp in day_responsibilities}

    # Add responsibility information to each substitutliste
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

    # Pass the data to the template context
    context = {
        'substitutlister': substitutlister,
        'afmeldingslister': afmeldingslister,
        'weeks': weeks,
        'welcome_text': welcome_text,
        'responsibility_list': responsibility_list,

        'assignments_by_substitutliste': assignments_by_substitutliste,
        'days': Day.objects.all(),
    }

    return render(request, 'front_page.html', context)

def select_substitut(request):
    if request.method == 'POST':
        list_id = request.POST.get('list_id')
        email = request.POST.get('email')

        # Fetch the Substitutliste object
        substitutliste = Substitutliste.objects.get(id=list_id)
        
        # Update the user assignment status
        UserSubstitutAssignment.objects.filter(substitutliste=substitutliste, user__email=email).update(status='Taken')

        # Get the responsible person email
        responsible_person_email = substitutliste.responsible_person.email  # Adjust based on your actual model

        # Send an email notification to the responsible person
        send_mail(
            subject=f'Substitut valgt for {substitutliste.day}',
            message=f'Substitut for {substitutliste.day} er blevet valgt. Kontaktperson: {email}.',
            from_email='no-reply@example.com',
            recipient_list=[responsible_person_email],  # Assumes there is a field for email
            fail_silently=False,
        )

        # Redirect back to the front page or wherever appropriate
        return redirect('front_page')

    # If not POST, redirect back
    return redirect('front_page')

def login(request):
    # Logic for handling login functionality
    return render(request, 'login.html')
