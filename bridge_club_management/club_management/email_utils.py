from django.conf import settings
from django.core.mail import send_mail as django_send_mail


def format_subject(subject: str) -> str:
    """Prefix subject with EMAIL_SUBJECT_PREFIX if defined."""
    prefix = getattr(settings, 'EMAIL_SUBJECT_PREFIX', '') or ''
    return f"{prefix}{subject}" if prefix else subject


def inject_testsite_banner(message: str) -> str:
    """If running on test-site, prepend a clear banner to the email body."""
    is_test_site = getattr(settings, 'TEST_SITE', False)
    if not is_test_site:
        return message
    banner = (
        "[TEST-SITE]\n"
        "Denne email er sendt fra test-siden (staging/dev).\n"
        "Hvis du ikke forventede denne besked, kan den ignoreres.\n\n"
    )
    return f"{banner}{message}"


def send_tilmeldingsliste_email(subject: str, message: str, recipient_list: list[str]) -> int:
    """Send an email for tilmeldingslister with environment-specific formatting."""
    formatted_subject = format_subject(subject)
    formatted_message = inject_testsite_banner(message)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    return django_send_mail(formatted_subject, formatted_message, from_email, recipient_list) 