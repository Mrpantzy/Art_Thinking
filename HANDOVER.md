# Handover: Disaster Networking

A satirical, LinkedIn-style site for an ESCP class project. Natural disasters have fictional LinkedIn profiles. This repo is the deployable site: a hub page that looks like the LinkedIn home feed, plus the original full profile pages that the hub opens.

Every person, company, number and quote on the site is fictional satire. Real event facts (USGS quakes, Gezani, Gironde fires, drought data) come from the user's own profile files. Keep the satire banner at the top of the page.

## Live links

| What | Value |
| --- | --- |
| Production URL | https://disaster-networking.vercel.app |
| GitHub repo | https://github.com/Mrpantzy/Art_Thinking (branch `main`) |
| Vercel project | `disaster-networking` (`prj_gfSST20mgn4WClvAW2XYNXBzDPAy`), personal Hobby account (`team_kDKAMk2lYoJrsMQ3YJ8RL47j`) |
| Git link | Vercel project is connected to the repo. A push to `main` redeploys to production on its own. |
| Preview copy | claude.ai artifact `https://claude.ai/artifact/VdoqAGenH5qdMKJmwun8vy` (private, slightly older wrapper; the repo is the source of truth) |

The production URL is public (no Vercel login), so the QR code works for anyone.

## Repo layout

```
index.html        The hub (single file: CSS + markup + JS + embedded base64 images)
profiles/
  dr-ought.html     Original profile pages, self-contained, unmodified
  wild-fire.html      except earth-quake.html (see Gotchas)
  tsu-nami.html
  tye-phoon.html
  earth-quake.html
qr.html           Phone-friendly QR page (/qr) for the live site; qr.svg + qr.png (print)
vercel.json       { "cleanUrls": true }
HANDOVER.md       This file
```

There is no build step, no package.json and no framework. Vercel serves the files as static.

## How the hub works (`index.html`)

Single file, around 820 lines plus long base64 lines. Vanilla JS. Open it in a browser to test.

**Perspective.** The viewer is **Dr. Ought**: "You" on his posts, his photo in the nav, left card and comment box. He is the owner of the point of view. Do not switch it.

**Data (top of the `<script>`):**
- `IMG`: base64 JPEGs (avatars, Dr. Ought cover, Somalia/England post images, Earth Quake post image). `imgSrc(k)` also accepts a raw `data:` URL for user-uploaded photos.
- `PPL`: people. Fields `n` name, `h` headline, `img` key (or `c` colour for an initials avatar), `prof` profile slug, `deg`, `you`. People without `prof` open a small person card instead of a profile.
- `PROF`: slug to display name for the profile viewer.
- `BIO`: every character's job, school and follower count, merged into `PPL` and shown on person cards. Keep follower counts identical to the profile pages (Dr. Ought 1,203,884 · Wild Fire 2,847,319 · Tsu Nami 1,874,206 · Earth Quake 1,562,903 · Tye Phoon 968,431).
- `POSTS`: feed posts. Fields `id`, `by`, `t` (relative time text), `title` (bold catchy title), `text` (keep it short), `tags`, `img`, `src` caption, `rx`, `likes`, `cm`, `rp`, and `th` (comment thread; each comment has `p`, `t`, `l`, `w` and optional `re` replies).
- `JOBS`: detailed job objects (salary, workplace, level, applicants, hiring manager `hire`, responsibilities, requirements, perks, skills match, company). `jobs()` renders the search/list; `jobDetail(i)` the full job view.
- `NOTIFS`, `MSG0`/`REPLY`, `GROUPS`, `NEWSL`, `EVENTS`, `INFO`: content for the secondary pages and modals.

**State:** one object `st` (liked, saved, open comment threads, connections, view, sort, messages, and so on). Nothing is persisted. A reload resets everything, including posts the user writes.

**Rendering:**
- `render()` draws the centre column for `st.view` (`home`, `network`, `jobs`, `messaging`, `notifs`). `PAGES` holds the non-home pages. `feedHTML()` and `postHTML(o)` draw the feed.
- `avatar(id)` and `nameBtn(id)` produce clickable people. They use `data-open` (profile slug) or `data-person` (person card).
- All clicks are delegated from one listener. `ext(t)` handles `data-act="name:arg:arg2"` and calls `ACT[name](arg, button, arg2)`. Add a new interaction by adding an `ACT` entry and a `data-act` attribute.
- `modal()` and `pop()` make the dialog and the popover. `openProfile(slug)` shows a profile in a full-screen iframe with a "Back to feed" bar.
- Comments are open by default for any post with a thread. `.cm-in input` posts a comment as Dr. Ought.

**Styling:** CSS tokens at the top (`--bg`, `--card`, `--blue` and so on) with light, dark (`prefers-color-scheme`) and `data-theme` variants. Layout copies LinkedIn desktop: 225px | 555px | 300px, collapsing to one column under 760px. Keep the `[hidden]{display:none!important}` rule.

## Verified behaviour

A Playwright run clicked about 35 controls (all nav pages, menus, composer, save, repost, send, reactions, tags, person cards, messaging with auto-reply, comments) with no console errors. There was no horizontal scroll at 400px on the home, network, jobs, messaging and notifications views. To re-test, load `index.html` in Chromium and click through the same set.

## Gotchas

- `profiles/earth-quake.html` was **slimmed**: the original was 17 MB (over limits) because one 4 MB profile photo was repeated four times. It was replaced with a 420px JPEG. The text and layout are unchanged. The other four profile files are byte-for-byte the user's originals.
- Tye Phoon's profile only had a truncated post ("…more"), so the hub shows only the text that was actually in the file. Do not invent the rest without asking.
- Some content is invented to make the feed feel alive: extra comments, the Jobs, Groups, Events and Newsletters lists, notifications, message threads, the news list. It is in the same satirical tone. The user knows and can edit it.
- The hub's profile viewer loads `profiles/<slug>.html` in an iframe (relative path). Keep that folder layout when moving files.
- Images are base64 inside `index.html`. Editing the file with tools that choke on very long lines can be painful. Prefer search/replace on distinctive strings or a small script.
- The original build used a scratch template plus a Python patch step, which no longer exists. `index.html` in the repo is the only source now.

## Showcase video

A 60 s 1080p showcase MP4 (feed, Congratulate Earth Quake, Dr. Ought profile, QR outro) is for the team to use separately. The MP4 itself is deliberately not in this repo or on the site. How to make or change it: `video/VIDEO_HANDOVER.md` (the `video/` folder is excluded from Vercel by `.vercelignore`).

## Ideas the user may want next

- Persist posts, comments and messages (localStorage, or a small backend) so they survive a reload.
- Add more disaster profiles. Add a `PPL` entry, a `PROF` slug, a file in `profiles/`, and posts in `POSTS`. Optionally add to `SUG` (the "Add to your feed" list).
- Turn off Vercel Authentication so the class can view it without a Vercel account.
- Add a custom domain.
- Tidy the page `<title>` and add a share image.

## Working agreements

- The user is an ESCP student working on this for class. Keep changes in the same voice and keep the site visually faithful to LinkedIn.
- Commit messages in this repo have been ending with the Claude attribution trailers the harness provides.
- Ask before pushing large or structural changes. Every push to `main` goes live.
