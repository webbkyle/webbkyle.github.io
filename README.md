# Kyle Webb — GitHub Pages site

Professional site: bio, resume, CV, and mini project space.
Live at `https://webbkyle.github.io` (repo: `webbkyle.github.io`).

## Structure

- `index.html` — Bio / home
- `resume/index.html` — concise resume
- `cv/index.html` — full CV (publications, service, earlier roles)
- `mini-projects/index.html` — mini project space (new write-ups appended as projects complete)
- `assets/css/style.css` — shared styles

## Deploy

This is a plain static site (no Jekyll build step needed):

1. Copy the contents of this folder into your `webbkyle.github.io` repo:
   ```bash
   cp -r ~/workspace/github-pages/* /path/to/webbkyle.github.io/
   ```
2. Commit and push:
   ```bash
   cd /path/to/webbkyle.github.io
   git add -A && git commit -m "Update professional site" && git push
   ```
3. GitHub Pages serves it automatically at `https://webbkyle.github.io`.

## Switching to a custom domain later

Yes — easy, no rebuild needed:

1. Buy the domain (e.g. Namecheap, Cloudflare, Porkbun).
2. In your `webbkyle.github.io` repo: Settings → Pages → Custom domain → enter it (e.g. `kylewebb.dev`) and save. This creates a `CNAME` file.
3. At your DNS provider, add:
   - `A` records for `@` pointing to GitHub Pages IPs (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`), or
   - `CNAME` for `www` → `webbkyle.github.io`
4. Wait for DNS + enable "Enforce HTTPS" in Pages settings.

Switching back is just removing the custom domain in settings.

## Adding a mini project write-up

Copy the commented template in `mini-projects/index.html`, fill in title/date/summary/repo link, and push. Each write-up follows: Problem → Approach → Results → Takeaways.
