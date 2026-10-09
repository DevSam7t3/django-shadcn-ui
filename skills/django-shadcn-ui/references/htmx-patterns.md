# HTMX + Alpine patterns with cotton components

Division of labour: **Alpine** owns client-only UI state (open/closed, active tab, the
selected value of `c-select`). **HTMX** owns anything that needs the server. Responses
are HTML partials built from the same `c-*` components as full pages.

## Contents
1. Setup (scripts, CSRF)
2. Partial templates and views
3. Forms: validate, show errors, succeed
4. Forms inside dialogs and sheets
5. Search, filters, pagination
6. Delete with confirmation
7. Toasts from the server
8. c-select with HTMX
9. Loading states
10. Alpine and swapped content

---

## 1. Setup

In the base template, load htmx and Alpine and send the CSRF token with every request:

```html
<head>
  <link rel="stylesheet" href="{% static 'css/output.css' %}">
  <script src="{% static 'js/htmx.min.js' %}" defer></script>
  <script src="{% static 'js/alpine.min.js' %}" defer></script>
  <style>[x-cloak]{display:none!important}</style>
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}' class="min-h-screen bg-background text-foreground antialiased">
```
Serve the scripts locally (or pinned versions) in production rather than unpinned CDN URLs.
Don't add these again if the project's base template already has them.

## 2. Partial templates and views

Keep each swappable region in its own template (`app/partials/_project_rows.html`) and
`{% include %}` it from the full page, so the first render and HTMX refreshes share one
source of truth. Cotton components work inside partials like anywhere else.

```python
def project_list(request):
    projects = Project.objects.filter(...)
    template = "projects/partials/_project_rows.html" if request.headers.get("HX-Request") else "projects/list.html"
    return render(request, template, {"projects": projects})
```
If `django-htmx` is installed, use `request.htmx` instead of reading the header. On Django
6+ (or with `django-template-partials`), `{% partialdef %}` and `template.html#name` can
replace separate files — follow whatever the project already does.

When an HTMX request targets a region that a non-HTMX request also renders (e.g. with
`hx-push-url`), add `Vary: HX-Request` (`django.utils.cache.patch_vary_headers`) so caches
don't serve a partial as a full page.

## 3. Forms

Wrap the form in a partial that renders the whole form (fields + errors), swap it with
itself, and re-render with errors on invalid input:

```html
{# partials/_project_form.html #}
<form id="project-form" hx-post="{% url 'project-create' %}" hx-target="this" hx-swap="outerHTML" class="grid gap-4">
  {% csrf_token %}
  {% if form.non_field_errors %}
    <c-alert variant="destructive"><c-alert.description>{{ form.non_field_errors|join:" " }}</c-alert.description></c-alert>
  {% endif %}
  {# fields using the c-form.field pattern from SKILL.md #}
  <c-button type="submit" hx-disabled-elt="this">Create</c-button>
</form>
```
```python
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        response = render(request, "projects/partials/_project_row.html", {"project": project})
        response["HX-Retarget"] = "#project-rows"
        response["HX-Reswap"] = "afterbegin"
        response["HX-Trigger"] = json.dumps({"show-toast": "toast-project-created", "project-saved": True})
        return response
    return render(request, "projects/partials/_project_form.html", {"form": form})
```
Return invalid forms with status 200: htmx does not swap 4xx responses by default. (If the
project has configured `htmx.config.responseHandling` to swap 422, follow that instead.)

## 4. Forms inside dialogs and sheets

Swap only the form *inside* `c-dialog.content` — never the dialog root, which holds the
Alpine `open` state. Close it when the server signals success with a custom event:

```html
<c-dialog>
  <c-dialog.trigger>New project</c-dialog.trigger>
  <c-dialog.content @project-saved.window="hideDialog()">
    <c-dialog.header><c-dialog.title>New project</c-dialog.title></c-dialog.header>
    {% include "projects/partials/_project_form.html" %}
  </c-dialog.content>
</c-dialog>
```
The `project-saved` event comes from the `HX-Trigger` header in section 3. `c-sheet` works
the same way with `hideSheet()` on `c-sheet.content`.

Don't pass `x-init` to `c-dialog` or `c-sheet` roots: they already define one, and a
duplicate attribute is dropped by the browser. Put extra Alpine directives on `.content`.

To reset the form after success, have the success response also send a fresh form via an
out-of-band swap (`<form id="project-form" hx-swap-oob="true">…</form>`).

## 5. Search, filters, pagination

```html
<c-input type="search" name="q" placeholder="Search projects…" class="max-w-sm"
         hx-get="{% url 'project-list' %}" hx-trigger="input changed delay:300ms, search"
         hx-target="#project-rows" hx-include="#project-filters" hx-push-url="true" />
```
Group filters in a `<form id="project-filters">` and `hx-include` it so search, filters and
page number travel together. Pagination buttons are `c-button variant="outline" size="sm"`
with `hx-get="?page={{ page_obj.next_page_number }}"` and `hx-include` on the same form;
render them inside the partial so they update with the rows.

## 6. Delete with confirmation

Use `c-alert_dialog` (see components.md) rather than `hx-confirm`, so confirmation looks
like the rest of the UI. The action button carries `hx-delete`, `hx-target="closest tr"`,
`hx-swap="outerHTML"`; the view returns an empty 200 response (or `HX-Trigger` a toast).
htmx sends DELETE with the CSRF header from section 1; read `request.method == "DELETE"`
in the view.

## 7. Toasts from the server

Place toasts once in the base template:
```html
<c-toast id="toast-saved"><c-toast.content title="Saved" description="Your changes were saved." /></c-toast>
```
Then fire one from any response:
```python
response["HX-Trigger"] = json.dumps({"show-toast": "toast-saved"})
```
htmx dispatches `show-toast` with `detail.value == "toast-saved"`; the event bubbles to
`window`, where `c-toast` listens. For messages that vary per request, return the toast
markup out-of-band and show it on init:
```html
<div id="toast-slot" hx-swap-oob="true">
  <c-toast id="toast-dynamic" x-init="$nextTick(() => show())">
    <c-toast.content title="{{ title }}" description="{{ message }}" />
  </c-toast>
</div>
```
(with an empty `<div id="toast-slot"></div>` in the base template). Wiring Django's
`messages` framework into this slot is a good project-level component.

## 8. c-select with HTMX

`c-select` keeps its value in Alpine and writes it to a hidden input, so there's no native
`change` event. Inside a form that submits normally, nothing extra is needed — the hidden
input is submitted. To fire a request when the value changes, watch it and trigger a
custom event on the root:

```html
<c-select name="status"
          x-init="$watch('value', () => $nextTick(() => htmx.trigger($el, 'select-changed')))"
          hx-get="{% url 'project-list' %}" hx-trigger="select-changed"
          hx-include="#project-filters" hx-target="#project-rows">
  …
</c-select>
```
Put the select inside `#project-filters` so its hidden input is included.

## 9. Loading states

- `hx-disabled-elt="this"` on submit buttons prevents double submits (disabled styling comes from `c-button`).
- `hx-indicator="#spinner"` plus an element with class `htmx-indicator` for a spinner;
  style it with tokens, e.g. `text-muted-foreground animate-spin`.
- Dim a region while loading: `class="transition-opacity [&.htmx-request]:opacity-50"` on the target.

## 10. Alpine and swapped content

Alpine v3 initialises `x-data` in newly swapped HTML automatically, so components inside
partials (dialogs, dropdowns, selects) just work. State lives on the element, though:
swapping an element that holds `x-data` resets it. Choose `hx-target`s *inside* the
Alpine scope you want to keep (form inside dialog, rows inside table body), not the scope
root itself.
