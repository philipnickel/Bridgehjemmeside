# Brugervejledning
## Nye Substitutliste-ledere
Skal oprettes i admin-delen af hjemmesiden under 'Godkendelse og Autorisation'. 
(husk at tildele dem rettigheder)

## Oprettelse af Substitutter
Sker i admin-delen af hjemmesiden under 'Substitutter' -> 'Tilføj Substitutter'.
Obs: De bliver ikke automatisk sat på allerede eksisterende substitutlister. (Hvis dette ønskes, skal substitutlisterne opdateres) - Kan gøre hurtigt fra 'Substitutlister'->Markér alle -> Handling -> opdatér valgte -> Udfør 

## Oprettelse af Substitutlister og uger
Der bliver lavet et automatisk 'tjek' hver aften, hvor det sikres, at kun den aktuelle uge vises og alle uger har tilhørende substitutlister.

## Ansvarlig for substitutliste
Vælges i admin-delen af hjemmesiden under 'Ansvarlig for dag' 

## Forsidetekst
Ændres i admin-delen af hjemmesiden under 'Forsidetekst'. 

## Automatiske Emails
Der sendes automatisk en email til den ansvarlige, når en substitut vælges. 

## Afmeldingslister 
Skal oprettes manuelt i admin-delen af hjemmesiden under 'Afmeldingslister'. 





# Documentation 

This repository contains the source code for managing a bridge club, including various Django models, forms, views, and templates.

## Table of Contents

1. [Models](#models)
2. [Forms](#forms)
3. [Admin](#admin)
4. [URLs](#urls)
5. [Views](#views)
6. [Commands](#commands)
7. [Templates](#templates)
8. [Tech Stack](#tech-stack)

## Models

The `models.py` file contains the database models for the application. These models define the structure of the database tables and the relationships between them.

## Forms

The `forms.py` file contains the Django forms used in the application. These forms handle user input and validation.

## Admin

The `admin.py` file is used to register the models with the Django admin site. This allows for easy management of the models through the Django admin interface.

## URLs

The `urls.py` file contains the URL patterns for the application. These patterns map URLs to views.

## Views

The `views.py` file contains the view functions or class-based views that handle the requests and return responses.

## Commands

The `commands` directory contains custom management commands for the Django application. These commands can be run using the Django `manage.py` script.

## Templates

The `templates` directory contains the HTML templates used in the application. These templates are rendered by the views and returned as HTML responses.

## Tech Stack

- **Python**: The main programming language used.
- **Django**: The web framework used for building the application.
- **CKEditor 4**: A web-based text editor used for rich text editing.
- **JavaScript**: Used for client-side scripting.
- **HTML/CSS**: Used for structuring and styling the web pages.
- **Tailwind CSS**: A utility-first CSS framework used for styling.
- **SQLite**: The database used. Only exists on server. 
- **Bootstrap**: A CSS framework used for responsive design.

## Questions 
Can be directed to Philip at Philipnickel@outlook.dk 
