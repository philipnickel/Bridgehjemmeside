# Wagtail Implementation Plan

Goal: Add a Wagtail admin panel on top of the existing Django app to improve content editing and workflows, without replacing the current Django admin or business logic.

## Summary Approach
- Keep Django admin for power users and full data control.
- Introduce Wagtail for content management, curated editing, and safer workflows.
- Incrementally surface domain models in Wagtail via Snippets/ModelAdmin with scoped access.

## 0) Prerequisites and Compatibility
  - Option B: Upgrade to Django 4.2 LTS, then use Wagtail 6.x (preferred long-term).
- Create/activate a virtualenv; back up DB and media before changes.

## 1) Install and Wire Up Wagtail (Admin only)
- Add packages to `requirements.txt` (exact versions after compatibility check):
  - `wagtail` (+ transitive: `modelcluster`, `taggit`)
  - Optional now, later if needed: `wagtail-localize` (for i18n UI), `django-guardian` (object perms)
- Install: `pip install -r requirements.txt`
- settings (`bridge_club_management/bridge_club_management/settings.py`):
  - Add to `INSTALLED_APPS` in a sensible order (before your app is fine):
    - `wagtail.contrib.forms`, `wagtail.contrib.redirects`, `wagtail.embeds`, `wagtail.sites`, `wagtail.users`,
      `wagtail.snippets`, `wagtail.documents`, `wagtail.images`, `wagtail.search`, `wagtail.admin`, `wagtail`,
      `modelcluster`, `taggit`.
    - Keep existing apps as-is.
  - Add middleware: `wagtail.contrib.redirects.middleware.RedirectMiddleware` (after `CommonMiddleware`).
  - Add `WAGTAIL_SITE_NAME = "Substitutliste"`.
  - Ensure static/media settings exist:
    - `MEDIA_URL = "/media/"`, `MEDIA_ROOT = BASE_DIR / "media"`.
  - Optional (multi-language):
    - `WAGTAIL_I18N_ENABLED = True`
    - `LANGUAGES = (("da", "Danish"), ("en", "English"))`
- urls (`bridge_club_management/bridge_club_management/urls.py`):
  - Add admin at a new path, leaving current site untouched:
    - `path("cms/", include("wagtail.admin.urls")),`
    - `path("documents/", include("wagtail.documents.urls")),`
  - If/when using Wagtail pages on the front-end, add `path("", include("wagtail.urls"))` last. For Phase 1, omit this to avoid changing routing.
- Migrate: `python manage.py migrate`
- Verify: `/cms/` loads Wagtail admin; Django admin remains at `/admin/`.

## 2) Create a dedicated app for Wagtail content
- Create app: `python manage.py startapp cms` (or `content`), add to `INSTALLED_APPS`.
- Add initial page models in `cms/models.py`:
  - `HomePage` (optional now), `StandardPage` (generic content), `NewsIndexPage` + `NewsPage`, `EventsIndexPage` + `EventPage`.
  - Use `StreamField` for flexible content (headings, rich text, images, callouts).
  - Register with Wagtail; create `cms/migrations/`.
- Templates under `cms/templates/cms/` with basic blocks; extend later to match site styles.
- Migrate and create a root page + site record through `/cms/` if using front-end pages later.

## 3) Surface domain models in Wagtail (extend, don’t replace)
- Start with read-focused exposure, then allow limited edits where safe.
- Option A: Wagtail ModelAdmin for existing models (no schema change):
  - Expose: `CustomUser` (as Substitutter – read-only or limited fields), `Substitutliste`, `UserSubstitutAssignment`, `Afmeldingsliste`, `Week`, `Day`, `DayResponsibility`, `Tilmeldingsliste`, `TilmeldingslistePair`.
  - Customize list displays, filters, search; restrict forms to safe fields.
  - Scoped querysets per user role (leaders see only their days/weeks).
- Option B: Snippets for curated entities:
  - Create Snippets for content-like data (e.g., “Welcome text”, announcements) or thin wrappers around existing models.
  - Use SnippetViewSet or ModelAdmin for UI; keep Django admin as the authoritative panel.
- Keep business actions (weekly generation, bulk updates) in Django admin/commands, and optionally add “Trigger now” admin actions/buttons in ModelAdmin for convenience.

## 4) Roles, permissions, and scoping
- Define Wagtail Groups: Superuser, Content Editor, Substituteliste Leader, Approver/Moderator.
- Configure permissions:
  - Editors: can edit/publish pages, manage images/documents.
  - Leaders: limited ModelAdmin access with queryset filtered to their responsibilities.
  - Approvers: can publish or approve.
- Implement scoping:
  - In each ModelAdmin class, override `get_queryset` and `get_form_fields` to restrict visibility/editable fields.
  - Optionally use object permissions (e.g., django-guardian) if row-level assignments must be enforced beyond UI.

## 5) Content areas in Wagtail (incremental)
- Map current editable texts to Wagtail:
  - `Configuration` model fields (welcome text etc.) => start as a Wagtail Snippet or `wagtail.contrib.settings`‑based Site settings.
  - Announcement bar/hero content as fields on `HomePage` (or a settings panel if homepage remains in Django templates).
- Keep existing front-end views/templates unchanged initially.
- Once content is validated in Wagtail, consider switching front-end pieces progressively or rendering Wagtail content into existing templates.

## 6) Forms and emails
- For simple site forms, use Wagtail Forms on appropriate pages; store submissions and enable CSV export.
- For domain emails (e.g., notify responsible when a substitute is chosen), keep current logic; expose email subject/body snippets or settings in Wagtail so content is maintainable without changing logic.

## 7) Internationalization (da/en)
- Enable `WAGTAIL_I18N_ENABLED` and define languages in settings.
- Create locales in `/cms/` settings.
- Decide translation policy: translate only public content pages first; keep operational models single-language.
- If needed later, consider `wagtail-localize` for advanced translation workflows.

## 8) Theming and admin UX
- Apply basic Wagtail branding (logo, colors) via Wagtail hooks.
- Keep Tailwind/Bootstrap for site front-end; no change required to use Wagtail admin.
- Add helpful dashboards/panels for leaders (links to their lists, upcoming deadlines).

## 9) Rollout, training, and backout
- Gate access by group membership; start with a pilot group.
- Provide a short guide for editors/leaders.
- Backout: remove group permissions and hide ModelAdmin menus if issues arise; Django admin remains available.

## 10) Deployment notes
- Back up DB and media.
- `python manage.py migrate`
- `python manage.py collectstatic`
- Ensure `MEDIA_ROOT` is writable and served by the platform (PythonAnywhere/other).
- Monitor logs and admin usage.

## Validation checklist
- `/cms/` loads; users can log in with existing Django auth.
- Editors can create/edit pages and upload images; no effect on site routing yet.
- Leaders can see only their relevant lists in Wagtail; edits are limited/safe.
- Existing site at `/` behaves unchanged.
- Emails and nightly jobs continue to work.

## Next concrete tasks (suggested order)
1) Add Wagtail to `requirements.txt`, install, configure settings/middleware/urls, run migrations.
2) Create `cms` app with a minimal `StandardPage` and verify Wagtail admin works.
3) Add ModelAdmin entries for `Substitutliste`, `UserSubstitutAssignment`, and `DayResponsibility` with read-only first.
4) Implement queryset scoping for leaders; create Wagtail groups and assign permissions.
5) Move `Configuration` texts into Wagtail Settings or a Snippet; render in existing templates.
6) Add `News`/`Events` page types and start content entry (optional).
7) Plan i18n enablement and create locales (da/en) when ready.

---
This plan keeps Django admin intact, adds Wagtail incrementally, and provides clear points to pause and validate before exposing more functionality.
