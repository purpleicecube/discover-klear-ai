"""
Discover Klear.ai — Streamlit show-and-tell wrapper.

This is intentionally thin: it loads the visual prototype HTML, inlines the
image assets as base64 (so the deploy is one self-contained file with no
extra static-serving config), and renders it inside a Streamlit component
with all default Streamlit chrome hidden.

No business logic, no state machine — the funnel logic comes later.
"""

import base64
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Discover Klear.ai",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit's default chrome so the prototype fills the page.
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
        .stApp { background: #0e0c2a; }
    </style>
    """,
    unsafe_allow_html=True,
)

APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"


def b64(path: Path, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


# Map the prototype's original relative paths -> inline data URIs so the embedded
# HTML can resolve image references inside the iframe srcdoc (which has no base URL).
asset_map = {
    "../../04_Resources/klearai-logo-circle.png":
        b64(ASSETS / "klearai-logo-circle.png", "image/png"),
    "../../04_Resources/edff4220-ef49-439a-b928-7b647f4530c6.png":
        b64(ASSETS / "edff4220-ef49-439a-b928-7b647f4530c6.png", "image/png"),
}

html = (APP_DIR / "index.html").read_text(encoding="utf-8")
for src, datauri in asset_map.items():
    html = html.replace(src, datauri)

# height=900 is comfortable on most laptop screens; the prototype's scroll-snap
# handles slide navigation inside the iframe.
st.components.v1.html(html, height=900, scrolling=True)
