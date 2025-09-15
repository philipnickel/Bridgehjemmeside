from django.db import migrations

def seed_sitecopy(apps, schema_editor):
    try:
        Site = apps.get_model('wagtailcore', 'Site')
        SiteCopy = apps.get_model('club_management', 'SiteCopy')
    except LookupError:
        return

    site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
    if not site:
        return

    obj, created = SiteCopy.objects.get_or_create(site=site)

    defaults = {
        'site_title': 'Forside',
        'nav_substitutlister': 'Substitutlister',
        'nav_afmeldingslister': 'Afmeldingslister',
        'nav_tilmeldingslister': 'Tilmeldingslister',
        'nav_login': 'Login',

        'front_title': 'Velkommen!',
        'substitutlister_title': 'Substitutlister',
        'afmeldingslister_title': 'Afmeldingslister',
        'tilmeldingslister_title': 'Tilmeldingslister',

        'select_week_label': 'Vælg uge:',
        'select_day_label': 'Vælg dag:',
        'select_list_label': 'Vælg liste:',
        'responsible_label': 'Ansvarlig:',
        'deadline_label': 'Frist:',
        'day_label': 'Dag:',
        'time_label': 'Tidspunkt:',
        'capacity_label': 'Antal pladser (par):',
        'afbud_label': 'Afbud:',

        'go_to_substitutlister_btn': 'Tryk her for at gå direkte til substitutlisterne',
        'go_to_afmeldingslister_btn': 'Tryk her for at gå direkte til afmeldingslisterne',
        'go_to_tilmeldingslister_btn': 'Tryk her for at gå direkte til tilmeldingslisterne',
        'add_pair_btn': 'Tilføj Par',
        'add_single_btn': 'Tilføj enkelt spiller',
        'deadline_exceeded_btn': 'Frist overskredet',
        'confirm_btn': 'Bekræft',
        'close_btn': 'Luk',

        'confirm_substitut_title': 'Bekræft valg af substitut',
        'absent_person_label': 'Hvem kommer Ikke? ',
        'your_email_label': 'Din email',
        'your_phone_label': 'Din telefon',
        'prearranged_label': 'Jeg bekræfter, at jeg har lavet en aftale på forhånd',
        'confirmation_title': 'Bekræftelse',
        'confirmation_msg': 'Du har nu valgt denne substitut. Der er sendt en mail til den ansvarlige.',

        'afbud_form_label': 'Meld Afbud:',
        'afbud_placeholder': 'Indtast navn',
        'afbud_submit': 'Meld Afbud',
        'deadline_exceeded': 'Frist overskredet',

        'pair_no_header': 'Parnummer',
        'name_header': 'Navn',
        'partner_header': 'Makker',
        'waitlist_title': 'Venteliste',
        'waitlist_description': 'I tilfælde af for mange tilmeldte vil de ekstra par blive vist herunder. En anden grund til at blive placeret på venteliste er hvis der er et ulige antal tilmeldte par, så vil det sidst tilmeldte par blive sat på venteliste indtil der kommer endnu en tilmelding, således at der vil være et lige antal tilmeldte par.',
        'modal_add_pair_title': 'Tilføj Par',
        'modal_add_single_title': 'Tilføj enkelt spiller',
        'player1_label': 'Navn:',
        'player2_label': 'Makker:',
        'submit_pair_btn': 'Tilmeld Par',
        'submit_single_btn': 'Tilmeld Enkelt Spiller',
        'tl_confirm_title': 'Bekræftelse',
        'tl_confirm_msg': 'Du har nu tilmeldt dig. Der er sendt en mail til den ansvarlige.',
        'error_title': 'Fejl',
        # Login page defaults
        'login_title': 'Log ind',
        'back_to_home_label': 'Til forsiden',
        'django_admin_label': 'Django Admin',
        'django_admin_desc': 'Standard Django administration',
        'wagtail_admin_label': 'Wagtail Admin',
        'wagtail_admin_desc': 'Indholdsredigering og administration',
        'login_hint': 'Du bliver bedt om at logge ind ved første adgang.',
        # Afmeldingslister messages
        'afbud_success_msg': 'Afbud er blevet registreret',
        'input_required_msg': 'Indtast venligst et navn',
        'generic_error_msg': 'Der opstod en fejl. Prøv igen.',
    }

    # Only set values where blank to avoid overwriting existing edits
    changed = False
    for field, value in defaults.items():
        if not getattr(obj, field, ''):
            setattr(obj, field, value)
            changed = True
    if changed:
        obj.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0054_pair_alter_configuration_options_and_more'),
        ('wagtailcore', '0084_workflowcontenttype'),
    ]

    operations = [
        migrations.RunPython(seed_sitecopy, noop),
    ]
