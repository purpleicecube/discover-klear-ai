# Discover Klear.ai

A guided-discovery web app for Klear.ai's Claims Administration product. Visitors watch a short intro video, then optionally engage with an AI avatar ("Christina") who walks them through a quick qualification.

This repo is a **visual prototype hosted on Streamlit** for share-and-review purposes. The full app (state machine, capture model, integrations) lives in the parent `VS_PDOE` workspace at `WS027_FLOW_GUIDED/`.

## Live demo

Two deploy targets pointed at the same source:

| Target | URL | Notes |
| ----- | ----- | ----- |
| **GitHub Pages** | <https://purpleicecube.github.io/discover-klear-ai/> | **Recommended for show-and-tell.** Native HTML at the page level — slides are full-viewport, video plays natively, the LiveAvatar iframe gets proper mic permission. |
| Streamlit Community Cloud | <https://discover-klear-app.streamlit.app/> | Same source, wrapped in a Streamlit component iframe. Works for visual review but layout is constrained to ~900px iframe height; mic permission for the LiveAvatar may not propagate through Streamlit's iframe. |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at <http://localhost:8501>.

## Structure

```
.
├── app.py             ~25-line Streamlit wrapper (hides chrome, embeds prototype)
├── index.html         Self-contained HTML prototype (Barlow font, wave gradient,
│                      avatar placeholder, draggable KlearAssist orb, 5 screens)
├── assets/            Logo + award PNGs (inlined as base64 at runtime)
├── requirements.txt   Just streamlit
└── README.md
```

## How it works

`app.py` reads `index.html`, base64-inlines the small image assets (so the deploy is self-contained with no static-file serving), and renders the result inside `st.components.v1.html()` with all default Streamlit chrome hidden via injected CSS.

## What's the prototype?

5 screens demonstrating the user journey:

1. **Landing** — gradient hero, video poster, "Discover Klear.ai"
2. **Award / Trust** — "Sustainable Work Starts Here" + award badge
3. **Engagement gate** — visitor decides whether to talk to Christina
4. **Christina + qualification** — avatar + "What's holding your program back?" + 3 numbered dark cards
5. **Book meeting** — Microsoft Bookings handoff + email capture

Drag the floating KlearAssist orb anywhere on screen; click it to visit klear.ai.

## License / status

Internal Klear.ai demo. Visual prototype only — no business logic, no live data capture, no integrations wired up.
