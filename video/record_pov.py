"""Showcase video from Dr. Ought's point of view: she operates the site herself (cursor, typing,
likes, her own post, corporate-jargon replies), with the same subtitles as before.

usage: record_pov.py BASE_URL FRAMES_DIR OUT_MP4
"""
import math, os, shutil, subprocess, sys
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

BASE, FRAMES, OUT = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
FPS = 30
HOLD = 3.4
shutil.rmtree(FRAMES, ignore_errors=True); os.makedirs(FRAMES)
n = 0
cur = [1000.0, 420.0]   # cursor position in CSS px

OVERLAY_JS = """([t,x,y,r])=>{
 let c=document.getElementById('cap');
 if(!c){c=document.createElement('div');c.id='cap';c.style.cssText='position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:99999;background:rgba(0,0,0,.78);color:#fff;font:600 24px -apple-system,system-ui,Segoe UI,Roboto,Arial,sans-serif;padding:12px 22px;border-radius:10px;max-width:78%;line-height:1.35;text-align:center;box-shadow:0 6px 24px rgba(0,0,0,.25)';document.body.appendChild(c)}
 if(t!==null){c.textContent=t;c.style.display=t?'block':'none'}
 let k=document.getElementById('cur');
 if(!k){k=document.createElement('div');k.id='cur';k.style.cssText='position:fixed;left:0;top:0;z-index:100000;pointer-events:none;width:22px;height:30px';
  k.innerHTML='<svg width="22" height="30" viewBox="0 0 22 30"><path d="M2 2 L2 24 L8 18.5 L12 28 L16 26.2 L12 17 L20 17 Z" fill="#111" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>';document.body.appendChild(k)}
 k.style.transform=`translate(${x-2}px,${y-2}px)`;
 let p=document.getElementById('rip');
 if(!p){p=document.createElement('div');p.id='rip';p.style.cssText='position:fixed;left:0;top:0;z-index:99998;pointer-events:none;border-radius:50%;border:3px solid #0a66c2;background:rgba(10,102,194,.18)';document.body.appendChild(p)}
 if(r>0){const s=8+r*34;p.style.display='block';p.style.width=p.style.height=s+'px';p.style.transform=`translate(${x-s/2}px,${y-s/2}px)`;p.style.opacity=String(1-r)}else{p.style.display='none'}
}"""

def overlay(page, text=None, ripple=0.0):
    page.evaluate(OVERLAY_JS, [text, cur[0], cur[1], ripple])

def shot(page):
    global n
    page.screenshot(path=os.path.join(FRAMES, f"{n:05d}.jpg"), type="jpeg", quality=88)
    n += 1

def hold(page, secs):
    overlay(page)
    for _ in range(int(secs * FPS)):
        shot(page)

def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)

def caption(page, text):
    overlay(page, text)

def scroll(page, target_y, secs, frame=None):
    ctx = frame or page
    y0 = ctx.evaluate("scrollY")
    steps = max(1, int(secs * FPS))
    for i in range(1, steps + 1):
        ctx.evaluate("y=>window.scrollTo(0,y)", y0 + (target_y - y0) * ease(i / steps))
        overlay(page); shot(page)

def move(page, x, y, secs=0.7):
    x0, y0 = cur
    steps = max(1, int(secs * FPS))
    for i in range(1, steps + 1):
        e = ease(i / steps)
        cur[0], cur[1] = x0 + (x - x0) * e, y0 + (y - y0) * e
        overlay(page); shot(page)

def rect(page, sel):
    return page.evaluate("s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height,top:r.top+scrollY}}", sel)

def into_view(page, sel, at=240):
    r = rect(page, sel)
    if r and not (90 < r["y"] < 600):
        scroll(page, max(0, r["top"] - at), 1.2)

def click(page, sel, scroll_first=True):
    if scroll_first:
        into_view(page, sel)
    r = rect(page, sel)
    move(page, r["x"] + min(r["w"] / 2, 60), r["y"] + r["h"] / 2)
    for i in range(1, 7):
        overlay(page, ripple=i / 7); shot(page)
    page.eval_on_selector(sel, "e=>{e.focus&&e.focus();e.click()}")
    page.wait_for_timeout(120)
    overlay(page, ripple=0); shot(page)

def type_text(page, sel, text, per_frame=1):
    page.eval_on_selector(sel, "e=>e.focus()")
    for i in range(0, len(text) + 1, per_frame):
        page.eval_on_selector(sel, "(e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}", text[:i])
        overlay(page); shot(page)
    page.eval_on_selector(sel, "(e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}", text)

def comment(page, pid, text):
    """Dr. Ought writes a comment on a post and publishes it."""
    click(page, f"#in-{pid}")
    type_text(page, f"#in-{pid}", text)
    hold(page, 0.4)
    click(page, f'[data-send="{pid}"]', scroll_first=False)
    hold(page, 1.2)

def top_of(page, sel, offset=70):
    r = rect(page, sel); return max(0, r["top"] - offset) if r else 0

INTRO = """<!doctype html><html><body style="margin:0;height:100vh;display:grid;place-items:center;background:#f4f2ee;font-family:-apple-system,system-ui,Segoe UI,Roboto,Arial,sans-serif">
<div style="text-align:center"><div style="display:inline-flex;align-items:center;gap:18px;font-size:56px;font-weight:700;color:#191919">
<span style="width:72px;height:72px;border-radius:8px;background:#0a66c2;color:#fff;display:grid;place-items:center;font-size:46px;font-weight:800;font-family:Arial">in</span>Disaster Networking</div>
<p style="font-size:26px;color:#555;margin:22px 0 0">%s</p></div></body></html>"""
CARD = """<!doctype html><html><body style="margin:0;height:100vh;display:grid;place-items:center;background:#f4f2ee;font-family:-apple-system,system-ui,Segoe UI,Roboto,Arial,sans-serif">
<div style="max-width:900px;padding:0 40px;text-align:center"><div style="font-size:20px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#0a66c2">%s</div>
<p style="font-size:36px;line-height:1.35;font-weight:600;color:#191919;margin:18px 0 0">%s</p></div></body></html>"""

def card_frames(page, html, secs):
    page.set_content(html)
    for _ in range(int(secs * FPS)):
        shot(page)

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5, color_scheme="light")

    # 1. title cards (unchanged)
    card_frames(page, INTRO % "What happens when destruction learns to speak the language of success?", 3.5)
    card_frames(page, CARD % ("The idea", "We gave real disasters professional profiles, and let them describe their damage the way we are taught to describe our careers."), 5)

    # 2. Dr. Ought logs in and writes her own post
    page.goto(BASE + "/", wait_until="networkidle")
    caption(page, "In the language of personal branding, every outcome becomes a success story.")
    hold(page, 1.2)
    click(page, '.start-opts [data-act="compose:article"]')
    hold(page, 0.5)
    click(page, "#comp-title", scroll_first=False)
    type_text(page, "#comp-title", "Five Seasons Without Rain: My Biggest Growth Story ☀️")
    click(page, "#comp-t", scroll_first=False)
    type_text(page, "#comp-t", "Reservoirs across the region are now running at peak efficiency (12% capacity).\nProud of every community that learned to do more with less. 🙏\n#Leadership #DoingMoreWithLess", per_frame=2)
    hold(page, 0.6)
    click(page, "#comp-post", scroll_first=False)
    hold(page, 2.2)

    # 3. she likes and cheers on Wild Fire
    caption(page, "42,000 hectares burned and 250,000 people displaced become “territory transformed”.")
    scroll(page, top_of(page, "#post-wf1"), 1.6)
    hold(page, 1.2)
    click(page, '[data-like="wf1"]')
    comment(page, "wf1", "Incredible scale, Wild! 🔥 Our dry-season groundwork really paid off. Let’s align on Q4.")

    # 4. Earth Quake's post
    caption(page, "An earthquake becomes a “shaky start to the day”.")
    scroll(page, top_of(page, "#post-eq1"), 1.6)
    hold(page, 1.2)
    click(page, '[data-like="eq1"]')
    hold(page, 1.4)

    # 5. a victim speaks; she answers in corporate jargon
    caption(page, "When a victim speaks, the answer is PR: “Always valuable to hear from key stakeholders.”")
    page.evaluate("()=>{const c=[...document.querySelectorAll('#post-eq1 .c')].find(c=>c.textContent.includes('literally collapsed'));c.id='lr-c';c.querySelector('[data-reply]').id='lr-reply'}")
    scroll(page, top_of(page, "#lr-c", 240), 1.6)
    hold(page, 2.2)
    click(page, "#lr-reply", scroll_first=False)
    into_view(page, "#in-eq1", at=200)
    type_text(page, "#in-eq1", "So sorry to hear this, Local resident 🙏 Have you considered it a chance to rightsize your housing footprint? Open to connect!")
    hold(page, 0.4)
    click(page, '[data-send="eq1"]', scroll_first=False)
    page.evaluate("()=>{const a=[...document.querySelectorAll('#post-eq1 .c')];a[a.length-1].id='mine-eq1'}")
    scroll(page, top_of(page, "#mine-eq1", 360), 1.2)
    hold(page, 2.4)

    # 6. her own Somalia post: she replies to Hank
    caption(page, "A failed rainy season and lost harvests become “key highlights” of a record quarter.")
    scroll(page, top_of(page, "#post-do1"), 1.6)
    hold(page, 1.6)
    comment(page, "do1", "Respectfully, Hank: water is a legacy model. The future is lean. 💧➡️📈")

    # 7. sad news, corporate condolences
    caption(page, "59 lives lost, filed under “operational disruption”.")
    scroll(page, top_of(page, "#post-tp1"), 1.6)
    hold(page, 1.8)
    comment(page, "tp1", "Thoughts with all impacted stakeholders 🙏 That said, 29 districts in one quarter is best-in-class reach. Congrats on the launch, Tye! 👏")

    # 8. the applause
    caption(page, "Likes and reposts reward the framing, not the reality.")
    scroll(page, top_of(page, "#post-do2"), 1.6)
    hold(page, 1)
    click(page, '[data-clike="do2:0"]')
    click(page, '[data-like="do2"]')
    hold(page, 1.6)

    # 9. congratulate Earth Quake, and post the pre-written applause
    scroll(page, 0, 1.4)
    caption(page, "The platform itself prompts us to celebrate: “Congratulate Earth Quake”.")
    hold(page, 1.6)
    click(page, ".cg-btn")
    page.wait_for_timeout(300)
    caption(page, "Applause comes pre-written. Reflection does not.")
    hold(page, 1.6)
    click(page, '[data-send="eq1"]', scroll_first=False)
    hold(page, 2)

    # 10. she visits her own profile
    page.evaluate("window.scrollTo(0,0)")
    click(page, ".me-name")
    page.wait_for_timeout(1500)
    frame = next(f for f in page.frames if "profiles/dr-ought" in f.url)
    frame.wait_for_load_state("networkidle")
    caption(page, "Dr. Ought (drought) is the ideal professional: polished, branded and #HIRING.")
    move(page, 250, 330, 0.8)
    hold(page, HOLD - 0.8)
    sections = [("About", "“Doing more with less”: jargon that hides who is left with less."),
                ("Featured", "Thought leadership turns scarcity into a product to sell."),
                ("Activity", "1.2 million followers for a failed rainy season. Visibility without accountability."),
                ("Experience", "A career measured in KPIs: rivers “mentored into becoming seasonal”."),
                ("Education", "Credentials and distinctions lend authority to destruction.")]
    for name, cap in sections:
        y = frame.evaluate("n=>{const h=[...document.querySelectorAll('h2')].find(x=>x.offsetParent&&x.textContent.trim().startsWith(n));return h?h.getBoundingClientRect().top+scrollY-100:null}", name)
        if y is None:
            continue
        caption(page, cap)
        scroll(page, y, 1.6, frame=frame)
        move(page, 300 + (len(name) * 7) % 200, 330, 0.6)
        hold(page, HOLD - 0.6)

    # 11. closing cards (unchanged)
    card_frames(page, CARD % ("The critique", "Personal branding, corporate jargon and performative success can reduce serious social and environmental harm to metrics, achievements and “impact at scale”."), 6)
    card_frames(page, CARD % ("The question", "Behind every “impact” metric are people and places.<br>What does our professional language leave out?"), 5)
    page.goto(BASE + "/qr.html", wait_until="networkidle")
    caption(page, "Explore the network yourself: scan the QR code.")
    page.evaluate("()=>{const k=document.getElementById('cur');k&&k.remove()}")
    for _ in range(int(4 * FPS)):
        shot(page)
    browser.close()

ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "%05d.jpg"),
                "-vf", "scale=1920:1080:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], check=True)
print(f"{n} frames, {n / FPS:.1f}s -> {OUT}")
