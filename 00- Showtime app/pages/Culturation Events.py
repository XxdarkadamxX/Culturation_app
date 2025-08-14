import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.title("Plans Culturation")

plan_cult_csv_path = Path(r"C:\Users\adamh\OneDrive\Bureau\Cinema showtime app\Cinema-showtimes-app\plan_culturation.csv")

plan_cult_df = pd.read_csv(plan_cult_csv_path)

st.write("### Plans culturation")

if not plan_cult_df.empty:
    
    st.dataframe(
        plan_cult_df,
        hide_index=True)

else:
    st.warning("Pas de plan culturation à proposer. Le Culture Club s'excuse grandement pour ce lackage.", icon="⚠️")

st.write("### Ajouter un plan culturation")

nom = st.text_input("Nom", placeholder="Ex: Nocturne du Louvre")

type_ = st.selectbox(
        "Type",
        ("Exposition/Musée","Festival","Théatre","Event musique","Plan Grrr"),
        index=None,
        accept_new_options=True,
        placeholder="Ex: Exposition/Musée"
    )

lieu=st.text_input("Lieu", placeholder="Ex: Musée du Louvre")

prix= st.text_input("Prix", placeholder="Ex: 10e en -26ans / 25e pr les 👴")

certif = st.selectbox(
        "Certification CC",
        ("CATUESAMERE ❤️","CAPASSE 🤷‍♂️","CAPUESAMERE 🤮"),
        index=None,
        placeholder="Qu'en a pensé la team ?"
    )

end_date=st.date_input("Date de fin")
res_url=st.text_input("Lien de reservation", placeholder="https://www.louvre.fr/expositions-et-evenements/evenements-activites/les-nocturnes-du-mercredi-et-du-vendredi")

add=st.button("Ajouter le plan")

if add and (nom in plan_cult_df['Nom'].values):
    st.error("Ya deja le plan mon gars concentres-toi")
elif add and (nom not in plan_cult_df['Nom'].values):
    plan_cult_df.loc[len(plan_cult_df)] = [nom, type_,lieu,prix,certif,end_date,res_url]
    plan_cult_df.to_csv(plan_cult_csv_path, index=False)
    st.success("Plan ajouté bsahtek")
    time.sleep(2)
    st.rerun()
