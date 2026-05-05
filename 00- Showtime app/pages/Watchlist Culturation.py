import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client
import os
import time 
from pathlib import Path
import sys

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import branding

branding.apply_branding()

st.title("Watchlist Culturation")

#Connect to DB and load watchlist

@st.cache_resource
def create_supabase_client():

    load_dotenv()
    supabase_table = os.getenv("WATCHLIST_TABLE")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your environment.")
    if not supabase_table:
            raise ValueError("WATCHLIST_TABLE must be set in your environment.")

    db_client = create_client(supabase_url, supabase_key)

    return db_client, supabase_table

def load_watchlist():

    db_client, supabase_table = create_supabase_client()

    watchlist=db_client.table(supabase_table).select("*").execute()

    watchlist_df=pd.DataFrame(watchlist.data)

    if watchlist_df.empty :
        return pd.DataFrame(columns=["Nom Francais", "Nom Anglais", "Type", "Lien trailer", "Vu?"])
    else :
        return watchlist_df

def remove_watched_movies(updated_df):
    db_client, supabase_table = create_supabase_client()
    watched_movies = updated_df[updated_df["Vu?"].fillna(False)]

    for _, row in watched_movies.iterrows():
        delete_query = db_client.table(supabase_table).delete()

        if pd.notna(row.get("Nom Francais")) and row.get("Nom Francais") != "":
            delete_query = delete_query.eq("Nom Francais", row["Nom Francais"])
        elif pd.notna(row.get("Nom Anglais")) and row.get("Nom Anglais") != "":
            delete_query = delete_query.eq("Nom Anglais", row["Nom Anglais"])
        else:
            delete_query = delete_query.eq("Lien trailer", row.get("Lien trailer", ""))

        delete_query.execute()

def add_movie_to_watchlist(french_title, english_title, type_logo, trailer):
    db_client, supabase_table = create_supabase_client()
    movie = {
        "Nom Francais": french_title,
        "Nom Anglais": english_title,
        "Type": type_logo,
        "Lien trailer": trailer,
        "Vu?": False
    }
    db_client.table(supabase_table).insert(movie).execute()

watchlist_df = load_watchlist()

st.write("### Watchlist actuelle")

# Allow user to filter either by new movies or old classics
filter_by = st.segmented_control(
    "Type de film", ["🆕 Nouveau Mouvie", "📼 Big classique","Tout"], selection_mode="single",default="Tout"
)

if not watchlist_df.empty:
    if filter_by == "🆕 Nouveau Mouvie":
        mask = watchlist_df["Type"] == "🆕"
    elif filter_by == "📼 Big classique":
        mask = watchlist_df["Type"] == "📼"
    else:
        mask = watchlist_df["Type"].isin(["📼","🆕"])

    edited_df = st.data_editor(
        watchlist_df.loc[mask],
        width='stretch',
        hide_index=True,
        column_config={
            "Vu?": st.column_config.CheckboxColumn(
                "Vu?",
                help="Mark as watched to remove",
                default=False
            )
        },
        disabled=[col for col in watchlist_df.columns if col != "Vu?"]
    )

#We need to keep the entire watchlist in memory with the "Vu?" info filled even with the type filtered
    complete_list_df=pd.concat([watchlist_df.loc[~mask],edited_df]) 
    if st.button("Supp. les films vus"):
        updated_df = complete_list_df[~complete_list_df["Vu?"].fillna(False)] # Remove movies marked as seen
        remove_watched_movies(complete_list_df)
        st.success("Removed watched movies from the list.")
        st.rerun()
else:
    st.warning('Pas de film dans la watchlist. Prière de se ressaisir.', icon="⚠️")

st.write("### Ajouter un film à la watchlist")

french_title = st.text_input("Nom du film en francais", placeholder="Ex: Les Bronzés font du ski")

english_title = st.text_input("Nom du film en anglais", placeholder="Ex: French Fried Vacation")

# Movie type
type = st.selectbox(
        "Type",
        ("🆕 Nouveau Mouvie","📼 Big classique"),
        index=None,
        placeholder="Nouvelle sortie ou classique de culturateur?"
    )

# Associate a logo to movie type, to be displayed in the table
if type=="🆕 Nouveau Mouvie" :
    type_logo="🆕"
elif type=="📼 Big classique" :
    type_logo="📼"

trailer=st.text_input("Lien du trailer", placeholder="Ex: https://www.youtube.com/watch?v=Fm8QaJS65nc")

add=st.button("Ajouter à la watchlist")

if add and (french_title=='' and english_title=='') :# If the movie name isn't given don't add a row
    st.error("Ajoutes le nom du film puto 🫵")
elif add and (french_title in watchlist_df.loc[lambda x: x['Nom Francais']!='']['Nom Francais'].values or english_title in watchlist_df.loc[lambda x: x['Nom Anglais']!='']['Nom Anglais'].values):
    st.error("Ya déjà le film mon gars concentres-toi 🥴")
elif add and (type is None):
    st.error("Renseignes le type de film le san 🙏")
elif add and (french_title !='' or english_title !='') :
    add_movie_to_watchlist(french_title, english_title, type_logo, trailer)
    st.success("Film ajouté bsahtek 👌")
    time.sleep(2)
    st.rerun()
