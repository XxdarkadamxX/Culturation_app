import streamlit as st
import pandas as pd
from pathlib import Path
import time
import datetime
from datetime import date


st.title("Plans Culturation")

plan_cult_csv_path = Path(__file__).parent.parent.parent / "plan_culturation.csv"

plan_cult_df_w_old_plans = pd.read_csv(plan_cult_csv_path)

# Automatically delete expired plans (plans with a datetime in the past)
plan_cult_df_w_old_plans['end_date_datetime'] = pd.to_datetime(plan_cult_df_w_old_plans['Date de fin'], errors='coerce')
plan_cult_df = plan_cult_df_w_old_plans[plan_cult_df_w_old_plans['end_date_datetime'] >= pd.Timestamp(date.today())].copy()

# Write end dates in french for easier comprehension
mois = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Décembre"
]

def date_to_french(date_str):
    # date_str: "2025-08-11"
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    nom_mois = mois[d.month - 1]

    return f"{d.day} {nom_mois} {d.year}"

st.write("### Liste des plans")

if not plan_cult_df.empty:
    
    # We display the culturation plans sorted by end date
    sorted_df = plan_cult_df.sort_values(by='end_date_datetime', ascending=True)
    sorted_df['Date de fin'] = sorted_df['Date de fin'].apply(date_to_french)  # write dates in words for lisibility

    st.dataframe(
        sorted_df[['Nom','Type','Lieu','Date de fin','Certification','Prix','Lien de reservation']],
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

col1, col2 = st.columns([1, 4])
with col1:
    add=st.button("Ajouter le plan")
with col2:
    if end_date==date.today():
        st.warning("Date de fin = Aujourd'hui : le plan sera supp. demain !",icon="⚠️")
    if end_date<date.today():
        st.warning("Date de fin dans le passé : le plan ne sera pas ajouté !",icon="⚠️")

if add and (nom in plan_cult_df['Nom'].values):
    st.error("Ya deja le plan mon gars concentres-toi")
elif add and (nom not in plan_cult_df['Nom'].values):
    plan_cult_df.loc[len(plan_cult_df)] = [nom, type_,lieu,prix,certif,str(end_date),res_url,None]
    # Exclude 'end_date_datetime' column before saving to CSV if it exists
    save_df = plan_cult_df.drop(columns=['end_date_datetime'], errors='ignore')
    save_df.to_csv(plan_cult_csv_path, index=False)
    st.success("Plan ajouté bsahtek👌")
    time.sleep(2)
    st.rerun()
