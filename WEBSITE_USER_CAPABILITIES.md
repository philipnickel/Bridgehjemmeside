# Website User Capabilities and Wagtail Admin Implications

This document summarizes what users can do on the site and highlights what to consider when adding a Wagtail-based admin UI.

## Roles (Observed)

- Public Visitor: Unauthenticated user interacting with lists (primary flow).
- Substitute (CustomUser): Domain user type with contact info and availability.
- Day Coordinator: A Django user assigned to a day (via DayResponsibility) and receiving notifications.
- Admin/Staff: Manages lists, users, and configuration in the admin.

## Public Features by Area

- Front Page
  - View Substitutlister (substitute lists) grouped by week/day with responsible coordinator info.
  - View Afmeldingslister (cancellation lists) and upcoming dates.
  - View Tilmeldingslister (registration lists) overview and capacities.
  - Read configurable texts: welcome, section intros (from Configuration model).

- Substitutlister
  - Select a substitute for a specific list/date (POST `select_substitut`).
    - Provide: absent person, email, phone, pre-arranged flag.
    - Effect: assignment status → “Optaget”; email sent to responsible coordinator.
  - Meld afbud (report absence) for a substitute (POST `meld_afbud`).
    - Effect: assignment status → “Fraværende”; email sent to responsible coordinator.

- Afmeldingslister
  - View all upcoming Afmeldingslister.
  - Append a name to a specific afbud list (POST `append_afbud/<id>`).
    - Deduplicated (case-insensitive), stored in `afbud` text field.
  - View afmeldingsliste details page.

- Tilmeldingslister (Event Registration)
  - View lists ordered by date; see registered pairs, waitlist, and singles.
  - Sign up as a pair (names, phone, email).
    - Validation: prevent duplicate player names across name/makker fields.
    - Auto assignment of `på_venteliste` and `parnummer` handled downstream.
    - Email confirmation sent.
  - Sign up as a single player.
    - Auto-pair with existing single if present, sending notifications to both; otherwise stored as single.

- Authentication
  - Basic login page provided; admin at `/admin/` uses Django auth.

## Data Model Highlights (What Admins Manage)

- Configuration: `welcome_text`, and per-section texts.
- Række: player ranking/group.
- Day: named weekdays; DayResponsibility links a coordinator (user) to a day.
- CustomUser (Substitutter): username, phone/email, række, availability (`days_available`), responsibilities, note.
- Week: label like “33-2024”.
- Substitutliste: name, week, day, deadline; saving triggers `update_assignments()` to seed assignments from availability.
- UserSubstitutAssignment: per user/list assignment with `status` (Ledig/Optaget/Fraværende) and `reservationsnote`.
- Afmeldingsliste: name, day, deadline, `afbud` text (comma-separated names prefixed by “Afbud:”).
- Tilmeldingsliste: name, day, deadline, responsible person, capacity (`antal_par`).
  - Changing `antal_par` can move waitlisted pairs via signals.
- TilmeldingslistePair: per-list registrations with names, contact, waitlist flag, optional `parnummer`, and `is_single`.

## Wagtail Admin Implications

- Model registration
  - Use Wagtail ModelAdmin to manage: Substitutliste, Afmeldingsliste, Tilmeldingsliste, Weeks, Days, DayResponsibility, Række, CustomUser, Configuration.
  - Consider Wagtail Snippets for Configuration texts and possibly Række/Day.

- Inlines / Editing UX
  - Substitutliste: inline panel for UserSubstitutAssignment (editable status, reservationsnote) for manual adjustments.
  - Tilmeldingsliste: inline panel for TilmeldingslistePair (with controls for waitlist and ordering). Make `parnummer` read-only if auto-managed.

- Actions & Signals
  - Ensure `Substitutliste.save()` hook (auto-assignments) and `Tilmeldingsliste.save()` (waitlist moves) still run via Wagtail admin submissions.
  - Provide admin actions to: regenerate assignments, bulk set statuses, move pairs between main/waiting lists.

- Permissions
  - Coordinators should only manage their day’s lists: set up groups/permissions or implement per-object filtering in ModelAdmin `get_queryset()`.
  - Limit who can edit Configuration texts.

- Validation & Constraints
  - Surface duplicate-player checks on Tilmeldingslister in the admin forms.
  - Prevent duplicate names in `afbud` when editing Afmeldingslister manually (or migrate storage to a normalized model).

- Email & Notifications
  - Keep email hooks for selection, cancellations, and registration confirmations. Consider using a service (and env settings) surfaced in admin.

- Content Editing
  - Rich text for `welcome_text` and section texts (Wagtail’s rich text field or StreamField if later expanded).

- Lists and Filters
  - Add list filters/search: by day, week, deadline, status; search by user name/phone/email.
  - Useful ordering: by date for lists; by `parnummer` for pairs; by status for assignments.

- Internationalization
  - Current UI mixes Danish labels with English day keys; ensure consistent translations in admin field labels and choices.

- Future niceties
  - Dashboard panels: upcoming lists needing attention, unpaired singles, assignments with Fraværende status.
  - Import/export helpers for substitutes (CSV) and historical lists.

## Quick URL Map (Public)

- `/` → Front page (lists + texts)
- `/substitutlister/` → Substitute lists
- `/afmeldingslister/` → Cancellation lists
- `/afmeldingsliste/<id>/` → Cancellation list details
- `/tilmeldingslister/` → Registration lists
- POST `/select_substitut/` → Choose substitute for a list
- POST `/meld_afbud/` → Mark substitute as absent
- POST `/append-afbud/<id>/` → Append a name to Afmeldingsliste
- `/admin/` → Django admin (for now)

## Risks/Edge Cases to Note

- Duplicate detection on registrations relies on matching two name fields (navn/makker) — fuzzy duplicates not handled.
- `afbud` is a free-text field; consider normalizing to a related model for robust edits/history.
- Assignment generation depends on `days_available` names matching Python weekday names exactly.
- Emails require proper SMTP config; in local settings, console backend is used.

