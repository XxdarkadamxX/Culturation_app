from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = PROJECT_ROOT / "Logo sidebar.png"


def apply_branding() -> None:
    return


def render_sidebar() -> None:
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)

    st.sidebar.divider()
    st.sidebar.caption("Navigation")
    st.sidebar.page_link("Accueil.py", label="Accueil", icon="🏠")
    st.sidebar.page_link("pages/Movie Showtimes.py", label="Séances de ciné", icon="🎬")
    st.sidebar.page_link("pages/Culturation Events.py", label="Plans Culturation", icon="🎭")
    st.sidebar.page_link("pages/Watchlist Culturation.py", label="Watchlist", icon="📼")
