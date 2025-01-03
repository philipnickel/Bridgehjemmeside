# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .models import (Configuration, Substitutliste, Afmeldingsliste, Week, 
                     DayResponsibility, UserSubstitutAssignment, Day, CustomUser, 
                     Tilmeldingsliste, Pair, TilmeldingslistePair)
from django.contrib.auth.models import User
from django.utils.dateformat import DateFormat
import logging
from django.db.models import Prefetch
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, fields
from django.db import transaction
from django.db.models import Q
from django.db.models import Min

logger = logging.getLogger(__name__)

@require_POST
def append_afbud(request, afmeldingsliste_id):
    try:
        afmeldingsliste = get_object_or_404(Afmeldingsliste, id=afmeldingsliste_id)
        afbud_name = request.POST.get('afbud_name', '').strip()

        if afbud_name:
            current_afbud = afmeldingsliste.afbud or ''
            afbud_list = [name.strip() for name in current_afbud.replace('Afbud:', '').split(',') if name.strip()]
            
            # Check if the name is already in the list (case-insensitive)
            if afbud_name.lower() not in [name.lower() for name in afbud_list]:
                afbud_list.append(afbud_name)
                
                # Join the list back into a string, adding 'Afbud:' at the beginning
                afmeldingsliste.afbud = 'Afbud: ' + ', '.join(afbud_list)
                afmeldingsliste.save()
                
                return JsonResponse({'success': True, 'updated_afbud': afmeldingsliste.afbud})
            else:
                return JsonResponse({'success': False, 'error': 'Dette navn er allerede registreret.'})
        else:
            return JsonResponse({'success': False, 'error': 'Navnet kan ikke være tomt.'})
    except Exception as e:
        print(f"Error in append_afbud: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

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
    afmeldingslister = Afmeldingsliste.objects.all().order_by('day')
    weeks = Week.objects.all()
    weeks = sorted(weeks, key=lambda week: int(week.name.split('-')[0]))  # Sort weeks by week number

    # Mapping of English day names to Danish day names
    day_name_mapping = {
        'Monday': 'Mandag',
        'Tuesday': 'Tirsdag',
        'Wednesday': 'Onsdag',
        'Thursday': 'Torsdag',
        'Friday': 'Fredag',
        'Saturday': 'Lørdag',
        'Sunday': 'Søndag'
    }

    responsibilities = DayResponsibility.objects.select_related('day', 'coordinator').all()
    responsibility_dict = {resp.day.name.lower(): resp.coordinator for resp in responsibilities}

    for substitutliste in substitutlister:
        substitutliste.day_of_week = substitutliste.day.strftime("%A")
        day_name = substitutliste.day.strftime("%A")
        day = Day.objects.get(name=day_name)
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
                'status': assignment.get_status_display(),  # This will use the Danish display name
                'reservationsnote': assignment.reservationsnote,
                'række': assignment.user.række.name if assignment.user.række else 'N/A'  # Add this line
            }
            for assignment in substitutliste.assignments
        ]

    context = {
        'substitutlister': substitutlister,
        'afmeldingslister': afmeldingslister,
        'weeks': weeks,
        'welcome_text': welcome_text,
        'days': Day.objects.all(),
        'day_name_mapping': day_name_mapping,  # Pass the mapping to the template
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
            assignment.status = 'Optaget'
            assignment.reservationsnote = f"Navn: {name}, Email: {email}, Telefon: {phone}"
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

def meld_afbud(request):
    if request.method == 'POST':
        list_id = request.POST.get('list_id')
        substitut_id = request.POST.get('substitut_id')
        responsible_email = request.POST.get('responsible_email')
        
        try:
            assignment = UserSubstitutAssignment.objects.get(
                substitutliste_id=list_id,
                user_id=substitut_id
            )
            assignment.status = 'Fraværende'
            assignment.save()
            
            substitutliste = get_object_or_404(Substitutliste, id=list_id)
            substitut = get_object_or_404(CustomUser, id=substitut_id)
            
            substitut_name = substitut.get_full_name() or substitut.username
            
            # Send email to responsible person
            subject = 'Substitut har meldt afbud'
            message = f"""
            Substitut {substitut_name} har meldt afbud for listen {substitutliste.name} ({substitutliste.day}).
            """
            send_mail(subject, message, 'from@example.com', [responsible_email])
            
            return JsonResponse({'success': True})
        except UserSubstitutAssignment.DoesNotExist:
            logger.error(f"UserSubstitutAssignment not found for list_id={list_id}, substitut_id={substitut_id}")
            return JsonResponse({'success': False, 'error': 'Substitut assignment not found.'})
        except Exception as e:
            logger.error(f"Unexpected error in meld_afbud: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

def login(request):
    # Logic for handling login functionality
    return render(request, 'login.html')

def afmeldingsliste_detail(request, afmeldingsliste_id):
    afmeldingsliste = get_object_or_404(Afmeldingsliste, id=afmeldingsliste_id)
    return render(request, 'afmeldingsliste_detail.html', {'afmeldingsliste': afmeldingsliste})

def substitutlister(request):
    configuration = Configuration.objects.first()
    substitutlister_text = configuration.substitutlister_text if configuration else ''
    
    substitutlister = Substitutliste.objects.prefetch_related(
        Prefetch(
            'usersubstitutassignment_set',
            queryset=UserSubstitutAssignment.objects.select_related('user'),
            to_attr='assignments'
        )
    ).all()
    weeks = Week.objects.all()
    weeks = sorted(weeks, key=lambda week: int(week.name.split('-')[0]))  # Sort weeks by week number

    # Mapping of English day names to Danish day names
    day_name_mapping = {
        'Monday': 'Mandag',
        'Tuesday': 'Tirsdag',
        'Wednesday': 'Onsdag',
        'Thursday': 'Torsdag',
        'Friday': 'Fredag',
        'Saturday': 'Lørdag',
        'Sunday': 'Søndag'
    }

    responsibilities = DayResponsibility.objects.select_related('day', 'coordinator').all()
    responsibility_dict = {resp.day.name.lower(): resp.coordinator for resp in responsibilities}

    for substitutliste in substitutlister:
        substitutliste.day_of_week = substitutliste.day.strftime("%A")
        day_name = substitutliste.day.strftime("%A")
        day = Day.objects.get(name=day_name)
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
                'status': assignment.get_status_display(),  # This will use the Danish display name
                'reservationsnote': assignment.reservationsnote,
                'række': assignment.user.række.name if assignment.user.række else 'N/A'
            }
            for assignment in substitutliste.assignments
        ]
    context = {
        'substitutlister': substitutlister,
        'weeks': weeks,
        'substitutlister_text': substitutlister_text,
        'days': Day.objects.all(),
        'day_name_mapping': day_name_mapping,
    }

    return render(request, 'substitutlister.html', context)

def afmeldingslister(request):
    afmeldingslister = Afmeldingsliste.objects.all()
    configuration = Configuration.objects.first()
    afmeldingslister_text = configuration.afmeldingslister_text if configuration else ''
    afmeldingslister_data = [
        {
            'id': str(liste.id),
            'name': liste.name,
            'day': liste.day.isoformat(),
            'deadline': liste.deadline.isoformat(),
            'afbud': liste.afbud or ''
        }
        for liste in afmeldingslister
    ]
    context = {
        'afmeldingslister': afmeldingslister,
        'afmeldingslister_json': json.dumps(afmeldingslister_data),
        'afmeldingslister_text': afmeldingslister_text,
    }
    return render(request, 'afmeldingslister.html', context)

def tilmeldingslister_view(request):
    tilmeldingslister = Tilmeldingsliste.objects.all().order_by('day')
    configuration = Configuration.objects.first()
    tilmeldingslister_text = configuration.tilmeldingslister_text if configuration else ''
    
    for liste in tilmeldingslister:
        liste.tilmeldte_par = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, på_venteliste=False, is_single=False).order_by('parnummer')
        liste.venteliste_par = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, på_venteliste=True, is_single=False).order_by('parnummer')
        liste.single_players = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, is_single=True).order_by('id')
        liste.all_pairs = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, is_single=False).order_by('parnummer')

    selected_list_id = request.GET.get('selected_list_id')
    if selected_list_id:
        selected_list = Tilmeldingsliste.objects.get(id=selected_list_id)
    else:
        # Select the oldest list based on the 'day' field
        oldest_date = Tilmeldingsliste.objects.aggregate(Min('day'))['day__min']
        selected_list = Tilmeldingsliste.objects.filter(day=oldest_date).first()

    if request.method == 'POST':
        list_id = request.POST.get('list_id')
        player1_name = request.POST.get('player1_name')
        player2_name = request.POST.get('player2_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        is_single = request.POST.get('is_single') == 'true'
        
        tilmeldingsliste = get_object_or_404(Tilmeldingsliste, id=list_id)

        # Check if players are already registered
        existing_players = TilmeldingslistePair.objects.filter(
            tilmeldingsliste=tilmeldingsliste
        ).filter(
            Q(navn__in=[player1_name, player2_name]) | Q(makker__in=[player1_name, player2_name])
        )

        if existing_players.exists():
            return JsonResponse({'success': False, 'error': 'En eller flere spillere er allerede tilmeldt.'})

        try:
            with transaction.atomic():
                if is_single:
                    other_single = TilmeldingslistePair.objects.filter(tilmeldingsliste=tilmeldingsliste, is_single=True).first()
                    
                    if other_single:
                        new_pair = TilmeldingslistePair.objects.create(
                            tilmeldingsliste=tilmeldingsliste,
                            navn=other_single.navn,
                            makker=player1_name,
                            telefonnummer=other_single.telefonnummer,
                            email=other_single.email,
                            is_single=False
                        )
                        other_single.delete()
                    else:
                        new_pair = TilmeldingslistePair.objects.create(
                            tilmeldingsliste=tilmeldingsliste,
                            navn=player1_name,
                            telefonnummer=phone_number,
                            email=email,
                            is_single=True
                        )
                else:
                    new_pair = TilmeldingslistePair.objects.create(
                        tilmeldingsliste=tilmeldingsliste,
                        navn=player1_name,
                        makker=player2_name,
                        telefonnummer=phone_number,
                        email=email,
                        is_single=False
                    )

                på_venteliste = new_pair.på_venteliste

                subject = f"Tilmelding til {tilmeldingsliste.name}"
                message = f"""
                Hej {player1_name}{f" og {player2_name}" if not is_single else ""},

                {"I" if not is_single else "Du"} er blevet tilmeldt til {tilmeldingsliste.name} den {tilmeldingsliste.day}.
                {"Du er blevet parret op med en anden spiller." if is_single and other_single else ""}
                {"I er på ventelisten." if på_venteliste else ""}

                Telefon: {phone_number}
                Email: {email}
                På venteliste: {'Ja' if på_venteliste else 'Nej'}
                """

                send_mail(subject, message, 'from@example.com', [email])

                return JsonResponse({
                    'success': True, 
                    'message': f"{'Par' if not is_single else 'Spiller'} er blevet tilmeldt{'og sat på venteliste' if på_venteliste else ''}."
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    context = {
        'tilmeldingslister': tilmeldingslister,
        'tilmeldingslister_text': tilmeldingslister_text,
        'selected_list': selected_list
    }
    return render(request, 'tilmeldingslister.html', context)