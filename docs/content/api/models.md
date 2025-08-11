# Models API Reference

Django models defining the database structure for the bridge club management system.

## Core Models

The following models handle the main data structures:

### User Management
- **CustomUser** - Extended user model with bridge club specific fields like phone, availability
- **UserSubstitutAssignment** - Tracks substitute assignments and user availability status

### Bridge Club Structure  
- **Day** - Represents days of the week with localized names
- **Week** - Manages weekly schedules and planning
- **DayResponsibility** - Assigns coordinators to specific days
- **Række** - Row/group assignments for organizing players

### List Management
- **Afmeldingsliste** - Absence/cancellation lists for tracking who can't attend
- **Substitutliste** - Substitute lists for managing replacement players
- **Tilmeldingsliste** - Registration lists for bridge sessions
- **Configuration** - System configuration and settings

*Note: Full API documentation with field details and relationships will be added once Django environment is properly configured for docs generation.*

## Database Schema

The models work together to provide:

- User registration and profile management
- Weekly schedule planning and coordination
- Substitute assignment and availability tracking
- Administrative configuration options

## Key Relationships

- Users can be assigned to multiple substitute lists
- Days have responsible coordinators and associated lists
- Weeks contain multiple days with their own management needs
- Configuration settings control system behavior

## Usage Examples

!!! example "Creating a new user"
    
    ```python
    from club_management.models import CustomUser, Day
    
    # Create a substitute user
    user = CustomUser.objects.create_user(
        username='john_doe',
        user_type='Substitutter',
        phone_number='+45 12 34 56 78',
        email='john@example.com'
    )
    
    # Set availability
    monday = Day.objects.get(name='Monday')
    user.days_available.add(monday)
    ```

!!! example "Working with substitute lists"
    
    ```python
    from club_management.models import Substitutliste, UserSubstitutAssignment
    
    # Get current week's substitute list for Monday
    monday = Day.objects.get(name='Monday')
    sub_list = monday.get_current_week_substitute_list()
    
    # Get available substitutes
    available = sub_list.get_available_substitutes()
    
    # Mark someone as chosen
    assignment = UserSubstitutAssignment.objects.get(
        user=user, substitutliste=sub_list
    )
    assignment.mark_as_chosen("Confirmed for bridge session")
    ```

## Waiting List Behavior

The system implements a waiting list for `Tilmeldingsliste` (signup lists) with the following rules:

### Regular Pairs
- First N pairs (where N is `antal_par`) are placed on the main list
- Additional pairs are placed on the waiting list (`på_venteliste = True`)
- Pairs are ordered by their signup time (first come, first served)
- Each pair gets a unique number (`parnummer`) regardless of waiting list status

### Single Players
- Single players (`is_single = True`) are always placed on the waiting list
- Single players get numbers after all regular pairs
- Single players can be matched with other single players by administrators

### Capacity Changes
- When capacity increases:
  - Pairs move from waiting list to main list in order
  - Single players remain on waiting list
- When capacity decreases:
  - Excess pairs move to waiting list (last in, first out)
  - Pair numbers are maintained

### Automatic Updates
The waiting list is automatically managed in these scenarios:
1. New pair signs up
2. Pair is deleted
3. List capacity changes
4. Single player signs up
5. Single players are matched into a pair

### Edge Cases
- Zero or negative capacity: All pairs go to waiting list
- Concurrent updates: Handled via database transactions
- Pair deletion: Next pair on waiting list moves to main list
- Rapid capacity changes: Processed in order, maintaining consistency

## Model Reference

::: club_management.models.Tilmeldingsliste
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.TilmeldingslistePair
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.CustomUser
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.Række
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.Day
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.Week
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.Configuration
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.UnavailableDay
    options:
      show_root_heading: true
      show_source: false

::: club_management.models.DayResponsibility
    options:
      show_root_heading: true
      show_source: false