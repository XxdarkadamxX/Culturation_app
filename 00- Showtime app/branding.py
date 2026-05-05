from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = PROJECT_ROOT / "Logo sidebar.png"


def apply_branding() -> None:
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), width='stretch')
        st.logo(str(LOGO_PATH), size="large", icon_image=str(LOGO_PATH))
        
