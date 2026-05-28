"""
Discover Klear.ai — Streamlit show-and-tell wrapper.

Thin wrapper around the prototype HTML: inlines image assets as base64
(so the deploy is self-contained), forces the embedded iframe to fill the
browser viewport (so each 100vh slide really matches the visible area),
and hides all default Streamlit chrome.

Note: the canonical version of this prototype lives on GitHub Pages at
<https://purpleicecube.github.io/discover-klear-ai/> — that's the recommended
URL for share-and-tell. The Streamlit version is best-effort; some things
(notably the intro mp4) won't render inside the iframe srcdoc.
"""

import base64
import re
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Discover Klear.ai",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit's default chrome AND force the embedded iframe to actually
# fill the viewport. Without the iframe override, components.v1.html()'s
# fixed `height` parameter caps the iframe at e.g. 900px, leaving a dark
# navy band below on any monitor taller than that.
st.markdown(
    """
    <style>
        header[data-testid="stHeader"] { display: none; }
        [data-testid="stToolbar"] { display: none; }
        [data-testid="stDecoration"] { display: none; }
        [data-testid="stStatusWidget"] { display: none; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        [data-testid="stAppViewBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
        footer { display: none !important; }
        iframe { border: none !important; display: block; }

        /* Force the embedded prototype iframe to the actual viewport height.
           Targets both the modern (stIFrame testid) and legacy iframe titles
           that Streamlit has used for components.v1.html(). */
        [data-testid="stIFrame"],
        [data-testid="stIFrame"] iframe,
        iframe[title="streamlit_app.iframe"],
        iframe[title="st_iframe"] {
            height: 100vh !important;
            min-height: 100vh !important;
            width: 100% !important;
        }
        .stApp { background: #0e0c2a; }
        html, body { overflow: hidden !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"


def b64(path: Path, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


# MIME types we'll inline. mp4 is intentionally excluded — base64 of the
# 5.8MB intro video would bloat the HTML by ~8MB and slow first paint;
# the video reference is left as a relative URL that won't resolve inside
# the iframe srcdoc, but the visual poster + play button still render fine.
_MIME = {
    "png":  "image/png",
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "gif":  "image/gif",
    "svg":  "image/svg+xml",
    "webp": "image/webp",
}


def auto_inline_assets(html: str, assets_dir: Path) -> str:
    """Find all `./assets/<filename>` refs in HTML and inline as base64 URIs.

    Resilient to the prototype gaining new image assets — no per-file map to
    keep in sync. Files whose extensions aren't in _MIME (e.g. .mp4) are left
    as-is.
    """
    pattern = re.compile(r"\./assets/([\w\-.]+)")
    cache: dict[str, str] = {}

    def replace(m: re.Match) -> str:
        fname = m.group(1)
        if fname in cache:
            return cache[fname]
        path = assets_dir / fname
        ext = path.suffix.lower().lstrip(".")
        mime = _MIME.get(ext)
        if not path.exists() or not mime:
            return m.group(0)  # leave intact
        cache[fname] = b64(path, mime)
        return cache[fname]

    return pattern.sub(replace, html)


def legacy_paths(html: str, assets_dir: Path) -> str:
    """Catch any remaining ../../04_Resources/... refs from earlier HTML versions."""
    legacy = {
        "../../04_Resources/klearai-logo-circle.png":
            (assets_dir / "klearai-logo-circle.png", "image/png"),
        "../../04_Resources/edff4220-ef49-439a-b928-7b647f4530c6.png":
            (assets_dir / "edff4220-ef49-439a-b928-7b647f4530c6.png", "image/png"),
    }
    for src, (path, mime) in legacy.items():
        if src in html and path.exists():
            html = html.replace(src, b64(path, mime))
    return html


html = (APP_DIR / "index.html").read_text(encoding="utf-8")
html = auto_inline_assets(html, ASSETS)
html = legacy_paths(html, ASSETS)

# Initial height — Streamlit needs a number; the CSS above overrides to
# 100vh on first paint and beyond. 1080 is a reasonable first-paint guess
# for desktop monitors.
st.components.v1.html(html, height=1080, scrolling=False)
