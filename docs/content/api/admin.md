# Admin API Reference

Django admin interface configuration for managing bridge club data.

## Admin Classes

::: club_management.admin
    options:
        show_source: true
        heading_level: 2
        members_order: source

## Admin Features

The Django admin provides a web-based interface for managing bridge club data:

### Key Features

- **User Management**: Create and manage substitute users
- **Substitute Lists**: Bulk operations for updating assignments
- **Day Responsibilities**: Assign coordinators to specific days
- **List Management**: Create and manage absence/registration lists

### Accessing the Admin

1. Ensure you have a superuser account:
   ```bash
   python manage.py createsuperuser
   ```

2. Navigate to `/admin/` in your browser
3. Login with your superuser credentials

### Custom Admin Actions

The admin interface includes custom bulk actions for efficiency:

- **Update substitute assignments** - Bulk update user assignments
- **Mark as chosen/available** - Quick status changes
- **Export data** - Generate reports

!!! tip "Admin Best Practices"
    
    - Use bulk actions for efficiency when managing multiple records
    - Set up proper permissions for non-superuser staff
    - Use the search and filter options to quickly find specific records
    - Regular backups before making bulk changes

## Admin Permissions

Different user types have different admin access levels:

- **Superusers**: Full access to all admin features
- **Staff users**: Limited access based on assigned permissions
- **Coordinators**: May have specific permissions for their assigned days