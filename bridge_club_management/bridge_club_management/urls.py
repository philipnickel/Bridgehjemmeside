"""bridge_club_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from club_management import views
try:
    from wagtail.admin import urls as wagtailadmin_urls
    from wagtail.documents import urls as wagtaildocs_urls
    _WAGTAIL_AVAILABLE = True
except ImportError:  # Wagtail not installed yet
    _WAGTAIL_AVAILABLE = False
if _WAGTAIL_AVAILABLE:
    from wagtail import urls as wagtail_urls

if getattr(settings, 'ADMIN_UI', 'django') == 'wagtail' and _WAGTAIL_AVAILABLE:
    admin_mount = path('admin/', include(wagtailadmin_urls))
else:
    admin_mount = path('admin/', admin.site.urls)

admin_urls = admin.site.urls

urlpatterns = [
    admin_mount,
    # Alternates for clarity/switching
    path('djadmin/', include((admin_urls[0], admin_urls[1]), namespace='djadmin')),
    *( [path('wadmin/', include(wagtailadmin_urls)), path('documents/', include(wagtaildocs_urls)), path('pages/', include(wagtail_urls))] if _WAGTAIL_AVAILABLE else [] ),

    # Public site
    path('', include('club_management.urls')),
    path('select_substitut/', views.select_substitut, name='select_substitut'),
    path('login/', views.login, name='login'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('append-afbud/<int:afmeldingsliste_id>/', views.append_afbud, name='append_afbud'),
    path('afmeldingsliste/<int:afmeldingsliste_id>/', views.afmeldingsliste_detail, name='afmeldingsliste_detail'),
    path('meld_afbud/', views.meld_afbud, name='meld_afbud'),
    path('Tilmeldingsliste/', views.Tilmeldingsliste, name='Tilmeldingslister'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add debug toolbar URLs for local development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
