""""Trending reels" preview for a destination, using embedded YouTube Shorts.

Dynamic when YOUTUBE_API_KEY is set in .env - searches "<city> travel food"
via the YouTube Data API (mcp_tools/youtube.py) and shows the top short
videos. Without a key, falls back to a small static demo set (Milan only).

Self-contained and safe to remove if we don't like it - delete this file and
the single `render_destination_reels(...)` call + its import in app.py.
"""

import streamlit as st

from travel_planner.mcp_tools.youtube import search_short_videos

# Fallback shown when YOUTUBE_API_KEY isn't configured, so the demo still
# works for Milan out of the box.
DEMO_REELS: dict[str, list[dict[str, str]]] = {
    "Milan": [
        {"id": "-qqdEm3P5H4", "title": "The city of fashion"},
        {"id": "g0pMLYjhIBg", "title": "The gelato artist of Milan"},
        {"id": "MXHrYXqjoiw", "title": "Aperitivo & street food"},
        {"id": "crwFhcYjF_A", "title": "Best fruit sorbet in town"},
    ],
}


@st.cache_data(ttl=3600, show_spinner=False)
def _reels_for_city(city: str) -> list[dict[str, str]]:
    videos = search_short_videos(f"{city} travel food", max_results=4)
    return videos or DEMO_REELS.get(city, [])


def render_destination_reels(city: str) -> None:
    """Show a horizontal row of autoplaying short video previews for `city`."""
    if not city:
        return

    reels = _reels_for_city(city)
    if not reels:
        return

    st.markdown(f"#### 🎬 Trending in {city}")

    cards = "".join(
        f"""
        <div class="reel-card">
            <iframe
                src="https://www.youtube.com/embed/{reel['id']}?autoplay=1&mute=1&loop=1&playlist={reel['id']}&controls=0&modestbranding=1&rel=0&playsinline=1"
                allow="autoplay; encrypted-media"
                allowfullscreen
                loading="lazy"
            ></iframe>
            <div class="reel-caption">{reel['title']}</div>
        </div>
        """
        for reel in reels
    )

    st.markdown(
        f"""
        <style>
        .reel-row {{
            display: flex;
            gap: 14px;
            overflow-x: auto;
            padding: 6px 2px 18px 2px;
            scroll-snap-type: x mandatory;
        }}
        .reel-card {{
            position: relative;
            flex: 0 0 auto;
            width: 180px;
            aspect-ratio: 9 / 16;
            border-radius: 16px;
            overflow: hidden;
            background: #1e293b;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            scroll-snap-align: start;
        }}
        .reel-card iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        .reel-caption {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 8px 10px;
            font-size: 12px;
            color: #f1f5f9;
            background: linear-gradient(to top, rgba(0,0,0,0.75), transparent);
        }}
        </style>
        <div class="reel-row">{cards}</div>
        """,
        unsafe_allow_html=True,
    )
