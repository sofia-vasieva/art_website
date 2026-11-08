# rays.escaping — watercolour paintings of deep-sky objects

A small static site for Sofia Vasieva's watercolour paintings. No build system,
no dependencies at serve time — just HTML, CSS and one small JavaScript file.

- **[PUBLISHING.md](PUBLISHING.md)** — how to put this online.
- **[DEFERRED.md](DEFERRED.md)** — features held back on purpose, and how to
  finish them later.
- **[CLAUDE.md](CLAUDE.md)** — orientation for Claude Code sessions.

## Structure

```
index.html            gallery + about
paintings/*.html      one page per painting (generated)
gallery.json          the data: titles, captions, sizes, image records
assets/style.css      all styling
assets/app.js         lightbox (the site works fine without it)
images/{thumb,display,full}/   generated derivatives, JPEG + WebP
tools/                the build scripts
posts/                raw Instagram export — NOT committed, see .gitignore
```

## Rebuilding

Requires Python 3 with Pillow (`pip install Pillow`).

```bash
python tools/parse_ig_export.py   # posts/posts_1.html -> gallery.json
python tools/build_images.py      # source images -> images/*  (slow, ~3 min)
python tools/build_site.py        # gallery.json -> index.html + paintings/
```

Run them in that order. `parse_ig_export.py` preserves already-built image
records, so editing titles or sections does **not** force an image rebuild.

To preview locally:

```bash
python -m http.server 8000
```

then open <http://localhost:8000>.

## Editing content

Most changes belong in **`gallery.json`** — titles, captions, section
assignment (`deepsky` / `other` / `process`), and the `about` field. After
editing it, run `tools/build_site.py` only. Do not re-run the parser, or it
will overwrite your edits from the Instagram captions again.

## What's shown, and what isn't

The site currently publishes **28 paintings** across *Deep sky* and
*Other work*. The *Process* section and the *About* text are finished features
that are deliberately switched off, so the site reads as complete rather than
half-built. Nothing was deleted:

- **Process** — `SECTIONS` in `tools/build_site.py`, flip `False` to `True`.
  Its entry and images are still in place.
- **About** — appears automatically as soon as `about` in `gallery.json` has
  text in it. There is no placeholder by design.

`build_site.py` prints a `held back (…)` line on every build so nothing gets
quietly forgotten. Full reasoning in [DEFERRED.md](DEFERRED.md).

## Notes

- Captions come verbatim from the Instagram export. Medium and size are
  extracted from the caption text and shown as separate metadata, so the
  duplicate "Watercolour, 10.5 x 14.8 cm" line is stripped from the prose.
- Every title is checked against its caption at build time: if a title's key
  term is not present in what was actually written, the build fails.
- All EXIF is stripped from generated images, including GPS.
