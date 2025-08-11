from django.test import TestCase
from django.utils import timezone
from club_management.models import (
    CustomUser, Række, Configuration, Tilmeldingsliste,
    TilmeldingslistePair
)

class WaitingListTests(TestCase):
    def setUp(self):
        self.række = Række.objects.create(name="Test-række")
        self.config = Configuration.objects.create(
            name="Test Configuration",
            welcome_text="Welcome"
        )
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
            user_type="Substitutter",
            phone_number="+45 87654321"
        )
        
        # Create a Tilmeldingsliste with capacity for 3 pairs
        self.test_date = timezone.now()
        self.tilmeldingsliste = Tilmeldingsliste.objects.create(
            name="Test Signup",
            day=self.test_date,
            deadline=self.test_date,
            responsible_person=self.admin_user,
            antal_par=3  # Small capacity to test edge cases
        )

    def test_capacity_increase_moves_pairs(self):
        """Test that increasing list capacity moves pairs from waiting list."""
        # Add 4 pairs (1 should go to waiting list)
        pairs = []
        for i in range(4):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Verify initial state
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 3)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 1)
        self.assertTrue(pairs[3].på_venteliste)  # Last pair should be on waiting list
        
        # Increase capacity
        self.tilmeldingsliste.antal_par = 4
        self.tilmeldingsliste.save()
        
        # Verify pair moved from waiting list
        pairs[3].refresh_from_db()
        self.assertFalse(pairs[3].på_venteliste)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 4)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 0)

    def test_capacity_decrease_moves_pairs_to_waiting(self):
        """Test that decreasing list capacity moves pairs to waiting list."""
        # Add 3 pairs (fills capacity)
        pairs = []
        for i in range(3):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Verify initial state
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 3)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 0)
        
        # Decrease capacity
        self.tilmeldingsliste.antal_par = 2
        self.tilmeldingsliste.save()
        
        # Verify last pair moved to waiting list
        pairs[2].refresh_from_db()
        self.assertTrue(pairs[2].på_venteliste)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 2)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 1)

    def test_pair_deletion_moves_from_waiting(self):
        """Test that deleting a pair moves another from waiting list."""
        # Add 4 pairs (1 should go to waiting list)
        pairs = []
        for i in range(4):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Verify initial state
        self.assertTrue(pairs[3].på_venteliste)
        
        # Delete a pair from main list
        pairs[0].delete()
        
        # Verify waiting list pair moved up
        pairs[3].refresh_from_db()
        self.assertFalse(pairs[3].på_venteliste)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 3)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 0)

    def test_single_players_always_on_waiting(self):
        """Test that single players are always on waiting list."""
        # Add 2 regular pairs
        for i in range(2):
            TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
        
        # Add single player (plenty of capacity left)
        single = TilmeldingslistePair.objects.create(
            tilmeldingsliste=self.tilmeldingsliste,
            navn='Single Player',
            telefonnummer='+45 11223344',
            email='single@test.com',
            is_single=True
        )
        
        # Verify single player on waiting list despite available capacity
        self.assertTrue(single.på_venteliste)
        self.assertEqual(single.parnummer, 3)  # Should be after regular pairs

    def test_pair_numbers_maintained(self):
        """Test that pair numbers are maintained correctly."""
        # Add 5 pairs (2 should go to waiting list)
        pairs = []
        for i in range(5):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Verify initial pair numbers
        for i, pair in enumerate(pairs, start=1):
            pair.refresh_from_db()
            self.assertEqual(pair.parnummer, i)
        
        # Delete pair 2
        pairs[1].delete()
        
        # Verify pair numbers were updated
        for i, pair in enumerate(pairs[2:], start=2):
            pair.refresh_from_db()
            self.assertEqual(pair.parnummer, i)

    def test_multiple_single_players(self):
        """Test handling of multiple single players."""
        # Add 2 regular pairs
        for i in range(2):
            TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
        
        # Add 3 single players
        singles = []
        for i in range(3):
            single = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Single {i}',
                telefonnummer='+45 11223344',
                email=f'single{i}@test.com',
                is_single=True
            )
            singles.append(single)
        
        # Verify all singles on waiting list with correct numbers
        for i, single in enumerate(singles):
            single.refresh_from_db()
            self.assertTrue(single.på_venteliste)
            self.assertEqual(single.parnummer, 3 + i)  # Should start after regular pairs

    def test_zero_capacity_all_waiting(self):
        """Test that zero capacity puts all pairs on waiting list."""
        # Set capacity to 0
        self.tilmeldingsliste.antal_par = 0
        self.tilmeldingsliste.save()
        
        # Add 3 pairs
        pairs = []
        for i in range(3):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Verify all pairs on waiting list
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 3)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 0) 

    def test_negative_capacity_all_waiting(self):
        """Test that negative capacity puts all pairs on waiting list."""
        # Set capacity to -1
        self.tilmeldingsliste.antal_par = -1
        self.tilmeldingsliste.save()
        
        # Add 3 pairs
        pairs = []
        for i in range(3):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Verify all pairs on waiting list
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 3)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 0)

    def test_rapid_capacity_changes(self):
        """Test rapid changes to capacity."""
        # Add 5 pairs
        pairs = []
        for i in range(5):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Initial state: 3 main list, 2 waiting
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 3)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 2)
        
        # Rapid changes: 3 -> 1 -> 5 -> 2
        self.tilmeldingsliste.antal_par = 1
        self.tilmeldingsliste.save()
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 1)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 4)
        
        self.tilmeldingsliste.antal_par = 5
        self.tilmeldingsliste.save()
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 5)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 0)
        
        self.tilmeldingsliste.antal_par = 2
        self.tilmeldingsliste.save()
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 2)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 3)

    def test_mixed_singles_and_pairs(self):
        """Test mixed singles and pairs with capacity changes."""
        # Add 2 pairs and 2 singles
        pairs = []
        singles = []
        
        # Add pairs
        for i in range(2):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Add singles
        for i in range(2):
            single = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Single {i}',
                telefonnummer='+45 11223344',
                email=f'single{i}@test.com',
                is_single=True
            )
            singles.append(single)
        
        # Initial state: 2 pairs on main list, 2 singles on waiting
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False, is_single=False).count(), 2)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True, is_single=True).count(), 2)
        
        # Increase capacity - singles should stay on waiting list
        self.tilmeldingsliste.antal_par = 5
        self.tilmeldingsliste.save()
        
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False, is_single=False).count(), 2)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True, is_single=True).count(), 2)
        
        # Decrease capacity - some pairs should move to waiting list
        self.tilmeldingsliste.antal_par = 1
        self.tilmeldingsliste.save()
        
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False, is_single=False).count(), 1)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 3)  # 1 pair + 2 singles

    def test_concurrent_updates(self):
        """Test that concurrent updates maintain consistency."""
        from django.db import transaction
        
        # Add 4 pairs
        pairs = []
        for i in range(4):
            pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn=f'Player {i}a',
                makker=f'Player {i}b',
                telefonnummer='+45 11223344',
                email=f'player{i}@test.com',
                is_single=False
            )
            pairs.append(pair)
        
        # Initial state: 3 main list, 1 waiting
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 3)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 1)
        
        # Simulate concurrent updates in a transaction
        with transaction.atomic():
            # Update capacity
            self.tilmeldingsliste.antal_par = 2
            self.tilmeldingsliste.save()
            
            # Add a new pair
            new_pair = TilmeldingslistePair.objects.create(
                tilmeldingsliste=self.tilmeldingsliste,
                navn='New Player A',
                makker='New Player B',
                telefonnummer='+45 11223344',
                email='new@test.com',
                is_single=False
            )
        
        # Verify final state: 2 main list, 3 waiting
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=False).count(), 2)
        self.assertEqual(TilmeldingslistePair.objects.filter(på_venteliste=True).count(), 3) 