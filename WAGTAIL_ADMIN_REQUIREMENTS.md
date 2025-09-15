# Wagtail Admin Requirements

This document outlines what an administrator should be able to do through a Wagtail-powered admin, layered on top of the existing Django app. Wagtail extends the current system; it does not replace the existing Django admin. Content editing and curated workflows live in Wagtail, while deep data management and power-user tasks remain available in Django admin.

## Core Content Management
- Manage pages: Home, About, News, Events, Contact, and custom pages.
- Rich text editing with images, links, embeds, and documents.
- Drafts, preview before publish, scheduled publishing/unpublishing.
- Version history with compare and revert.
- Media library: upload, organize, reuse images/files with alt text and captions.

## Homepage & Announcements
- Edit hero banner (title, subtitle, image, CTA).
- Manage announcement bar for urgent messages (maintenance, closures).
- Add/reorder content sections (text blocks, image callouts, links).

## News/Updates
- Create and categorize news posts (tags/categories).
- Schedule posts and pin featured items to the homepage.
- Archive view and search across posts.

## Events & Calendar
- Create club events (title, date/time, location, description, optional image).
- Optional registration link/CTA; external or internal form.
- Optional calendar export (iCal) and list/calendar views.

## Substitutes & Lists (Domain-Specific)
Align Wagtail with existing Django models by using Wagtail Snippets and/or admin views:
- Manage Substitute profiles as Snippets (name, contact, notes, status).
- Manage Substitution Lists by day/week with assignments.
- Mark substitute availability (vacation/absence) and effective dates.
- Assign “Responsible for day” and change ownership.
- Approve and authorize new substituteliste leaders.
- Manage off-boarding/opt-out lists.
- Trigger or override weekly list generation; run on-demand updates.
- View activity log/history for list changes and assignments.

## Forms & Submissions
- Build and edit simple site forms (contact, sign-up, feedback) using Wagtail Forms.
- View, search, and export submissions (CSV) from the admin.
- Basic spam protection (honeypot/recaptcha if configured).

## Email & Notifications
- Manage email templates for automatic notifications (e.g., notify responsible when a substitute is chosen).
- Configure recipient roles/addresses per notification type.
- View delivery status/logs for important notifications (where feasible).

## Navigation & Structure
- Edit main navigation menu and footer links.
- Manage redirects (legacy URLs to new pages).
- Control 404/empty state messaging.

## Users, Roles, and Workflow
- Define roles (examples): Superuser, Content Editor, Substituteliste Leader, Approver/Moderator.
- Per-section/page permissions (who can add/edit/publish which content).
- Optional editorial workflow: submit for review, approve, publish.
- Audit trail: who changed what and when (page history, snippet revisions).
 - Scoped access for Substituteliste Leaders to only their lists/weeks.

## Accessibility & Quality
- Alt text required for images; warnings for missing metadata.
- Image renditions and size presets to optimize performance.
- Link checking and basic accessibility guidance where possible.

## Integrations & Technical
- Reuse existing Django models for substitutions via Wagtail Snippets or custom ModelAdmin.
- Keep email backend and existing notification logic; expose template/content in Wagtail.
- Optional: expose event feed via iCal, and structured data (schema.org) for SEO.
- Multilingual content: English and Danish.
- Coexistence: Do not remove or replace Django admin; use Wagtail ModelAdmin/Snippets for curated, safer editing paths while leaving full model control in Django admin for power users.

## Operations
- Nightly/automated tasks continue to run (weekly checks, list rollovers) with manual override buttons in admin.
- Backups and content export guidance (database-level in current setup).

## Migration Notes (High-Level)
- Map current static content (homepage text, announcements) to Wagtail Pages/StreamFields.
- Convert relevant domain models to Snippets or integrate with Wagtail ModelAdmin.
- Migrate current media into Wagtail’s media library.
- Preserve URLs; add redirects if structures change.
 - Keep Django admin intact throughout; surface the most common content operations in Wagtail first and expand incrementally.

## Open Questions
- Which parts of substitution workflows should be surfaced in Wagtail vs. remain in Django admin?
- Should events support registrations internally or link out only?

---
