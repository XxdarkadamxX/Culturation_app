import streamlit as st
import pandas as pd
from pathlib import Path
import time
import datetime
from datetime import date
from dotenv import load_dotenv
import os
from supabase import Client,create_client
import sys

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import branding

branding.apply_branding()
branding.render_sidebar()

st.title("Plans Culturation")

st.markdown(
    """
    :grey[*Tiens toi au courant des ***plans suggérés par tes culturateurs pref*** et surtout ramènes toi ou ça va mal finir igo*]"""
)
st.divider()



@st.cache_resource
def create_supabase_client():

    load_dotenv()
    supabase_table = os.getenv("EVENTS_TABLE")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your environment.")
    if not supabase_table:
            raise ValueError("EVENTS_TABLE must be set in your environment.")

    db_client = create_client(supabase_url, supabase_key)

    return db_client, supabase_table

def load_non_expired_events():

    # Load all culturation events that have are still available 
    # (end date before page load), and delete others

    db_client, supabase_table = create_supabase_client()

    db_client.table(supabase_table).delete().lt("Date de fin",date.today()).execute()

    events=db_client.table(supabase_table).select("*").execute()

    events_df = pd.DataFrame(events.data)

    if events_df.empty :
        return pd.DataFrame(['Nom','Type','Lieu','Date de fin','Certification','Prix','Lien de reservation'])        
    else :
        return events_df

def add_event_to_list(name, type, lieu, end_date,certif,price,res_url):
    db_client, supabase_table = create_supabase_client()
    event = {
        "Nom": name,
        "Type": type,
        "Lieu": lieu,
        "Date de fin": end_date.isoformat(),
        "Certification": certif,
        "Prix": price ,
        "Lien de reservation": res_url
    }

    db_client.table(supabase_table).insert(event).execute()

plan_cult_df = load_non_expired_events() 

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
    sorted_df = plan_cult_df.sort_values(by='Date de fin', ascending=True)
    sorted_df['Date de fin'] = sorted_df['Date de fin'].apply(date_to_french)  # write dates in words for lisibility

    st.dataframe(
        sorted_df[['Nom','Type','Lieu','Date de fin','Certification','Prix','Lien de reservation']],
        hide_index=True)

else:
    st.warning("Pas de plan culturation à proposer. Le Culture Club s'excuse grandement pour ce lackage.", icon="⚠️")

st.write("### Ajouter un plan culturation")

nom = st.text_input("Nom", placeholder="Ex: Nocturne du Louvre")

type = st.selectbox(
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

if add and (end_date<date.today()):
    st.error("Le plan est plus dispo, vérifie la date")
elif add and (nom in plan_cult_df['Nom'].values):
    st.error("Ya deja le plan mon gars concentres-toi")
elif add and (nom not in plan_cult_df['Nom'].values):
    add_event_to_list(nom, type,lieu,end_date,certif,prix,res_url)
    st.success("Plan ajouté bsahtek👌")
    time.sleep(2)
    st.rerun()
