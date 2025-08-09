import streamlit as st
import pandas as pd
from pathlib import Path

st.write("Showtimes")

showtimes_csv_path = Path(r"C:\Users\adamh\OneDrive\Bureau\Cinema showtime app\Cinema-showtimes-app\combined_showtimes.csv")

showtimes_df = pd.read_csv(showtimes_csv_path)

st.write(showtimes_df)


st.write("culturation watchlist")

watchlist_csv_path = Path(r"C:\Users\adamh\OneDrive\Bureau\Cinema showtime app\Cinema-showtimes-app\watchlist_culturation.csv")

# try:
watchlist_df = pd.read_csv(watchlist_csv_path)
# st.write(watchlist_df)

#     if showtimes_df is not None:
#         # Get unique movies from showtimes
shows_available = showtimes_df['movie'].unique()
st.write("Available movies in showtimes:")
st.write(shows_available)
        
#         # Find movies in watchlist that are available in showtimes
available_in_watchlist = watchlist_df[
    watchlist_df['Nom Anglais'].isin(shows_available) | watchlist_df['Nom Francais'].isin(shows_available)
]
st.write("Movies from watchlist that are available:")
st.write(available_in_watchlist)







