from pathlib import Path
import sys

import streamlit as st

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import branding

branding.apply_branding()

st.write("Salut les culturateurs. Vous voilÃƒÂ  dans l'antre de la culturation elle-mÃƒÂªme: "
    "Ici vous pourrez voir les diffÃƒÂ©rents programmes que nous avons pu vous cook ainsi "
    "que voir les sÃƒÂ©ances de cinÃƒÂ©ma dans Paris. Plus d'excuse donc pour ne pas sortir de chez vous. "
    "Ps: Les culturatrices ajoutez moi sur snap @admmharzi Ã°Å¸Ëœâ€° ")
