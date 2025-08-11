import streamlit as st
import pandas as pd
from pathlib import Path

st.write("Culturation watchlist")

watchlist_csv_path = Path(r"C:\Users\adamh\OneDrive\Bureau\Cinema showtime app\Cinema-showtimes-app\watchlist_culturation_copy.csv")

watchlist_df = pd.read_csv(watchlist_csv_path)



if not watchlist_df.empty:
    st.write("### Current watchlist")

    edited_df = st.data_editor(
        watchlist_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Watched": st.column_config.CheckboxColumn(
                "Watched",
                help="Mark as watched to remove",
                default=False
            )
        },
        disabled=[col for col in watchlist_df.columns if col != "Watched"]  # make all other columns read-only
    )

    if st.button("Remove watched movies"):
        updated_df = edited_df[~edited_df["Watched"].fillna(False)]
        updated_df.to_csv(watchlist_csv_path, index=False)
        st.success("Removed watched movies from the list.")
        st.rerun()
else:
    st.write("No movies in your watchlist.")

st.write("Add a movie")

french_title = st.text_input("Nom du film en francais", placeholder="Ex: Les Bronzés font du ski")

english_title = st.text_input("Nom du film en anglais", placeholder="Ex: French Fried Vacation")

trailer=st.text_input("Lien du trailer", placeholder="Ex: https://www.youtube.com/watch?v=Fm8QaJS65nc")

add=st.button("Add movie")

if add and (french_title=='' and english_title=='') :# If the movie name isn't given don't add a row
    st.error("ajoute le nom du film puto")
elif add and (french_title in watchlist_df['Nom Francais'].values or english_title in watchlist_df['Nom Anglais'].values):
    st.error("ya deja le film mon gars concentres toi")
elif add and (french_title !='' or english_title !='') :
    watchlist_df.loc[len(watchlist_df)] = [french_title, english_title,"",trailer,False]
    watchlist_df.to_csv(watchlist_csv_path, index=False)
    st.rerun()
    st.success("bien joué bg")

st.write(watchlist_df)
