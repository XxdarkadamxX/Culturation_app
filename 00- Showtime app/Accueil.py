from pathlib import Path
import sys

import streamlit as st

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import branding

branding.render_sidebar()

st.write(
    "Salut les culturateurs. Vous voilà dans l'antre de la culturation elle-même: "
    "Ici vous pourrez voir les différents programmes que nous avons pu vous cook ainsi "
    "que voir les séances de cinéma dans Paris. Plus d'excuse donc pour ne pas sortir de chez vous. "
    "Ps: Les culturatrices ajoutez moi sur snap @admmharzi 😉"
)

PROJECT_ROOT = APP_ROOT.parent
gif_path = PROJECT_ROOT / "Accueil.gif"
logo_path = PROJECT_ROOT / "Logo accueil.png"

if gif_path.exists():
    st.image(str(gif_path), width='stretch')

col1, col2 = st.columns([2, 1], vertical_alignment="center")
with col2:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
