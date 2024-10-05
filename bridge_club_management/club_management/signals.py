from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TilmeldingslistePair, Tilmeldingsliste

@receiver(post_save, sender=TilmeldingslistePair)
def manage_waiting_list(sender, instance, created, **kwargs):
    if created:
        tilmeldingsliste = instance.tilmeldingsliste
        # Initially set the new pair to be on the waiting list
        instance.på_venteliste = True
        instance.save()

        # Get all pairs ordered by their creation time
        pairs = TilmeldingslistePair.objects.filter(tilmeldingsliste=tilmeldingsliste).order_by('id')
        # Count pairs not on the waiting list
        non_waiting_pairs = pairs.filter(på_venteliste=False).count()

        # Calculate available slots on the main list
        available_slots = tilmeldingsliste.antal_par - non_waiting_pairs

        # If there are at least two slots available, move pairs from the waiting list
        if available_slots >= 2:
            waiting_pairs = pairs.filter(på_venteliste=True).order_by('id')[:2]
            if len(waiting_pairs) == 2:  # Ensure we have two pairs to move
                for pair in waiting_pairs:
                    pair.på_venteliste = False
                    pair.save()

        # Reassign parnummer
        for i, pair in enumerate(pairs, start=1):
            pair.parnummer = i
            pair.save()

@receiver(post_delete, sender=TilmeldingslistePair)
def update_parnummer_on_delete(sender, instance, **kwargs):
    tilmeldingsliste = instance.tilmeldingsliste
    # Reorder pairs after deletion
    pairs = TilmeldingslistePair.objects.filter(tilmeldingsliste=tilmeldingsliste).order_by('id')
    non_waiting_pairs = pairs.filter(på_venteliste=False).count()

    # Check if the number of non-waiting pairs is odd
    if non_waiting_pairs % 2 != 0:
        # Move the newest added pair to the waiting list
        newest_pair = pairs.filter(på_venteliste=False).order_by('-id').first()
        if newest_pair:
            newest_pair.på_venteliste = True
            newest_pair.save()

    # Reassign parnummer
    for i, pair in enumerate(pairs, start=1):
        pair.parnummer = i
        pair.save()
