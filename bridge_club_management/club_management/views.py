
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .models import Configuration, Substitutliste, Afmeldingsliste, Week, DayResponsibility, UserSubstitutAssignment
from django.contrib.auth.models import User



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
    responsibilities = DayResponsibility.objects.all()

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
    # Pass the data to the template context
    context = {
        'substitutlister': substitutlister,
        'afmeldingslister': afmeldingslister,
        'weeks': weeks,
        'welcome_text': welcome_text,
        'responsibility_list': responsibility_list,

        'assignments_by_substitutliste': assignments_by_substitutliste
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
