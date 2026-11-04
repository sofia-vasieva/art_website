# Putting this site online

Written for Sofia. Follow in order. Steps 1–3 get the site live; steps 4–5 put
your own domain on it. Nothing here needs the command line.

Throughout, `YOURNAME` means your GitHub username.

---

## 1. Create the repository

1. Go to <https://github.com/new> (signed in to your existing account).
2. **Repository name:** `rays-escaping`
   *(Dots are not allowed in GitHub names, so `rays.escaping` can't be used.
   With a custom domain attached in step 4, this name never appears in the URL
   anyway.)*
3. Set it to **Public**. GitHub Pages needs public on a free account.
4. **Do not** tick "Add a README", "Add .gitignore", or "Choose a license" —
   those files already exist here and GitHub would conflict with them.
5. Click **Create repository**.

Leave the page open. You'll want the URL it shows you.

---

## 2. Publish the files with GitHub Desktop

The project folder is already a git repository with everything committed.

1. Open **GitHub Desktop**.
2. **File → Add local repository…**
3. Choose this folder:
   `C:\Users\sofia\OneDrive\Desktop\ART\art_website`
4. It should say the repository has no remote. Click **Publish repository**.
5. In the dialog:
   - **Name:** `rays-escaping` (must match step 1)
   - **Untick "Keep this code private"** ← important
6. Click **Publish repository**.

If GitHub Desktop instead offers "Publish branch", click that.

**Check it worked:** reload your repository page on github.com. You should see
`index.html`, `assets/`, `images/`, `paintings/` and `tools/`.

You should **not** see a `posts/` folder. That's deliberate — the raw Instagram
export contains your Android device ID, so it's excluded by `.gitignore`.

---

## 3. Turn on GitHub Pages

1. On the repository page: **Settings** (top row) → **Pages** (left sidebar).
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. **Branch:** `main`, folder: **`/ (root)`**. Click **Save**.
4. Wait 1–3 minutes. Refresh the page; a banner appears with your live URL:

   `https://YOURNAME.github.io/rays-escaping/`

Open it. The site is now live and you could put that link on your CV as-is.

> If you see a plain unstyled page or a 404, wait another minute and hard-refresh
> (**Ctrl+F5**). First deployments can lag.

---

## 4. Attach your own domain

Skip this if you're happy with the github.io URL.

### 4a. At your domain registrar

Open your domain's **DNS settings** and add **one** record.

**If you're using a subdomain** such as `art.yourdomain.com` — recommended, and
free if you already own the domain:

| Type | Name / Host | Value / Points to |
|---|---|---|
| CNAME | `art` | `YOURNAME.github.io` |

Note the value is `YOURNAME.github.io` — the account, **not** the repository.
Some registrars require a trailing dot: `YOURNAME.github.io.`

**If you're using the bare domain** such as `raysescaping.com`, add four A
records instead:

| Type | Name / Host | Value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

and optionally a CNAME for `www` → `YOURNAME.github.io`.

### 4b. Back on GitHub

1. **Settings → Pages → Custom domain**.
2. Type the full domain, e.g. `art.yourdomain.com`. Click **Save**.
   GitHub adds a `CNAME` file to the repository — that's expected.
3. GitHub checks DNS. You may see *"Domain's DNS record could not be verified"*
   for a while; this is normal and clears once DNS propagates. Usually minutes,
   occasionally up to 24 hours.
4. Once the check passes, tick **Enforce HTTPS**. If it's greyed out, the
   certificate is still being issued — come back later and tick it.

**Don't put the link on your CV until Enforce HTTPS is ticked** and the padlock
shows in the browser.

### 4c. Worth doing

**Settings → Pages → Verify domain** (on your *account* settings, not the repo)
stops anyone else claiming your domain on GitHub later.

---

## 5. Making changes later

After editing anything — `gallery.json`, the about text, CSS:

1. If you changed `gallery.json`, run `python tools/build_site.py` to regenerate
   the pages. (In the project folder: Shift+right-click → "Open PowerShell here".)
2. Open **GitHub Desktop**. Your changes appear in the left panel.
3. Type a short summary in the bottom-left box, click **Commit to main**.
4. Click **Push origin** at the top.

The live site updates within a minute or two.

---

## Troubleshooting

**Site shows a 404.** Check Settings → Pages says branch `main`, folder
`/ (root)`. Check `index.html` is at the top level of the repo, not inside a
subfolder.

**Page loads but has no styling.** Usually a half-finished deploy. Hard-refresh
with Ctrl+F5. If it persists, check `assets/style.css` is present in the repo.

**Images missing.** Confirm the `images/` folder was pushed — it's about 37 MB,
so the first push takes a minute. GitHub Desktop shows upload progress.

**Custom domain stopped working after a push.** GitHub needs the `CNAME` file in
the repo. If it vanished, re-enter the domain in Settings → Pages.

**I want the Instagram export in the repo after all.** Don't. `posts_1.html`
contains `android-…` device identifiers. If you need a backup, keep the ZIP in
OneDrive.
