# cheshire0xff.github.io

Personal site: short stories, blog, opinions and links.
Live at **https://cheshire0xff.github.io/**

Built with a small Python static site generator (Mako templates, Markdown content), managed with [uv](https://docs.astral.sh/uv/) and deployed to GitHub Pages by GitHub Actions.

## Writing content

Each post is a folder with one Markdown file per language; the filename is the language code (`en`, `pl`):

```
content/stories/cien/
    en.md        # English, the default
    pl.md        # optional translation
    assets/      # optional images
```

- Sections: `content/stories/`, `content/blog/`, `content/opinions/`, `content/pages/` (About, Links).
- Front matter: `title` (required), `date`, `tags`, `summary`, `draft: true`, `original: <lang>`.
- The default language is `en` when present; `original:` overrides it.
- A PL | EN switch is shown only when a post has more than one language file.
- `date` must match across the language files of a post; tags are merged.

## Development

```powershell
uv sync
uv run sitegen serve      # build and serve on http://127.0.0.1:8000
uv run sitegen build      # build into dist/
uv run mypy --strict
uv run pylint src tests
uv run pytest
```

## Deployment

Pushing to `main` runs `.github/workflows/pages.yml`: type checks, lint, tests, build, deploy.
Pages source must be set to **GitHub Actions** (Settings → Pages).
`.github/workflows/ci.yml` runs the same checks for branches and pull requests.
