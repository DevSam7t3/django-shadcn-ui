---
name: django-shadcn-ui
description: Build Django template UI from reusable django-cotton components that follow the shadcn/ui design system (shadcn-django), styled only with shadcn semantic Tailwind color tokens, with Alpine.js and HTMX for interactivity. Use this skill whenever writing or editing Django templates, pages, partials, layouts, forms, tables, modals, dashboards, or admin-style screens in a project that has a templates/cotton directory or uses c-button, c-card or other c-* cotton tags, even if the user just says "make a page", "add a form", "build the UI for this view", or "create a component" without mentioning shadcn or cotton. Also use it when creating a new reusable cotton component, wiring HTMX partials into templates, or when the user pastes or names a shadcn/ui block or React component (sidebar, dashboard, login block, .tsx from ui.shadcn.com) to recreate in Django.
license: MIT
---

# Django + shadcn (cotton) UI

This project's UI is built from **django-cotton** components ported from shadcn/ui by
[shadcn-django](https://github.com/SarthakJariwala/shadcn-django). Components live in
`templates/cotton/` and are used as HTML-like tags (`<c-button>`, `<c-card.header>`).
The goal of this skill is a UI that looks and behaves like shadcn everywhere: the same
building blocks reused instead of re-invented, and colors that come only from the
design tokens so light/dark themes and future re-theming keep working.

## Workflow

1. **Inventory first.** List `templates/cotton/` (check `COTTON_DIR` in settings if it
   isn't there) to see which components are actually installed. Do this before writing
   markup — guessing leads to tags that render as nothing.
2. **Compose from existing components.** Map each piece of the UI to a component in
   `references/components.md` (tag names, props, sub-parts, examples). Prefer
   composition: a settings panel is `c-card` + `c-form.field` + `c-input` + `c-button`,
   not a new hand-styled `<div>`.
3. **Missing component?** If shadcn-django ships it (see the catalog's "available but
   maybe not installed" list, or run `uvx shadcn_django list`), install it:
   `uvx shadcn_django add <name>` — this also pulls dependencies. Only when no upstream
   component fits, build a custom one following "Building a new component" below.
   Tell the user what you added.
4. **Write the page/partial** with layout utilities (flex, grid, gap, spacing,
   responsive prefixes) plus semantic color tokens.
5. **Add interactivity**: Alpine.js for local UI state, HTMX for server round-trips.
   See `references/htmx-patterns.md`.
6. **Check colors**: run `python <skill-dir>/scripts/check_colors.py <paths...>` on the
   templates you wrote or edited and fix every finding. Run it on your files, not the
   whole `cotton/` folder: a few upstream components (e.g. toast's destructive state)
   contain raw colors you shouldn't touch. Add `{# check_colors: ignore #}` on a line
   only for a deliberate exception, and say why.

## Porting shadcn/ui blocks

If the user gives you a shadcn/ui block or component in React/TSX (or names one, such as
"sidebar-07"), read `references/porting-blocks.md` first. In short: map each
`@/components/ui/*` import to a cotton component, install or port the missing primitives
as generic components, turn each block file (`nav-main.tsx`…) into its own project
component built from those primitives, and move hard-coded data into Django context.
Keep the source's class strings; they already use the semantic tokens.

## Color rules (the important part)

Use **only shadcn semantic tokens**. Never use the raw Tailwind palette (`bg-blue-500`,
`text-gray-600`, `border-slate-200`, `text-white`, `bg-black`), hex/rgb/oklch literals,
or inline `style="color:..."`. Raw colors don't change with `.dark`, break when the theme
in `input.css` is edited, and drift from the shadcn look.

| Purpose | Tokens |
|---|---|
| Page | `bg-background text-foreground` |
| Surfaces | `bg-card text-card-foreground`, `bg-popover text-popover-foreground` |
| Primary action / emphasis | `bg-primary text-primary-foreground` |
| Secondary | `bg-secondary text-secondary-foreground` |
| Subtle backgrounds, helper text | `bg-muted`, `text-muted-foreground` |
| Hover / selected rows & items | `bg-accent text-accent-foreground` |
| Errors, delete | `bg-destructive text-destructive-foreground`, `text-destructive`, `border-destructive/50` |
| Borders & inputs | `border` (defaults to `border-border`), `border-input` |
| Focus | `ring-ring`, `focus-visible:ring-1` |
| Data viz | `bg-chart-1` … `bg-chart-5` (also `fill-`/`stroke-`) |
| Sidebar | `bg-sidebar`, `text-sidebar-foreground`, `bg-sidebar-accent`, `border-sidebar-border` … |

Opacity modifiers are fine and encouraged for nuance: `bg-primary/90`, `bg-muted/50`,
`bg-background/80`. Radius uses `rounded-sm|md|lg|xl` (mapped to `--radius`).

**Status colors** (success / warning / info) have no default token. Don't reach for
`green-600`. Options, in order:
1. Express it with existing tokens: `c-badge variant="secondary"` for neutral/info,
   `variant="outline"` for pending, `destructive` for failure; or an icon + `text-foreground`.
2. If the design genuinely needs a new semantic color, add a token to `input.css` in all
   three places (`:root`, `.dark`, `@theme inline` as `--color-success`) and then use
   `bg-success text-success-foreground`. Mention to the user that you added a token.

Don't add `dark:` color overrides on components — the tokens already switch. `dark:` is
only for non-color tweaks if ever needed.

## Using components

Conventions every shadcn-django component follows:
- Props via attributes: `<c-button variant="outline" size="sm">`. Defaults are set in the
  component's `<c-vars>`.
- `class="..."` is **appended** to the component's classes — use it for layout/spacing
  (`class="w-full mt-4"`), not to override colors.
- Any other attribute (`type`, `name`, `id`, `hx-post`, `@click`, `x-model`, `disabled`)
  is forwarded through `{{ attrs }}` to the root element.
- Sub-parts use dot notation: `c-card.header`, `c-dialog.content`, `c-table.row`.
- Pass Django variables to props with a colon prefix: `<c-badge :variant="status_variant">`
  (cotton evaluates `:attr` as template context), or `{{ }}` inside plain strings.

```html
<c-card class="max-w-md">
  <c-card.header>
    <c-card.title>Create project</c-card.title>
    <c-card.description>Deploy your new project in one click.</c-card.description>
  </c-card.header>
  <c-card.content class="space-y-4">
    <c-form.field>
      <c-form.label for="name">Name</c-form.label>
      <c-input id="name" name="name" placeholder="Name of your project" />
    </c-form.field>
  </c-card.content>
  <c-card.footer class="flex justify-between">
    <c-button variant="outline">Cancel</c-button>
    <c-button type="submit">Deploy</c-button>
  </c-card.footer>
</c-card>
```

### Django forms

Render fields inside `c-form.field`, using the field's data rather than `{{ form.as_p }}`:

```html
<c-form.field>
  <c-form.label for="{{ form.email.id_for_label }}" :error="form.email.errors">Email</c-form.label>
  <c-input type="email" id="{{ form.email.id_for_label }}" name="{{ form.email.html_name }}"
           value="{{ form.email.value|default_if_none:'' }}"
           {% if form.email.errors %}aria-invalid="true"{% endif %} />
  {% if form.email.help_text %}<c-form.description>{{ form.email.help_text }}</c-form.description>{% endif %}
  {% for e in form.email.errors %}<c-form.error>{{ e }}</c-form.error>{% endfor %}
</c-form.field>
```
Show `form.non_field_errors` with `c-alert variant="destructive"`. Include `{% csrf_token %}`.
If a form renders many fields, make a project component (e.g. `cotton/form/input_field.html`)
that takes a bound field and does the above, rather than repeating it.

## Reuse within the project

When the same composition appears twice (a stat card, a page header with actions, an
empty state, a field row), extract it into its own cotton component under
`templates/cotton/` (e.g. `cotton/stat_card.html` → `<c-stat_card>`), built from the base
components. One edit then updates every page. Keep page templates mostly composition.

## Building a new component

Only after confirming shadcn-django doesn't ship it. Mirror the upstream conventions
exactly so it feels native:

```html
{# templates/cotton/stat_card.html #}
<c-vars title value trend="" variant="default"></c-vars>
<c-card class="{% if class %}{{ class }}{% endif %}" {{ attrs }}>
  <c-card.header class="flex flex-row items-center justify-between space-y-0 pb-2">
    <c-card.title class="text-sm font-medium">{{ title }}</c-card.title>
    {{ icon }}
  </c-card.header>
  <c-card.content>
    <div class="text-2xl font-bold">{{ value }}</div>
    {% if trend %}<p class="text-xs text-muted-foreground">{{ trend }}</p>{% endif %}
    {{ slot }}
  </c-card.content>
</c-card>
```

Checklist:
- `<c-vars>` declares every prop with a sensible default (props not in `c-vars` leak into `{{ attrs }}`).
- Root element merges `{% if class %}{{ class }}{% endif %}` and renders `{{ attrs }}`.
- Content via `{{ slot }}`; extra regions via named slots (`<c-slot name="icon">` → `{{ icon }}`).
- Variants as an `{% if variant == ... %}{% elif %}` block of token classes, like `c-button`.
- Multi-part components go in a folder: `index.html` + `title.html`, etc.
- Build on existing components (`c-card`, `c-button`) instead of duplicating their classes.
- Accessibility: semantic elements, `role`/`aria-*`, `sr-only` labels on icon-only buttons,
  `focus-visible:ring-1 focus-visible:ring-ring` on interactive elements.
- Interactive state with Alpine (`x-data` on the root, `x-cloak` on things hidden initially);
  dispatch window events for cross-component communication, as `c-dialog` does with `show-dialog`.
- Tokens only for color.

Don't edit installed shadcn-django components for one page's needs — pass `class` or wrap
them. Editing is fine for a deliberate project-wide change; say so.

## Interactivity

- **Alpine.js**: open/close, tabs, local toggles, client-side filtering. Components like
  `c-dialog`, `c-sheet`, `c-select`, `c-tabs`, `c-dropdown_menu` already contain their Alpine
  state — use them rather than writing new `x-data` for the same thing.
- **HTMX**: anything that talks to the server — form submits, inline edits, search-as-you-type,
  pagination, deletes. Return partial templates built from the same components.
  Read `references/htmx-patterns.md` before writing hx-* code; it covers partials,
  `HX-Request` detection, re-initialising Alpine after swaps, toasts from responses, and
  CSRF.

## Self-review before finishing

- Every visual element is a `c-*` component or layout utilities around them.
- `check_colors.py` reports nothing.
- Repeated compositions are extracted into components.
- Icon-only buttons have `sr-only` text; forms have labels and error display.
- HTMX endpoints return partials, not full pages, for `HX-Request`.
