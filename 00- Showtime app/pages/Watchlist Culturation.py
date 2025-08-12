import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.title("Watchlist Culturation")

watchlist_csv_path = Path(__file__).parent.parent.parent / "watchlist_culturation.csv"
watchlist_df = pd.read_csv(watchlist_csv_path)

st.write("### Watchlist actuelle")

if not watchlist_df.empty:

    edited_df = st.data_editor(
        watchlist_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Vu?": st.column_config.CheckboxColumn(
                "Vu?",
                help="Mark as watched to remove",
                default=False
            )
        },
        disabled=[col for col in watchlist_df.columns if col != "Vu?"]  # make all other columns read-only
    )

    if st.button("Supp. les films vus"):
        updated_df = edited_df[~edited_df["Vu?"].fillna(False)]
        updated_df.to_csv(watchlist_csv_path, index=False)
        st.success("Removed watched movies from the list.")
        st.rerun()
else:
    st.warning('Pas de film dans la watchlist. Prière de se ressaisir.', icon="⚠️")

st.write("### Ajouter un film à la watchlist")

french_title = st.text_input("Nom du film en francais", placeholder="Ex: Les Bronzés font du ski")

english_title = st.text_input("Nom du film en anglais", placeholder="Ex: French Fried Vacation")

trailer=st.text_input("Lien du trailer", placeholder="Ex: https://www.youtube.com/watch?v=Fm8QaJS65nc")

add=st.button("Ajouter à la watchlist")

if add and (french_title=='' and english_title=='') :# If the movie name isn't given don't add a row
    st.error("Ajoute le nom du film puto")
elif add and (french_title in watchlist_df['Nom Francais'].values or english_title in watchlist_df['Nom Anglais'].values):
    st.error("Ya deja le film mon gars concentres-toi")
elif add and (french_title !='' or english_title !='') :
    watchlist_df.loc[len(watchlist_df)] = [french_title, english_title,"",trailer,False]
    watchlist_df.to_csv(watchlist_csv_path, index=False)
    st.success("Film ajouté bsahtek")
    time.sleep(2)
    st.rerun()
