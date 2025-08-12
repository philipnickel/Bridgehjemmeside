from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TilmeldingslistePair, Tilmeldingsliste
from .email_utils import send_tilmeldingsliste_email

@receiver(post_save, sender=TilmeldingslistePair)
def manage_waiting_list(sender, instance, created, **kwargs):
    if hasattr(instance, '_managing_waiting_list'):
        return
    
    instance._managing_waiting_list = True
    try:
        with transaction.atomic():
            tilmeldingsliste = instance.tilmeldingsliste
            pairs = TilmeldingslistePair.objects.filter(tilmeldingsliste=tilmeldingsliste, is_single=False).order_by('id')
            
            main_list_capacity = tilmeldingsliste.antal_par
            total_pairs = pairs.count()
            
            previous_states = {p.id: (p.på_venteliste, p.parnummer) for p in pairs}

            pairs_to_update = []
            for i, pair in enumerate(pairs, start=1):
                if i <= main_list_capacity and (i < total_pairs or total_pairs % 2 == 0):
                    pair.på_venteliste = False
                    pair.parnummer = i
                else:
                    pair.på_venteliste = True
                    pair.parnummer = i
                pairs_to_update.append(pair)
            
            TilmeldingslistePair.objects.bulk_update(pairs_to_update, ['på_venteliste', 'parnummer'])
            
            # Handle single players
            single_players = TilmeldingslistePair.objects.filter(tilmeldingsliste=tilmeldingsliste, is_single=True).order_by('id')
            for i, player in enumerate(single_players):
                player.på_venteliste = True
                player.parnummer = total_pairs + i + 1
            TilmeldingslistePair.objects.bulk_update(single_players, ['på_venteliste', 'parnummer'])
            
            # Update Tilmeldingsliste statistics
            tilmeldingsliste.antal_par_på_venteliste = max(0, total_pairs - main_list_capacity)
            if total_pairs % 2 != 0:
                tilmeldingsliste.antal_par_på_venteliste += 1
            tilmeldingsliste.antal_enkelte_spillere = single_players.count()
            tilmeldingsliste.save()

            # Notify pairs who moved off the waiting list
            moved_off_wait = [
                pair for pair in pairs_to_update
                if previous_states.get(pair.id, (True, None))[0] and not pair.på_venteliste
            ]
            # Notify pairs who moved onto waiting list due to capacity decrease
            moved_to_wait = [
                pair for pair in pairs_to_update
                if not previous_states.get(pair.id, (False, None))[0] and pair.på_venteliste
            ]
            for pair in moved_off_wait:
                subject = f"Opdatering for {tilmeldingsliste.name}"
                message = (
                    f"Hej {pair.navn}{f' og {pair.makker}' if pair.makker else ''},\n\n"
                    f"I er nu flyttet fra ventelisten til hovedlisten for {tilmeldingsliste.name} den {tilmeldingsliste.day}.\n"
                    f"Jeres parnummer er {pair.parnummer}."
                )
                recipients = [addr for addr in [pair.email] if addr]
                if recipients:
                    send_tilmeldingsliste_email(subject, message, recipients)
            for pair in moved_to_wait:
                subject = f"Opdatering for {tilmeldingsliste.name}"
                message = (
                    f"Hej {pair.navn}{f' og {pair.makker}' if pair.makker else ''},\n\n"
                    f"På grund af en ændring i kapacitet er I flyttet til ventelisten for {tilmeldingsliste.name} den {tilmeldingsliste.day}.\n"
                    f"Jeres parnummer er {pair.parnummer}."
                )
                recipients = [addr for addr in [pair.email] if addr]
                if recipients:
                    send_tilmeldingsliste_email(subject, message, recipients)
    finally:
        delattr(instance, '_managing_waiting_list')

@receiver(post_delete, sender=TilmeldingslistePair)
def update_on_delete(sender, instance, **kwargs):
    move_pairs_from_waiting_list(instance.tilmeldingsliste)
    # Notify that a pair was removed
    subject = f"Opdatering for {instance.tilmeldingsliste.name}"
    message = (
        f"Hej,\n\nEt par er blevet fjernet fra {instance.tilmeldingsliste.name} den {instance.tilmeldingsliste.day}.\n"
        f"Hvis du står på ventelisten, kan du være rykket frem."
    )
    # No direct recipients known here; skip or add admin notification if needed.
    pass


def move_pairs_from_waiting_list(tilmeldingsliste):
    with transaction.atomic():
        pairs = TilmeldingslistePair.objects.filter(tilmeldingsliste=tilmeldingsliste, is_single=False).order_by('id')
        main_list_capacity = tilmeldingsliste.antal_par
        main_list_count = pairs.filter(på_venteliste=False).count()
        
        notified_pairs = []
        if main_list_count < main_list_capacity and main_list_count % 2 == 0:
            pairs_to_move = min(2, main_list_capacity - main_list_count)
            waiting_pairs = list(pairs.filter(på_venteliste=True)[:pairs_to_move])
            
            for pair in waiting_pairs:
                pair.på_venteliste = False
            
            TilmeldingslistePair.objects.bulk_update(waiting_pairs, ['på_venteliste'])
            notified_pairs = waiting_pairs
    
    # Trigger the manage_waiting_list signal to update parnummer and statistics
    if pairs.exists():
        pairs.first().save()
    
    # Send notifications after parnummer update
    for pair in notified_pairs:
        refreshed = TilmeldingslistePair.objects.get(id=pair.id)
        subject = f"Opdatering for {tilmeldingsliste.name}"
        message = (
            f"Hej {refreshed.navn}{f' og {refreshed.makker}' if refreshed.makker else ''},\n\n"
            f"I er nu flyttet fra ventelisten til hovedlisten for {tilmeldingsliste.name} den {tilmeldingsliste.day}.\n"
            f"Jeres parnummer er {refreshed.parnummer}."
        )
        recipients = [addr for addr in [refreshed.email] if addr]
        if recipients:
            send_tilmeldingsliste_email(subject, message, recipients)