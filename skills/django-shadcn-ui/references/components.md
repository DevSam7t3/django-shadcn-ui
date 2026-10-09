# shadcn-django component catalog

Tags, props (with defaults from each component's `<c-vars>`) and usage. Every component
also accepts `class` (appended) and forwards other attributes to its root element.
Folder names use underscores (`alert_dialog`); cotton also accepts hyphens in tags
(`<c-alert-dialog>` == `<c-alert_dialog>`). Pick one style per project.

Always check `templates/cotton/` for what is actually installed. Anything below that is
missing can be installed with `uvx shadcn_django add <folder_name>`.

## Contents
- Actions: button, a, badge
- Layout & display: card, separator, alert, progress, table, accordion, tabs
- Forms: label, input, textarea, checkbox, select, combobox, form
- Overlays: dialog, alert_dialog, sheet, popover, dropdown_menu, toast
- Navigation & search: navigation_menu, command, command_dialog
- Auth: allauth (django-allauth page templates)

---

## Actions

### c-button — `variant="default"` `size="default"`
variant: `default | destructive | outline | secondary | ghost | link`
size: `default | xs | sm | lg | icon`
```html
<c-button>Save</c-button>
<c-button variant="outline" size="sm" type="button">Cancel</c-button>
<c-button variant="ghost" size="icon"><svg>…</svg><span class="sr-only">Settings</span></c-button>
<c-button variant="destructive" hx-delete="{% url 'item-delete' item.pk %}">Delete</c-button>
```
Renders a `<button>`; for navigation use `c-a`.

### c-a — `size="default"`
Link styled to match buttons/links. `<c-a href="{% url 'home' %}">Home</c-a>`.
Check the installed file for its variant options.

### c-badge — `variant="default"`
variant: `default | secondary | destructive | outline`
```html
<c-badge variant="secondary">Draft</c-badge>
<c-badge :variant="order.badge_variant">{{ order.get_status_display }}</c-badge>
```

## Layout & display

### c-card (+ .header .title .description .content .footer)
```html
<c-card>
  <c-card.header>
    <c-card.title>Title</c-card.title>
    <c-card.description>Supporting text</c-card.description>
  </c-card.header>
  <c-card.content>…</c-card.content>
  <c-card.footer class="flex justify-end gap-2">…</c-card.footer>
</c-card>
```

### c-separator — `orientation="horizontal"` `decorative="true"`
`<c-separator class="my-4" />`, vertical: `<c-separator orientation="vertical" class="h-5" />`

### c-alert (+ .title .description) — `variant="default"`
variant: `default | destructive`. An optional leading `<svg>` is auto-positioned.
```html
<c-alert variant="destructive">
  <c-alert.title>Error</c-alert.title>
  <c-alert.description>{{ form.non_field_errors|join:" " }}</c-alert.description>
</c-alert>
```

### c-progress — `value` `min="0"` `max="100"`
`<c-progress :value="job.percent" />`

### c-table (+ .caption .header .body .footer .row .head .cell .empty)
```html
<c-table>
  <c-table.header>
    <c-table.row>
      <c-table.head class="w-[100px]">Invoice</c-table.head>
      <c-table.head class="text-right">Amount</c-table.head>
    </c-table.row>
  </c-table.header>
  <c-table.body id="invoice-rows">
    {% for inv in invoices %}
      <c-table.row>
        <c-table.cell class="font-medium">{{ inv.number }}</c-table.cell>
        <c-table.cell class="text-right">{{ inv.amount }}</c-table.cell>
      </c-table.row>
    {% empty %}
      <c-table.empty>No invoices yet.</c-table.empty>
    {% endfor %}
  </c-table.body>
</c-table>
```
`c-table.empty` renders a full row with centered content; use it in `{% empty %}`.
Put the body rows in a partial template when HTMX will refresh them.

### c-accordion (+ .item .trigger .content) — `type="single"` `collapsible="false"`
Pass the same `value` to item, trigger and content.
```html
<c-accordion type="single" collapsible="true">
  <c-accordion.item value="a">
    <c-accordion.trigger value="a">Question?</c-accordion.trigger>
    <c-accordion.content value="a">Answer.</c-accordion.content>
  </c-accordion.item>
</c-accordion>
```

### c-tabs (+ .list .trigger .content) — `default_value`
```html
<c-tabs default_value="account">
  <c-tabs.list class="grid w-full grid-cols-2">
    <c-tabs.trigger value="account">Account</c-tabs.trigger>
    <c-tabs.trigger value="password">Password</c-tabs.trigger>
  </c-tabs.list>
  <c-tabs.content value="account">…</c-tabs.content>
  <c-tabs.content value="password">…</c-tabs.content>
</c-tabs>
```
For server-loaded panels, put `hx-get` + `hx-trigger="click once"` on the trigger and
target the matching content panel.

## Forms

### c-label, c-input, c-textarea, c-checkbox
Plain elements with shadcn styling; all attributes (`name`, `type`, `value`, `required`,
`x-model`, `hx-*`) pass through.
```html
<c-label for="email">Email</c-label>
<c-input id="email" type="email" name="email" placeholder="you@example.com" />
<c-textarea name="bio" rows="4"></c-textarea>
<div class="flex items-center gap-2">
  <c-checkbox id="terms" name="terms" />
  <c-label for="terms">Accept terms</c-label>
</div>
```

### c-form.* — `field`, `fieldset`, `label` (`error`), `description`, `error`
Spacing and error styling for fields. `c-form.label` turns `text-destructive` when
`error` is truthy. See SKILL.md "Django forms" for the bound-field pattern.

### c-select (+ .trigger .value .content .item) — `name=""`
Custom Alpine dropdown. It submits through a hidden `<input name="{{ name }}">` only when
`name` is set.
```html
<c-select name="framework" class="w-[180px]">
  <c-select.trigger><c-select.value placeholder="Select…" /></c-select.trigger>
  <c-select.content>
    {% for value, label in form.framework.field.choices %}
      <c-select.item value="{{ value }}">{{ label }}</c-select.item>
    {% endfor %}
  </c-select.content>
</c-select>
```
The hidden input's value is set by Alpine, so no native `change` event fires; see
htmx-patterns.md for triggering requests from it.

### c-combobox
Searchable select. Read the installed `templates/cotton/combobox.html` for its props
before using it.

## Overlays

### c-dialog (+ .trigger .content .header .title .description .footer) — `default_open="false"`
`c-dialog.trigger` renders an outline button by default; `as_child="true"` wraps your own
element instead. Closes on backdrop click and Escape. Inside the dialog's scope you can
call `showDialog()` / `hideDialog()`.
```html
<c-dialog>
  <c-dialog.trigger>Edit profile</c-dialog.trigger>
  <c-dialog.content>
    <c-dialog.header>
      <c-dialog.title>Edit profile</c-dialog.title>
      <c-dialog.description>Make changes and save.</c-dialog.description>
    </c-dialog.header>
    <form hx-post="{% url 'profile-edit' %}" hx-target="this" hx-swap="outerHTML" class="grid gap-4">
      {% csrf_token %}
      …
      <c-dialog.footer><c-button type="submit">Save</c-button></c-dialog.footer>
    </form>
  </c-dialog.content>
</c-dialog>
```
`c-dialog` also listens for the window event `show-dialog`. With several dialogs on one
page they would all open, so open dialogs from their own trigger rather than a global
`$dispatch('show-dialog')`.

### c-alert_dialog (+ .trigger .content .header .title .description .footer .cancel .action) — `default_open="false"`
Confirmation for destructive actions. `.cancel` is an outline button, `.action` default.
```html
<c-alert-dialog>
  <c-button variant="destructive"><c-alert-dialog.trigger>Delete</c-alert-dialog.trigger></c-button>
  <c-alert-dialog.content>
    <c-alert-dialog.header>
      <c-alert-dialog.title>Are you absolutely sure?</c-alert-dialog.title>
      <c-alert-dialog.description>This cannot be undone.</c-alert-dialog.description>
    </c-alert-dialog.header>
    <c-alert-dialog.footer>
      <c-alert-dialog.cancel>Cancel</c-alert-dialog.cancel>
      <c-alert-dialog.action class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          hx-delete="{% url 'project-delete' project.pk %}" hx-target="closest tr" hx-swap="outerHTML">
        Delete
      </c-alert-dialog.action>
    </c-alert-dialog.footer>
  </c-alert-dialog.content>
</c-alert-dialog>
```

### c-sheet (+ .trigger .content .header .title .description) — content `side="right"`
side: `top | right | bottom | left`. Good for mobile nav, filters, detail panes.
```html
<c-sheet>
  <c-sheet.trigger><c-button variant="outline">Filters</c-button></c-sheet.trigger>
  <c-sheet.content side="right">
    <c-sheet.header><c-sheet.title>Filters</c-sheet.title></c-sheet.header>
    …
  </c-sheet.content>
</c-sheet>
```

### c-popover (+ .trigger .content) — `default_open="false"`
```html
<c-popover>
  <c-popover.trigger><c-button variant="outline">Open</c-button></c-popover.trigger>
  <c-popover.content class="w-80">…</c-popover.content>
</c-popover>
```

### c-dropdown_menu (+ .trigger .content .label .separator .item)
```html
<c-dropdown-menu>
  <c-button variant="ghost" size="icon">
    <c-dropdown-menu.trigger>⋯<span class="sr-only">Actions</span></c-dropdown-menu.trigger>
  </c-button>
  <c-dropdown-menu.content class="w-48">
    <c-dropdown-menu.label>Actions</c-dropdown-menu.label>
    <c-dropdown-menu.separator />
    <c-dropdown-menu.item>Edit</c-dropdown-menu.item>
    <c-dropdown-menu.item class="text-destructive">Delete</c-dropdown-menu.item>
  </c-dropdown-menu.content>
</c-dropdown-menu>
```

### c-toast (+ .content .trigger) — content `type="default"` `title` `description`; trigger `toast_target`
A toast listens for the window event `show-toast` whose detail is its `id` (or
`{value: id}`) and auto-hides after 3s.
```html
<c-toast id="toast-saved">
  <c-toast.content title="Saved" description="Your changes were saved." />
</c-toast>
<c-toast.trigger toast_target="toast-saved">Show</c-toast.trigger>
```
To show it from a server response, see htmx-patterns.md ("Toasts from the server").

## Navigation & search

### c-navigation_menu (+ .list .item .trigger .content .link .link_details)
`trigger` and `content` take a matching `index`. Read the installed files for structure.

### c-command (+ .input .list .empty .group .item .separator .shortcut)
Filterable command list. `group` takes `heading`, `input` takes `placeholder`, `item`
takes `value`.

### c-command_dialog — `shortcut_key="k"`
Command palette opened with ⌘/Ctrl + key.

## Auth

`allauth/` contains shadcn-styled templates for django-allauth pages (login, logout,
password reset/change, email). Install them with `uvx shadcn_django add allauth` rather
than styling allauth pages by hand.
