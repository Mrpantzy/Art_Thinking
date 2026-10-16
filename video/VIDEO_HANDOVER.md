# Handover: the Disaster Networking showcase video

This covers how the showcase video is made, what it uses, and how to change it. For the website itself, see `../HANDOVER.md`.

## What the video is

| | |
| --- | --- |
| File | `disaster-networking-showcase-pov.mp4` (not stored in this repo; shared with the team separately) |
| Length / format | 133 s, 1920×1080, 30 fps, H.264 MP4, about 26 MB |
| Point of view | **Dr. Ought** operates the site herself: a visible cursor clicks, types and posts |
| Audio | None (silent, subtitled). Add music in an editor if wanted (see "Adding sound") |
| Purpose | For the team to use in presentations. It is **not** embedded in the website |

The `video/` folder is listed in `../.vercelignore`, so nothing in it is deployed to Vercel.

## Storyboard

Subtitles explain the meaning of the project, not how LinkedIn works. Keep them as they are unless the team agrees on new wording.

| # | On screen | What Dr. Ought does | Subtitle |
| --- | --- | --- | --- |
| 1 | Title card | | "What happens when destruction learns to speak the language of success?" |
| 2 | Card "The idea" | | "We gave real disasters professional profiles, and let them describe their damage the way we are taught to describe our careers." |
| 3 | Feed | Opens *Write article*, types a title and post ("Five Seasons Without Rain: My Biggest Growth Story ☀️"), clicks Post | "In the language of personal branding, every outcome becomes a success story." |
| 4 | Wild Fire's Gironde post | Likes it, comments "Incredible scale, Wild! 🔥 Our dry-season groundwork really paid off. Let's align on Q4." | "42,000 hectares burned and 250,000 people displaced become "territory transformed"." |
| 5 | Earth Quake's Alaska post | Likes it | "An earthquake becomes a "shaky start to the day"." |
| 6 | "My house literally collapsed." comment | Clicks Reply, answers the local resident with corporate jargon ("…a chance to rightsize your housing footprint? Open to connect!") | "When a victim speaks, the answer is PR: "Always valuable to hear from key stakeholders."" |
| 7 | Her Somalia post | Replies to Hank Hurricane: "water is a legacy model" | "A failed rainy season and lost harvests become "key highlights" of a record quarter." |
| 8 | Tye Phoon's Gezani post | Corporate condolences: "Thoughts with all impacted stakeholders 🙏 That said, 29 districts in one quarter is best-in-class reach." | "59 lives lost, filed under "operational disruption"." |
| 9 | Her England post | Likes a comment and the post | "Likes and reposts reward the framing, not the reality." |
| 10 | Congratulate card | Clicks "Congratulate Earth Quake", then posts the pre-filled message | "The platform itself prompts us to celebrate…" then "Applause comes pre-written. Reflection does not." |
| 11 | Her own profile | Opens it, scrolls About, Featured, Activity, Experience, Education | One subtitle per section (see the script) |
| 12 | Card "The critique" | | "Personal branding, corporate jargon and performative success can reduce serious social and environmental harm to metrics, achievements and "impact at scale"." |
| 13 | Card "The question" | | "Behind every "impact" metric are people and places. What does our professional language leave out?" |
| 14 | QR page | | "Explore the network yourself: scan the QR code." |

Dr. Ought is referred to as **she**.

## Resources used

Everything is free and runs locally on a Mac. No accounts, API keys or paid tools.

| Resource | What it is for | Where it comes from |
| --- | --- | --- |
| The website in this repo | All footage, images and text in the video | `../index.html`, `../profiles/`, `../qr.html` |
| Python 3.9+ | Runs the recording script | Preinstalled on macOS (`python3`) |
| Playwright 1.60 + Chromium headless shell | Drives a real browser and takes a screenshot per frame | `pip install playwright`, then `python -m playwright install chromium` (about 90 MB) |
| imageio-ffmpeg 0.6 | Bundled ffmpeg binary that turns the frames into an MP4 | `pip install imageio-ffmpeg` (no Homebrew needed) |
| Python's built-in web server | Serves the site locally at `http://localhost:8765` | `python3 -m http.server` |
| `video/record_pov.py` | The whole video: storyboard, cursor, typing, subtitles, encoding | This folder |

No external images, stock footage or music are used. Every visual already exists on the site (the images are embedded in the HTML files). Fonts are the system fonts.

## How to make the video

Run these from the repo root (`Art_Thinking/`).

1. One-time setup (a throwaway virtual environment):

```bash
python3 -m venv .venv-video
```

```bash
.venv-video/bin/pip install -r video/requirements.txt
```

```bash
.venv-video/bin/python -m playwright install chromium
```

2. Start the local site in a separate terminal and leave it running:

```bash
python3 -m http.server 8765
```

3. Record (takes about 6–8 minutes; frames go to a temporary folder):

```bash
.venv-video/bin/python video/record_pov.py http://localhost:8765 /tmp/dn-frames ~/Desktop/disaster-networking-showcase-pov.mp4
```

You can point it at the live site instead (`https://disaster-networking.vercel.app`), but the local copy is faster and always matches your latest edits.

4. Delete `/tmp/dn-frames` afterwards (about 4,000 JPEGs). `.venv-video/` can be deleted too; do not commit it.

## How the script works

- **Frame by frame, not screen recording.** The script sets the page to an exact state, takes one screenshot, moves a tiny step, and repeats (30 screenshots per second of video). Scrolling, cursor movement and typing are therefore perfectly smooth and the result is identical every run, however slow the computer is.
- **Viewport** 1280×720 at `device_scale_factor=1.5`, so screenshots are 1920×1080. Light colour scheme, so the site looks like default LinkedIn.
- **Overlay** (`OVERLAY_JS`) injects three elements into the page: the subtitle box, a black arrow cursor and a blue click ripple. They are added only in the recording browser, never to the website.
- **Helpers:** `caption()` sets the subtitle, `move()` glides the cursor, `click()` scrolls the target into view, moves the cursor, shows the ripple and clicks, `type_text()` types one character per frame (`per_frame=2` for longer text), `comment()` types and posts a comment, `scroll()` eases the page or the profile iframe, `card_frames()` shows a title card.
- **Encoding:** the bundled ffmpeg encodes with `libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart` (plays in QuickTime, PowerPoint, Keynote, browsers and phones).

### Site elements the script relies on

If these change in `../index.html`, update the script too.

| Selector | Element |
| --- | --- |
| `.start-opts [data-act="compose:article"]`, `#comp-title`, `#comp-t`, `#comp-post` | "Write article" composer |
| `#post-<id>` | A feed post (`wf1`, `eq1`, `do1`, `tp1`, `do2`…) |
| `[data-like="<id>"]` | Like button on a post |
| `#in-<id>`, `[data-send="<id>"]` | Comment box and its Post button |
| `[data-reply]`, `[data-clike="<id>:<n>"]` | Reply and Like on a comment |
| `.cg-btn` | "Congratulate Earth Quake" button |
| `.me-name` | Dr. Ought's name in the left card (opens her profile) |

## How to change things

- **Subtitles:** edit the strings passed to `caption(...)` and the `sections` list. Two lines fit comfortably; keep each under about 110 characters.
- **Dr. Ought's own post and comments:** edit the `type_text(...)` and `comment(...)` strings.
- **Pacing:** `HOLD` (seconds a subtitle stays still, default 3.4), the `secs` argument of `scroll()`/`move()`, and `per_frame` in `type_text()`.
- **Resolution:** `viewport` and `device_scale_factor`, plus the `scale=` filter in the ffmpeg command. For a 9:16 phone version, use a 390×844 viewport with `device_scale_factor=3` and change the scale to `1170:2532`. Check that the mobile layout shows the targeted buttons first.
- **New segment:** copy a block such as section 7, change the post id, subtitle and comment.

## Adding sound

The video is silent so it works in a room with a presenter. To add music or voice-over, import the MP4 into iMovie, CapCut or Premiere. If you use music, take it from a source whose licence allows it (for example the YouTube Audio Library or Pixabay Music) and check the terms for your use.

A simpler alternative to the script is a manual screen recording (QuickTime: File → New Screen Recording, or OBS) with subtitles added in an editor. The script is better for repeatable, perfectly smooth takes.

## Gotchas

- **`net::ERR_CONNECTION_REFUSED`:** the local web server is not running. Start step 2 again.
- **Wrong iframe:** opening a profile changes the hub's URL to `/#dr-ought`, so the script finds the profile frame with `"profiles/dr-ought" in f.url`. Matching only `"dr-ought"` grabs the main page and the profile sections get skipped.
- **Re-rendering:** clicking Like, Reply or Post re-renders the feed, which removes any temporary ids the script adds. Add ids after the click (see the `lr-c` and `mine-eq1` steps).
- **Sticky header:** profile sections scroll to `top - 100` so their headings are not hidden under the profile's own nav bar.
- **Dr. Ought's profile page is static.** The post she writes in the video appears in the feed but not on her profile's Activity section.
- **Nothing persists.** Each run starts from a fresh page, so likes and comments from earlier runs never carry over.
