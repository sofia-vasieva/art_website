# Deferred work

Features deliberately held back so the site reads as **finished now**, for PhD
application CVs. Nothing here is abandoned and no progress has been lost — each
item records what it was for, what already exists, and how to switch it on.

Ordered by value to a PhD reader.

---

## 1. About section — highest value, do this first

**Status:** written nothing yet. The section renders only when
`gallery.json → about` is non-empty; until then it produces no heading, no nav
link, no placeholder. Writing the text is the entire task.

**Why it matters more than anything else here.** The paintings show skill; the
About is the only place the site says *why an astrophysicist paints deep-sky
objects*. That connection is the thing an admissions reader actually takes
away. It is worth more than every other item on this page combined.

**This text is Sofia's to write. Claude must not draft or invent it.** Offer the
prompts below, help tighten her own wording if asked, and nothing more.

Aim for **120–200 words, first person**, answering a few of:

- What drew you to deep-sky objects specifically, rather than planets or landscapes?
- What does painting one show you that looking at the photo doesn't?
- Does knowing the physics of what you're looking at change how you paint it?
- Why watercolour? What's technically hardest about it?
- How long does a piece take?
- What do you want someone to feel looking at them?

Don't justify it as "relevant to research" — the connection speaks for itself.

**A starting point in her own words already exists.** Her Instagram
introduction post reads:

> I should make a post to introduce myself. I'm Sofia and I really like
> watercolour painting, especially sunsets, galaxies and other deep-sky
> objects. If you follow my account, maybe my paintings will spice up your
> insta feed! Have a lovely day :)

That post is excluded from the gallery (it isn't a painting) but is preserved
in `posts/posts_1.html`. It's hers to keep, rework or discard.

**To enable:** set `about` in `gallery.json`, run `python tools/build_site.py`.
Section and nav link reappear automatically.

---

## 2. Process section

**Status:** built and working, but unpublished — `SECTIONS` in
`tools/build_site.py` has `("process", …, False)`.

**Why held back:** it contains exactly one entry, the "Watercolour tip #1"
post about starting an M82 painting. A section with a single item looks thin,
which is the opposite of the goal.

**What already exists:** the entry is still in `gallery.json`, and both its
images are still built in `images/{thumb,display,full}/watercolour-tip-*`. The
painting page is not generated and nothing links to it.

**The intent was richer than one post.** It should show how a piece is built up:

- **M101 progress stages** — five or six in-progress photographs exist on
  Sofia's machine (previously seen in a `My paintings` folder) but are **not**
  in the Instagram export, so they were never imported. She would need to point
  at that folder explicitly. *Do not go looking for it — see the scope rule in
  CLAUDE.md.*
- **The M51 timelapse** — a 1.2 GB file, far too large to commit. It belongs on
  her YouTube channel (<https://youtube.com/@raysescaping4526>) and should be
  embedded, not hosted. No ffmpeg needed, no bandwidth cost.

**To enable:** flip the flag to `True` and rebuild. Worth adding the M101 shots
first so it isn't a section of one.

---

## 3. Reference astrophotos per painting

**Status:** dropped from v1 by agreement. Nothing built.

**Intent:** show the real astronomical image each painting was made from, small,
beside the piece, clearly captioned — making the scientific grounding explicit.

**Why it was dropped: licensing, and it is genuinely slow.** Each image needs
checking individually.

- **Safe to embed with attribution:** NASA, ESA/Hubble, ESO, NOIRLab, JWST —
  public domain or CC BY 4.0.
- **Not safe:** work by individual astrophotographers, amateur or professional.
  A file named `NGC2403_credit_tony_hallas.jpg` sits in the parent `ART` folder
  and is exactly this case — Tony Hallas is a professional and his image must
  not be republished without written permission.

If revisited: flag any reference whose licence cannot be confirmed rather than
guessing, and link out instead of embedding where permission is unclear.

---

## 4. Phase 2 — high-resolution images

**Status:** not started. Current images come from the Instagram export, which
re-compresses to 1080–1440px on the long edge (one 10.3 MP outlier survives).

The site is perfectly presentable as-is; this is an upgrade, not a repair. The
URLs and page structure do not change, so it is safe to do after applications
go out.

**Source priority, best first:**

1. **Re-scan the physical painting.** Best possible result. Watercolour scans
   flat and true. A 600 dpi flatbed scan of an A4 piece is ~35 MP. An existing
   phone document-scan of the M64 painting reached 4.1 MP and looked excellent.
2. **Google Photos at original quality** — album, then Shift+D or a
   Takeout export scoped to that album. Not "storage saver".
3. **Straight off the phone by cable** — `DCIM/Camera`, no cloud re-compression.
4. Fall back to the current export image where nothing better survives.

**Matching must not be guessed.** Mismatching a painting to the wrong caption is
worse than a low-resolution image. Three signals:

1. **Exact EXIF timestamp.** Each entry carries `takenRaw` from the export,
   precise to the second (e.g. `2025:09:10 09:51:34`). An original whose own
   `DateTimeOriginal` matches is the same photograph — effectively proof.
2. **Perceptual hash** against the existing version.
3. **Direct visual comparison** (permission granted to view `posts/` images).

Produce a review table and **have Sofia confirm before swapping anything**.
Entries with no confident match keep their current image.

Keep originals out of the repo — `originals/` is gitignored, and raw camera
files carry GPS coordinates.

---

## 5. Smaller open decisions

| Item | Question |
|---|---|
| **"A portrait"** | An A4 painting of Sofia's nephew, currently published under *Other work*. Already public on Instagram, but a child's portrait on a CV-linked site is a different context. Her call; undecided. |
| **"Hierarchical Bubble Structure"** | Her caption names no object, so the title came from her own hashtag `#hierarchicalbubblestructure`. May want renaming. |
| **NGC 1501 size** | Shows `A6` while the postcard-sized pieces now show `10.5 × 14.8 cm` — the same dimensions. Offered to unify; no answer yet. |
| **Contact details** | None on the site. An academic email would be reasonable; a personal address or phone number would not. |
