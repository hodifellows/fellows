# Hodi Fellows: the fellows page

This is a page https://hodifellows.com/fellows that will display fellows who have participated in the program.

Each fellow adds one small file about themselves. A Python script turns those files into a page of photos; selecting a photo opens a card with the fellow's bio, languages, links and, when they finish, a testimonial.

New here? Start with **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## How it works

```
fellows/<username>.yaml  ─┐
photos/<username>.jpg    ─┼─▶ scripts/build.py ─▶ _site/ ─▶ hodifellows.com/fellows
templates/ + static/     ─┘
```

1. A fellow adds `fellows/<username>.yaml` (and optionally a photo) in a pull request.
2. The **Check** workflow runs the tests and a test build on every pull request.
3. After review, the pull request is merged into `main`.
4. The main website rebuilds and publishes the page within a few minutes.

Profiles are **static**: they change only when someone merges a change. Nothing is fetched from GitHub automatically.

## Run it on your computer

You need Python 3.10 or newer.

```bash
pip install -r requirements-dev.txt
python -m pytest -q                       # run the tests
python scripts/build.py                   # build the page into _site/
python -m http.server --directory _site   # preview at http://localhost:8000
```

Fonts come from the main website, so your local preview uses your computer's fonts. That's expected.

## Folders

| Path | What's in it |
| --- | --- |
| `fellows/` | One YAML file per fellow. `_template.yaml` shows every field |
| `photos/` | Fellow photos (square, about 400 × 400) |
| `templates/index.html` | The page layout (HTML with Jinja2) |
| `static/` | Styles (`styles.css`) and the script that opens cards (`fellows.js`) |
| `scripts/build.py` | Reads the fellow files, checks them and builds the page |
| `scripts/add_fellow.py` | Creates your fellow file from your GitHub profile, once |
| `tests/` | pytest tests |
| `.github/` | Issue forms, the pull request template and workflows |

## Privacy

A profile is published only when its file says `consent: true`, which the fellow sets themselves. To remove a profile, delete the file (or set `consent: false`) and its photo in a pull request. Questions: hello@hodifellows.com.

## For maintainers: connecting to hodifellows.com

The main website (`SBusienei/hodi-fellows-site`) builds this repo into `/fellows` when it deploys. It rebuilds daily on its own. To make it update right after each merge:

1. Create a **fine-grained personal access token** (GitHub → Settings → Developer settings) with access to `SBusienei/hodi-fellows-site` only and **Contents: Read and write** permission.
2. In this repo, go to **Settings → Secrets and variables → Actions** and add it as `SITE_DISPATCH_TOKEN`.

The **Update hodifellows.com** workflow then asks the website to rebuild after every merge.

## Licence

MIT. See [LICENSE](LICENSE).
