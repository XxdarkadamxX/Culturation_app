import streamlit as st
import pandas as pd
from pathlib import Path
import time
from dotenv import load_dotenv
from supabase import Client, create_client
import os

st.title("Watchlist Culturation")

#Connect to DB and load watchlist

def load_watchlist():

    load_dotenv()
    supabase_table = os.getenv("WATCHLIST_TABLE")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your environment.")

    db_client=create_client(supabase_url, supabase_key)

    watchlist_df=db_client.table(supabase_table).select("*").execute()

    return pd.DataFrame(watchlist_df.data)

# def save_showtimes(self, showtimes_data: Dict[str, Any]) -> int:
#         """
#         Write Dulac showtimes directly to Supabase database.

#         Existing rows for the fetched dates are removed first to avoid duplicates.

#         Returns:
#             Number of records written
#         """
#         records = self.flatten_showtimes_format(showtimes_data)
#         if not records:
#             print("No Dulac showtime records to write to Supabase.")
#             return 0

#         supabase = self.create_supabase_client()

#         supabase.table(self.supabase_table).delete().neq("movie", 0).execute()

#         batch_size = 500
#         inserted_count = 0

#         for i in range(0, len(records), batch_size):
#             batch = records[i:i + batch_size]
#             supabase.table(self.supabase_table).insert(batch).execute()
#             inserted_count += len(batch)

#         print(f"Wrote {inserted_count} records to Supabase table '{self.supabase_table}'.")
#         return inserted_count




# watchlist_csv_path = Path(__file__).parent.parent.parent / "watchlist_culturation.csv"
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
        use_container_width=True,
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
        updated_df.to_csv(watchlist_csv_path, index=False)
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
elif add and (french_title in watchlist_df['Nom Francais'].values or english_title in watchlist_df['Nom Anglais'].values):
    st.error("Ya déjà le film mon gars concentres-toi 🥴")
elif add and (type is None):
    st.error("Renseignes le type de film le san 🙏")
elif add and (french_title !='' or english_title !='') :
    watchlist_df.loc[len(watchlist_df)] = [french_title, english_title,type_logo,trailer,False]
    watchlist_df.to_csv(watchlist_csv_path, index=False)
    st.success("Film ajouté bsahtek 👌")
    time.sleep(2)
    st.rerun()
