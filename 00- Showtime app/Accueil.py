from pathlib import Path
import sys

import streamlit as st

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import branding

branding.apply_branding()
branding.render_sidebar()

st.markdown(
    """
    </style>
    <div style="padding: 0rem 0 0.5rem 0;">
        <div style="
            font-size: 0.70rem;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: #d4af37;
            margin-bottom: 0.45rem;">
            Culturation Club
        </div>
        <div style="
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1.02;
            color: #f3eee7;
            margin-bottom: 0.1rem;
            max-width: 760px;">
            Maintenant on a un site mon gars.
        </div>
        <div style="
            font-size: 0.75rem;
            line-height: 1.6;
            color: rgba(243, 238, 231, 0.8);
            max-width: 1000px;">
            Salut les culturateurs. Eh ouais c'est du sérieux là. Confussio vous a cook un petit site pour voir les différents programmes qu'on a pu vous cook et 
            check les séances de cinéma dans Paris. Plus d'excuse mtn #sortezdechezvous. 
            Ps: Les culturatrices ajoutez moi sur snap @admmharzi 😉
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

PROJECT_ROOT = APP_ROOT.parent
gif_path = PROJECT_ROOT / "visuals/Accueil.gif"
logo_path = PROJECT_ROOT / "visuals/Logo accueil.png"

if gif_path.exists():
    st.image(str(gif_path), width='stretch')

col1, col2 = st.columns([2, 1], vertical_alignment="center")
with col2:
    if logo_path.exists():
        st.image(str(logo_path), width='stretch')

