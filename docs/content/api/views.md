# Views API Reference

Django views handle HTTP requests and return responses. This page documents all view functions and classes.

## Main Views

### Front Page View

::: club_management.views.front_page
    options:
        show_source: true
        heading_level: 3

### Substitute Lists View

::: club_management.views.substitutlister
    options:
        show_source: true
        heading_level: 3

### Absence Lists View

::: club_management.views.afmeldingslister
    options:
        show_source: true
        heading_level: 3

### Registration Lists View

::: club_management.views.tilmeldingslister_view
    options:
        show_source: true
        heading_level: 3

## URL Configuration

The views are mapped to URLs in `club_management/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.front_page, name='front_page'),
    path('substitutlister/', views.substitutlister, name='substitutlister'),
    path('afmeldingslister/', views.afmeldingslister, name='afmeldingslister'),
    path('tilmeldingslister/', views.tilmeldingslister_view, name='tilmeldingslister'),
]
```

## Template Integration

Each view renders specific templates:

- `front_page.html` - Homepage with current substitute information
- `substitutlister.html` - Interactive substitute list management
- `afmeldingslister.html` - Absence list display
- `tilmeldingslister.html` - Event registration interface