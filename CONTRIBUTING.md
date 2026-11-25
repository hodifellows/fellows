# Contributing

Thanks for building this with us. Every change, big or small, goes through the same steps: **issue → branch → pull request → review → merge**. Nothing reaches the live site without a review.

## Your first pull request: add yourself

1. **Open an issue** with the **"Add myself to the fellows page"** form (Issues → New issue).
2. **Get the code** (once):
   ```bash
   git clone https://github.com/hodifellows/fellows.git
   cd fellows
   pip install -r requirements-dev.txt
   ```
3. **Make a branch** for your change:
   ```bash
   git checkout -b add-<your-username>
   ```
4. **Create your file.** Either run the helper, which copies your GitHub name, bio and photo once:
   ```bash
   python scripts/add_fellow.py <your-github-username>
   ```
   or copy `fellows/_template.yaml` to `fellows/<your-username>.yaml` (lowercase) and fill it in.
5. **Check every field**, write a bio in your own words, and set `consent: true` if you agree to be shown.
6. **Test and preview:**
   ```bash
   python -m pytest -q
   python scripts/build.py
   python -m http.server --directory _site
   ```
   Open http://localhost:8000 and select your card.
7. **Commit and push:**
   ```bash
   git add fellows/ photos/
   git commit -m "Add <your name> to the fellows page"
   git push -u origin add-<your-username>
   ```
8. **Open a pull request** on GitHub. Fill in the template and write `Closes #<your issue number>`.
9. **Respond to review.** A groupmate reviews first, then a lead. Push more commits to the same branch to make changes.

## Picking up other issues

- Look for the labels **`good first issue`** (easier) and **`stretch`** (harder). Issues are grouped into steps (Step 1 to Step 6): finish one step's issues before moving to the next.
- **Comment "I'd like to take this"** and wait to be assigned. One person per issue.
- **Keep pull requests small:** one issue per pull request.
- Stuck for more than an hour? Comment on the issue with what you tried. Asking is part of the work.
- Can't finish? Say so on the issue so someone else can pick it up.

## Reviewing a groupmate's pull request

Everyone reviews as well as codes. When you review:

- Pull the branch and run it: `git fetch origin && git checkout <branch>`, then test and build.
- Check it does what the issue asked, and nothing else.
- Be kind and specific: *"Could we name this `photo_path` so it's clearer?"* rather than *"bad name"*.
- Approve when you'd be happy for it to go live.

## Ground rules

- **Explain your work in your own words** in the pull request. You're welcome to use AI tools, but you must understand and be able to explain every line you submit.
- **Never commit secrets** (passwords, tokens) or anyone else's personal information.
- **Only add your own profile**, never someone else's.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
