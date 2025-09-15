from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create initial Wagtail pages (Home + section pages) if missing. Idempotent."

    def handle(self, *args, **options):
        try:
            from wagtail.models import Site, Page
            from club_management.models import (
                HomePage, SubstitutlisterPage, AfmeldingslisterPage, TilmeldingslisterPage
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Wagtail not available or models missing: {e}"))
            return

        site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
        if site and site.root_page:
            root = site.root_page.specific
        else:
            root = Page.get_first_root_node()

        def get_or_create_page(parent, model, title, slug):
            page = model.objects.filter(slug=slug).first()
            if page:
                return page
            page = model(title=title, slug=slug)
            parent.add_child(instance=page)
            page.save_revision().publish()
            return page

        # Create HomePage
        home = HomePage.objects.first()
        if not home:
            home = get_or_create_page(root, HomePage, title="Forside", slug="forside")
            self.stdout.write(self.style.SUCCESS("Created HomePage"))
        else:
            self.stdout.write("HomePage exists; skipping")

        # Create children pages
        subs = SubstitutlisterPage.objects.first()
        if not subs:
            subs = get_or_create_page(home, SubstitutlisterPage, title="Substitutlister", slug="substitutlister")
            self.stdout.write(self.style.SUCCESS("Created SubstitutlisterPage"))
        else:
            self.stdout.write("SubstitutlisterPage exists; skipping")

        afl = AfmeldingslisterPage.objects.first()
        if not afl:
            afl = get_or_create_page(home, AfmeldingslisterPage, title="Afmeldingslister", slug="afmeldingslister")
            self.stdout.write(self.style.SUCCESS("Created AfmeldingslisterPage"))
        else:
            self.stdout.write("AfmeldingslisterPage exists; skipping")

        tilm = TilmeldingslisterPage.objects.first()
        if not tilm:
            tilm = get_or_create_page(home, TilmeldingslisterPage, title="Tilmeldingslister", slug="tilmeldingslister")
            self.stdout.write(self.style.SUCCESS("Created TilmeldingslisterPage"))
        else:
            self.stdout.write("TilmeldingslisterPage exists; skipping")

        self.stdout.write(self.style.SUCCESS("Wagtail pages seeding complete."))

