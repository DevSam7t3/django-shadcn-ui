# django-shadcn-ui

An agent skill for building Django UIs from [shadcn-django](https://github.com/SarthakJariwala/shadcn-django)
cotton components: shadcn/ui design, semantic Tailwind color tokens only, Alpine.js and HTMX.

Works with Claude Code, Cursor, Codex and any agent that supports [skills](https://skills.sh).

## Install

```bash
npx skills add DevSam7t3/django-shadcn-ui
```

Install globally (all projects):

```bash
npx skills add DevSam7t3/django-shadcn-ui -g
```

## What it does

When your agent writes Django templates in a project that uses shadcn-django, this skill makes it:

- **Reuse your components.** It checks `templates/cotton/` and composes pages from `<c-button>`,
  `<c-card>`, `<c-table>`, `<c-dialog>` and the rest instead of hand-styling `<div>`s.
- **Install before building.** Missing components are added with `uvx shadcn_django add <name>`.
  Only components shadcn-django doesn't ship are built by hand, following the same conventions
  (`<c-vars>`, `class` merging, `{{ attrs }}`, slots).
- **Stick to design tokens.** Colors come only from shadcn semantic tokens (`bg-primary`,
  `text-muted-foreground`, `border-input`…), so light/dark mode and re-theming keep working.
  A bundled script flags raw palette classes, hex values and inline color styles.
- **Extract repeated UI.** Compositions used more than once become project components.
- **Use HTMX for server interaction.** Partial templates, forms with validation inside dialogs,
  search-as-you-type, confirmed deletes, toasts triggered from responses.
- **Port shadcn/ui blocks.** Paste a React block (e.g. a sidebar or dashboard) and it is rebuilt as
  reusable cotton primitives plus block-level components, with data moved into Django context.

## Example prompts

- "Build a projects list page with search, status badges, and a create modal using HTMX."
- "Make a dashboard with four KPI cards and a recent orders table."
- "Here's the shadcn sidebar-07 block. Recreate it as my base layout."
- "Add a toggle switch for email notifications that saves immediately."

## Requirements

Your Django project should have:

- [django-cotton](https://django-cotton.com)
- shadcn-django initialised (`uvx shadcn_django init`) with components in `templates/cotton/`
- Tailwind CSS v4 with the shadcn-django `input.css` theme
- Alpine.js, and HTMX if you use the server-interaction patterns
- Python 3 available to the agent, for the color check script

## Contents

```
skills/django-shadcn-ui/
├── SKILL.md                     # workflow, color rules, component conventions
├── references/
│   ├── components.md            # catalog of shadcn-django components, props and usage
│   ├── htmx-patterns.md         # HTMX + Alpine patterns with cotton components
│   └── porting-blocks.md        # translating shadcn/ui React blocks to cotton
└── scripts/
    └── check_colors.py          # flags non-token colors in templates
```

You can run the color check yourself too:

```bash
python skills/django-shadcn-ui/scripts/check_colors.py templates/
```

## Credits

Built on [shadcn-django](https://github.com/SarthakJariwala/shadcn-django) by Sarthak Jariwala,
an unofficial Django port of [shadcn/ui](https://ui.shadcn.com). This skill is not affiliated
with either project.

## License

MIT
