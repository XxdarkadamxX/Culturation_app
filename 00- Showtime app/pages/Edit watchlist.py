import streamlit as st
import pandas as pd
from pathlib import Path

st.write("Culturation watchlist")

watchlist_csv_path = Path(r"C:\Users\adamh\OneDrive\Bureau\Cinema showtime app\Cinema-showtimes-app\watchlist_culturation_copy.csv")

watchlist_df = pd.read_csv(watchlist_csv_path)

st.write(watchlist_df)


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
    watchlist_df.loc[len(watchlist_df)] = [french_title, english_title,"",trailer]
    watchlist_df.to_csv(watchlist_csv_path, index=False)
    st.success("bien joué bg")

st.write(watchlist_df)
