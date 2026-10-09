# Porting shadcn/ui blocks (React/TSX) to Django + cotton

Use this when the user pastes or names a shadcn/ui block or component (sidebar-07,
dashboard-01, login-03, a `components/ui/*.tsx` file) and wants it in Django.

The aim is a faithful visual port built from **reusable cotton components**, not one
flattened template. A shadcn block is two layers, and both become cotton components:

1. **UI primitives** it imports from `@/components/ui/*` (Button, Avatar, Sidebar…)
2. **Block parts** defined in the block itself (`app-sidebar.tsx`, `nav-main.tsx`,
   `nav-user.tsx`, `team-switcher.tsx`)

## Contents
1. Workflow
2. Mapping shadcn/ui imports to cotton
3. Translating JSX
4. Porting a primitive that shadcn-django doesn't ship
5. Example: the Sidebar

---

## 1. Workflow

1. **Inventory the imports.** List every `@/components/ui/*` import and every local
   component file in the block. If the user gave only a block name, ask them to paste the
   code. If network access is available, you can instead fetch it from the shadcn/ui repo.
   Don't reconstruct a block from memory, because the class strings matter.
2. **Map each primitive** using the table in section 2. Check `templates/cotton/` for
   what is installed, and run `uvx shadcn_django add <name>` for anything available but
   missing.
3. **Port missing primitives** (section 4) into `templates/cotton/<name>/`. Do this first,
   because the block parts depend on them.
4. **Port each block part** to its own project component (`nav-main.tsx` →
   `templates/cotton/nav_main.html` → `<c-nav_main>`), built from the primitives.
5. **Move data out of the markup.** Hard-coded arrays in the block (`data.navMain`,
   `teams`, `user`) become Django context. Use the view for page data, and a context
   processor for app-wide data like nav items and the current user's teams.
6. **Assemble** the block in the base layout or page template, then run `check_colors.py`.
7. **Tell the user** which primitives were installed, which were ported, and what was
   simplified (e.g. tooltip-on-collapsed replaced by `title=`).

## 2. Mapping shadcn/ui imports to cotton

| shadcn/ui (React) | cotton |
|---|---|
| Button | `c-button` (same variant/size names) |
| Badge, Card*, Alert*, Separator, Label, Input, Textarea, Checkbox, Progress, Table* | same name, `c-*` |
| Tabs*, Accordion*, Dialog*, AlertDialog*, Sheet*, Popover*, DropdownMenu*, Select*, Command*, NavigationMenu* | same name, `c-*` (snake_case folder, e.g. `c-dropdown_menu.item`) |
| Sonner / Toast | `c-toast` |
| Form + react-hook-form | Django form + `c-form.*` (see SKILL.md) |
| Sidebar*, Avatar, Collapsible, Tooltip, Breadcrumb, Skeleton, Switch, ScrollArea, HoverCard, Toggle, RadioGroup, Slider, Pagination | not in shadcn-django: check `uvx shadcn_django list`, otherwise port (section 4) |
| Chart (recharts) | not portable as markup; use a JS chart lib with `--chart-1..5` colors via `getComputedStyle`, or ask the user |

Compound parts map to dot notation: `<CardHeader>` → `<c-card.header>`,
`<DropdownMenuItem>` → `<c-dropdown_menu.item>`, `<SidebarMenuButton>` →
`<c-sidebar.menu_button>`.

## 3. Translating JSX

| React | Django / cotton / Alpine |
|---|---|
| `className="…"` | `class="…"` (keep class strings verbatim; they already use tokens) |
| `cn(base, cond && "x", className)` | `class="base {% if cond %}x{% endif %} {% if class %}{{ class }}{% endif %}"` |
| `cva` variants | `<c-vars variant="default">` + `{% if variant == '…' %}` blocks, like `c-button` |
| `{items.map(i => …)}` | `{% for i in items %}…{% endfor %}` |
| `{cond && <X/>}` / ternary | `{% if %}…{% else %}…{% endif %}` |
| `{...props}` | `{{ attrs }}` on the root element |
| `children` | `{{ slot }}`; extra regions → named slots |
| `asChild` (render child as root) | wrap the child: put the anchor inside, or render `<a>` with the primitive's classes when an `href` prop is given |
| `<Link href="/x">` | `<a href="{% url 'name' %}">` |
| `useState` / open state | Alpine `x-data` on the component root |
| `data-state={open ? "open" : "closed"}` | `x-bind:data-state="open ? 'open' : 'closed'"` (keep the `data-[state=open]:` classes working) |
| `data-active={isActive}` | `data-active="{% if request.resolver_match.url_name == 'x' %}true{% else %}false{% endif %}"` |
| `usePathname()` active check | `request.resolver_match` / `request.path` (needs the request context processor) |
| `useIsMobile()` | Tailwind breakpoints (`md:`), plus `c-sheet` for the mobile variant |
| lucide-react `<Home />` | inline `<svg>` copied from lucide.dev (ISC license), or a project `<c-icon name="home" />` component that includes `icons/<name>.svg`; keep `[&_svg]:size-4` sizing |
| Collapsible | Alpine `x-data="{open:false}"` + `x-show` with `x-transition`; mirror `data-state` |
| Tooltip | `title="…"` for a simple port; a small Alpine tooltip component if it matters visually |
| `onClick` handlers that call APIs | HTMX (`hx-post`, etc.); see htmx-patterns.md |
| `"use client"`, imports, types | drop |

## 4. Porting a primitive that shadcn-django doesn't ship

Use the shadcn/ui source of that primitive as the spec and follow "Building a new
component" in SKILL.md:

- One folder per primitive, one file per exported part (`avatar/index.html`,
  `avatar/image.html`, `avatar/fallback.html`).
- Copy each part's class string from the source and convert `cn`/`cva` per section 3.
- Keep the same part names in snake_case, so future ports map 1:1.
- Primitives must stay generic: no app data, URLs or copy inside them. These go in
  block parts or pages.
- Radix behaviour (focus management, keyboard, aria) becomes Alpine plus the right
  `role`/`aria-*` attributes. Implement what the block actually uses, not all of Radix.

## 5. Example: the Sidebar

The shadcn Sidebar is the largest primitive. Its tokens (`--sidebar`,
`--sidebar-accent`, `--sidebar-border`, …) already exist in shadcn-django's `input.css`,
so use `bg-sidebar`, `text-sidebar-foreground` and the other sidebar tokens.

Suggested structure (`templates/cotton/sidebar/`):

```
provider.html      Alpine state: open (desktop expanded/collapsed), openMobile; Ctrl/Cmd+B toggle
index.html         desktop <aside> (hidden md:block) + mobile c-sheet; collapsible="offcanvas|icon|none"
trigger.html       c-button variant="ghost" size="icon" that toggles
inset.html         <main> next to the sidebar
header.html  content.html  footer.html  separator.html  rail.html
group.html  group_label.html  group_content.html
menu.html  menu_item.html  menu_button.html  menu_action.html  menu_badge.html
menu_sub.html  menu_sub_item.html  menu_sub_button.html
```

Key points:
- **State on the provider.** `x-data="{ open: …, openMobile: false, toggle() {…} }"`.
  Set `data-state` and `data-collapsible` on the sidebar root so the source's
  `group-data-[collapsible=icon]:…` classes keep working unchanged.
- **Persist without flash.** shadcn stores `sidebar_state` in a cookie. Read it in Django
  (`request.COOKIES.get("sidebar_state", "true")`) to render the initial `open` server-side,
  and write the cookie from Alpine in `toggle()`.
- **Mobile** reuses `c-sheet` (`side="left"`) rather than a second implementation.
- **menu_button** takes `href`, `active` and `size` (`default|sm|lg`): render `<a>` when
  `href` is set, otherwise `<button>`, with `data-active` driving the active styles.
- **Block parts** (`app_sidebar`, `nav_main`, `nav_projects`, `nav_user`, `team_switcher`)
  compose these with `c-dropdown_menu`, `c-avatar` (ported) and collapsible groups, and get
  their items from context:

```html
{# templates/cotton/nav_main.html #}
<c-vars items></c-vars>
<c-sidebar.group>
  <c-sidebar.group_label>Platform</c-sidebar.group_label>
  <c-sidebar.menu>
    {% for item in items %}
      <c-sidebar.menu_item x-data="{ open: {{ item.is_active|yesno:'true,false' }} }">
        <c-sidebar.menu_button :href="item.url" :active="item.is_active" @click="open = !open">
          {% include item.icon %}<span>{{ item.title }}</span>
        </c-sidebar.menu_button>
        {% if item.children %}
          <c-sidebar.menu_sub x-show="open" x-transition>
            {% for child in item.children %}
              <c-sidebar.menu_sub_item>
                <c-sidebar.menu_sub_button :href="child.url" :active="child.is_active">{{ child.title }}</c-sidebar.menu_sub_button>
              </c-sidebar.menu_sub_item>
            {% endfor %}
          </c-sidebar.menu_sub>
        {% endif %}
      </c-sidebar.menu_item>
    {% endfor %}
  </c-sidebar.menu>
</c-sidebar.group>
```

Page layout then becomes:

```html
<c-sidebar.provider :default_open="sidebar_open">
  <c-app_sidebar :nav="nav" :user="request.user" />
  <c-sidebar.inset>
    <header class="flex h-16 items-center gap-2 border-b px-4">
      <c-sidebar.trigger /><c-separator orientation="vertical" class="h-4" />
      {% block breadcrumb %}{% endblock %}
    </header>
    {% block content %}{% endblock %}
  </c-sidebar.inset>
</c-sidebar.provider>
```
