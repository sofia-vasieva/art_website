# CLAUDE.md

Static gallery site for **Sofia Vasieva's** watercolour paintings of deep-sky
objects. Purpose: a link in the "additional skills and interests" section of her
**PhD applications**, as a more professional alternative to her Instagram
(@rays.escaping) that people without an account can also view.

That purpose drives the taste calls: quiet, fast, legible on a phone, and
unmistakably hers.

---

## Standing instructions from Sofia

These persist across sessions. Do not relax them without her saying so.

1. **Stay inside this folder.** Do not browse `OneDrive`, `Desktop\PHOTOS`,
   `Pictures` or anywhere else on the machine. She will give an explicit path
   when she wants a folder used. *(This followed an early session where
   unprompted searching through her personal photo folders was not OK.)*
2. **Invent nothing.** Titles, object names, catalogue numbers, medium and
   dimensions come **only** from what she already wrote in her Instagram
   captions. Do not look facts up, and do not fill gaps from general knowledge.
   If a caption doesn't say it, the field stays empty and isn't rendered.
3. **The About text is hers to write.** Offer prompts; never draft it.
4. **Commit and push after every set of changes.** Don't leave work sitting in
   the working tree — the live site is what she's linking from her CV, so
   finishing a change means it is on GitHub. Run the `posts/` leak check below
   before each push.
5. **Ship finished, not half-done.** Unfinished features are held back rather
   than shown as placeholders or thin sections. See **[DEFERRED.md](DEFERRED.md)**
   before proposing anything "missing" — it is probably deferred on purpose,
   with the reasoning and the restore instructions recorded there.

---

## Current state

- Repo: <https://github.com/sofia-vasieva/art_website> — public, branch `main`,
  all commits pushed.
- **Live** at <https://sofia-vasieva.github.io/art_website/> (Pages enabled,
  deploying from `main` / `/ (root)`). **This is the URL on Sofia's CV.** When
  the custom domain is attached, GitHub redirects this URL to it, so the CV
  stays correct — do not break or rename the repo.
- Custom domain **`art.sofiavasieva.com`** is planned but not attached — she is
  waiting on a registrar transfer to IONOS. Instructions are in
  [PUBLISHING.md](PUBLISHING.md) §4. Don't add DNS records mid-transfer.
- **Published:** 28 paintings — 22 `deepsky`, 6 `other`. 37 MB of images.
- **Held back:** the `process` section (1 entry) and the About section. The site
  is intended to look complete as it stands.

### Deferred — read [DEFERRED.md](DEFERRED.md)

Four things were deliberately postponed, with full context preserved there:
the **About text** (highest value to a PhD reader, and Sofia's to write), the
**Process section**, **reference astrophotos**, and **Phase 2 high-resolution
images**. Plus one smaller undecided item: the "Hierarchical Bubble Structure"
title.

Do not treat any of these as oversights to fix unprompted.

---

## How it is built

No framework, no Node, no Jekyll (`.nojekyll` is committed). Python 3 + Pillow
generate plain static HTML. The published site has no build step.

```
posts/              raw Instagram export  ** GITIGNORED, see Gotchas **
tools/              the three build scripts
gallery.json        single source of truth for content
index.html          generated
paintings/*.html    generated, one per entry
assets/style.css    all styling (dark theme)
assets/app.js       lightbox only; site works fully without JS
images/{thumb,display,full}/   generated, JPEG + WebP each
```

### Pipeline

```bash
python tools/parse_ig_export.py   # posts/posts_1.html -> gallery.json
python tools/build_images.py      # source images -> images/   (incremental)
python tools/build_site.py        # gallery.json -> index.html + paintings/
python -m http.server 8000        # preview at http://localhost:8000
```

**Usually you only need `build_site.py`.** Edit `gallery.json` by hand for
titles, captions, section moves and the `about` field, then regenerate.

**Re-running `parse_ig_export.py` overwrites `gallery.json` from the captions**,
discarding hand edits. It does preserve built image records (matched by slug),
so it won't force an image rebuild. Durable content tweaks belong in the
script's own tables (`TITLES`, `SIZE_NORMALISE`, `SWAP_ORDER`, `MERGE_INTO`,
`EXCLUDE`, `NO_CAPTION`), not in `gallery.json`.

**`NO_CAPTION`** holds slugs shown with medium, size and date but *no* caption
prose — currently `a-walk`, `sunset`, `a-guinea-pig`, `another-guinea-pig`, at
Sofia's request (those captions were casual asides). The medium/size is still
extracted from the caption first, so nothing is lost. `build_site.py` renders no
caption block at all for these, in both the painting page and the lightbox.
Unknown slugs in the set fail the build.

`build_images.py` skips entries whose derivatives already exist; pass `--force`
to rebuild all (~3 minutes). Both build scripts prune orphans, so renaming a
title (which changes the slug) leaves no stale files behind.

### gallery.json shape

```
artist, copyright, youtube, instagram, about, entries[]
entry: slug, title, section, order, caption, hashtags, medium, size,
       posted, postedISO, takenRaw, sourceImages[], images[]
images[i]: w, h, lqip, thumb{jpg,webp,w,h}, display{...}, full{...}
```

`section` is one of `deepsky` | `other` | `process`. Gallery order follows
`order`; `SWAP_ORDER` in the parser overrides positions.

### Showing and hiding sections

`SECTIONS` in `tools/build_site.py` carries a `published` flag per section. An
unpublished section keeps its entries in `gallery.json` and its built images,
but renders no cards, no nav link and no painting pages — so switching one back
on is a single `False` → `True` and a rebuild, with nothing to re-import.

The **About** section works the same way implicitly: it renders only when
`gallery.json → about` is non-empty. There is deliberately **no placeholder** —
an empty stub reads as unfinished, which is worse than its absence.

`build_site.py` prints a `held back (…)` line listing anything suppressed, so
the state is visible on every build.

---

## Gotchas

**There are two dates per entry, and only one is real.**

- `posted` / `postedISO` — the **post date**, from `<div class="_3-94 _a6-o">` in
  the export, e.g. `окт 24, 2026 2:37 am`. Present on all 31 posts, strictly
  descending, and it confirms export order *is* newest-first. This is the one
  displayed, as month and year only. The parser fails the build if any entry
  comes out without it.
- `takenRaw` — the EXIF **capture** date of the photograph. Only 14 of 29 have
  one and it is not monotonic. **Never display or sort by it.** It exists solely
  to identify the same photograph when swapping in high-resolution originals.

Gallery order still follows `order` (export order), not a date sort. The two now
agree, but `order` is what the code uses and what `SWAP_ORDER` adjusts.

The export UI is Russian, so month names are parsed through `RU_MONTHS` in the
parser.

**Dates show on painting pages and in the lightbox, not on the index cards** —
`meta_bits(entry, with_date)` in `build_site.py` controls this, so the grid stays
quiet while each piece's own page carries a full gallery label
(medium · size · month year).

**The gallery must read row by row.** It originally used CSS `column-count`
masonry, which flows down each column — so with 22 deep-sky pieces in 3 columns
the oldest seven landed at the top of the right-hand column, which Sofia
noticed. It is now a real grid with square cells and `object-fit: contain`
(nothing cropped). If you change the layout, preserve left-to-right,
top-to-bottom reading order.

**`posts/` must never be committed.** `posts_1.html` embeds two Android device
IDs and camera firmware strings, 19 occurrences. It is gitignored. Verify before
any push — this must print nothing:

```bash
git grep -lE "android-[0-9a-f]{16}" HEAD
```

The IDs themselves are deliberately not quoted here: this file is public, and an
earlier version pasted a prefix of one into it, which both leaked it and made the
check match itself. Read them out of `posts/posts_1.html` if you ever need them.

**Instagram mislabels file extensions.** 12 of the export's files end `.webp` or
`.heic` but are JPEG inside. `build_images.py` detects true format; never trust
the extension.

**EXIF is stripped from every generated image**, GPS included. Phone originals
carry home coordinates — this matters most for Phase 2. Verify:
`python -c "from PIL import Image; print(Image.open('images/full/<x>.jpg').getexif())"`

**Titles are guarded against drift.** Each `TITLES` entry carries a `verify`
substring that must appear in that post's caption, or the build fails. This
enforces instruction 2 mechanically. Note it checks the *verify term*, not the
title text, so a typo introduced into a title can still pass — read titles.

**Pushing needs a large buffer.** 37 MB over HTTP resets the connection with
git's 1 MB default. Already configured locally:
`http.postBuffer=524288000`, `http.version=HTTP/1.1`.

**GitHub Desktop "Publish repository" will always fail here** — the repo already
exists, and Publish only knows how to *create*. Use `git push`. (Historical: the
first create returned HTTP 500 *after* succeeding, which caused the confusion.)

**Size strings are normalised for display only** (`10.5x14.8cm` → `10.5 × 14.8
cm`); caption prose is untouched. `"postcard size"` maps to `10.5 × 14.8 cm` at
Sofia's request.

---

## Writing style for this repo

Match the existing code: plain Python, standard library plus Pillow, no
cleverness, comments only where intent isn't obvious. Comments explain *why*
(the device-ID exclusion, the format detection) rather than restating the code.
