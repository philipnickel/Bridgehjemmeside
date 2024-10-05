from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TilmeldingslistePair, Tilmeldingsliste

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

            # Refresh the instance to ensure it has the latest data
            instance.refresh_from_db()
    finally:
        delattr(instance, '_managing_waiting_list')

@receiver(post_delete, sender=TilmeldingslistePair)
def update_on_delete(sender, instance, **kwargs):
    move_pairs_from_waiting_list(instance.tilmeldingsliste)

def move_pairs_from_waiting_list(tilmeldingsliste):
    with transaction.atomic():
        pairs = TilmeldingslistePair.objects.filter(tilmeldingsliste=tilmeldingsliste, is_single=False).order_by('id')
        main_list_capacity = tilmeldingsliste.antal_par
        main_list_count = pairs.filter(på_venteliste=False).count()
        
        if main_list_count < main_list_capacity and main_list_count % 2 == 0:
            pairs_to_move = min(2, main_list_capacity - main_list_count)
            waiting_pairs = pairs.filter(på_venteliste=True)[:pairs_to_move]
            
            for pair in waiting_pairs:
                pair.på_venteliste = False
            
            TilmeldingslistePair.objects.bulk_update(waiting_pairs, ['på_venteliste'])
    
    # Trigger the manage_waiting_list signal to update parnummer and statistics
    if pairs.exists():
        pairs.first().save()