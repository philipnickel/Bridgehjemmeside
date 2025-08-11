# Management Commands API Reference

Custom Django management commands for automation and maintenance tasks.

## Command Overview

The Bridge Club Management System includes several custom management commands that handle automated tasks like creating substitute lists, updating day names, and ensuring data consistency.

All commands are located in `club_management/management/commands/` and can be run using:

```bash
python manage.py <command_name>
```

## Available Commands

The following management commands are available for automating bridge club operations:

- **create_days** - Creates missing day records for the bridge club schedule
- **ensure_substitutlister** - Ensures substitute lists exist for the current week
- **update_day_names** - Updates day names with proper localization
- **update_substitution_lists** - Refreshes substitute assignments and availability
- **update_weeks** - Creates upcoming week records for planning

*Note: Full API documentation for these commands will be added once Django environment is properly configured for docs generation.*

## Usage Examples

### Running Commands Manually

```bash
# Create missing day records
python manage.py create_days

# Ensure substitute lists exist for current week
python manage.py ensure_substitutlister

# Update day names with localization
python manage.py update_day_names

# Refresh substitute assignments
python manage.py update_substitution_lists

# Create upcoming week records
python manage.py update_weeks
```

### Automated Scheduling

These commands are designed to be run regularly via cron jobs:

```bash
# Example crontab entries

# Run daily at 2 AM - ensure substitute lists exist
0 2 * * * cd /path/to/project && python manage.py ensure_substitutlister

# Run weekly on Sunday at 1 AM - create upcoming weeks  
0 1 * * 0 cd /path/to/project && python manage.py update_weeks

# Run monthly on 1st at midnight - update day names
0 0 1 * * cd /path/to/project && python manage.py update_day_names
```

## Command Development

!!! example "Creating custom management commands"
    
    To create a new management command:
    
    1. Create a new file in `club_management/management/commands/`
    2. Inherit from `BaseCommand`
    3. Implement the `handle()` method
    
    ```python
    from django.core.management.base import BaseCommand
    
    class Command(BaseCommand):
        help = 'Description of what this command does'
        
        def add_arguments(self, parser):
            parser.add_argument(
                '--option',
                type=str,
                help='Optional argument',
            )
        
        def handle(self, *args, **options):
            self.stdout.write(
                self.style.SUCCESS('Command executed successfully')
            )
    ```

## Error Handling

All management commands include proper error handling and logging:

- Commands log their progress and results
- Failed operations are logged with details
- Commands are idempotent (safe to run multiple times)
- Database transactions ensure data consistency