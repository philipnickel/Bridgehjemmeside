from django.shortcuts import render
from .models import Configuration, Substitutliste, Afmeldingsliste

def front_page(request):
    # Logic to fetch data for the front page
    configuration = Configuration.objects.first()  # Assuming there's only one configuration object
    welcome_text = configuration.welcome_text if configuration else ''  # Get the welcome text or an empty string if no configuration exists
    
    # Retrieve substitutlister data from the database
    substitutlister = Substitutliste.objects.all()
    
    # Retrieve afmeldingslister data from the database
    afmeldingslister = Afmeldingsliste.objects.all()
    
    # Pass the substitutlister and afmeldingslister data along with welcome text to the template context
    context = {
        'substitutlister': substitutlister,
        'afmeldingslister': afmeldingslister,
        'welcome_text': welcome_text
    }

    return render(request, 'front_page.html', context)

def login(request):
    # Logic for handling login functionality
    return render(request, 'login.html')
