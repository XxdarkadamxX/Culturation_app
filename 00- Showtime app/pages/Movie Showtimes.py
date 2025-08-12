import streamlit as st
import pandas as pd
import unicodedata
from pathlib import Path
import datetime
from streamlit import column_config
import subprocess
import sys
import os


st.title("Séances de ciné")


# First get the showtimes previously scraped
showtimes_csv_path = Path(__file__).parent.parent.parent / "combined_showtimes.csv"

showtimes_df = pd.read_csv(showtimes_csv_path)

# Add a button to refresh the showtime programs 
col1, col2, col3 = st.columns([1, 1, 1])
with col3:
    st.write("*Prog du* " + str(min(showtimes_df['showtime_day']))+" *-* "+str(max(showtimes_df['showtime_day'])))
    if st.button("Charger la prog de la semaine"):
        # Find the main.py path relative to this Streamlit app
        main_py_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "main.py")
        )

        # Run main.py as a subprocess
        result = subprocess.run(
            [sys.executable, main_py_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            st.success("Prog chargés jusqu'au " + str(max(showtimes_df['showtime_day'])))
        else:
            st.error("Erreur lors de la mise à jour des programmes :\n\n" + result.stderr)

shows_available = showtimes_df['movie'].unique() # All movies available

# Allow user to filter either by date (with pills) or by movie name (with a dropdown)
filter_by = st.segmented_control(
    "Recherche par", ["Date", "Film"], selection_mode="single",default="Date"
)

# French day and month names
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
mois = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Décembre"
]

def date_to_french(date_str,month_only=False):
    # date_str: "2025-08-11"
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    jour = jours[d.weekday()]
    nom_mois = mois[d.month - 1]
    if month_only:
        return f"{jour} {d.day}"
    else : 
        return f"{jour} {d.day} {nom_mois}"

dates_raw = showtimes_df['showtime_day'].unique()
dates = [date_to_french(d) for d in dates_raw]

# si on filtre par date
if filter_by=="Date":

    dates_selection = st.pills("Selectionner une date", dates, selection_mode="single")
    if not dates_selection:
        st.info(' Selectionner une date pour voir le programme', icon="🗓️")
    else:
        # Convert selected French dates back to raw date strings for filtering
            selected_raw_dates = [d for d, f in zip(dates_raw, dates) if f in dates_selection]
        # Prepare DataFrame for display
            df_display = showtimes_df.loc[
                showtimes_df['showtime_day'].isin(selected_raw_dates)
            ].copy()
            # Drop 'showtime_day' column
            if 'showtime_day' in df_display.columns:
                df_display = df_display.drop(columns=['showtime_day'])
            # Rename columns: capitalize all, and special case for 'nb_showings'
            rename_dict = {col: col.capitalize() for col in df_display.columns}
            if 'nb_showings' in df_display.columns:
                rename_dict['nb_showings'] = 'Nb of showings'
            df_display = df_display.rename(columns=rename_dict)
            # Use st.dataframe with column_config to wrap or expand the 'Showtimes' column
            # so that long lists are not truncated visually.

            # If 'Showtimes' column exists, set it to display as a wide, wrapped column
            col_config = {}
            if 'Showtimes' in df_display.columns:
                col_config['Showtimes'] = st.column_config.TextColumn(
                    "Showtimes",
                    width="large",  # or "medium", or a pixel value like 400
                    help="All showtimes for this movie"
                )
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config=col_config if col_config else None
            )
# si on filtre par film
else :
    movie_selection = st.selectbox(
        "Selectionner un film",
        shows_available,
        index=None,
        placeholder="Qu'est-ce que tu veux regarder mon cochon ?"
    )
    if not movie_selection:
        st.info(' Selectionner un film pour voir le programme', icon="🎬")
    else:
        # Prepare DataFrame for display
            df_display = showtimes_df.loc[
                showtimes_df['movie'].str.contains(movie_selection)
            ].copy()
            df_display['Showtime day'] = df_display['showtime_day'].apply(lambda d: date_to_french(d, True))
            # Rename columns: capitalize all, and special case for 'nb_showings'
           
            rename_dict = {col: col.capitalize() for col in df_display.columns}
            rename_dict['nb_showings'] = 'Nb of showings'

            df_display = df_display.rename(columns=rename_dict)
            # Use st.dataframe with column_config to wrap or expand the 'Showtimes' column
            # so that long lists are not truncated visually.

            # If 'Showtimes' column exists, set it to display as a wide, wrapped column
            col_config = {}
            if 'Showtimes' in df_display.columns:
                col_config['Showtimes'] = st.column_config.TextColumn(
                    "Showtimes",
                    width="large",  # or "medium", or a pixel value like 400
                    help="All showtimes for this movie"
                )
            st.dataframe(
                df_display[['Movie','Cinema','Showtime day','Nb of showings','Showtimes']],
                use_container_width=True,
                hide_index=True,
                column_config=col_config if col_config else None
            )


# Then we get the movies from the watchlist
watchlist_csv_path = Path(r"C:\Users\adamh\OneDrive\Bureau\Cinema showtime app\Cinema-showtimes-app\watchlist_culturation.csv")
watchlist_df = pd.read_csv(watchlist_csv_path)
        
# Finally we find movies in watchlist that are available in cinemas

# Remove accents and convert to lowercase so that syntax errors are minimized 
def normalize_str(s):
    if pd.isna(s):
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', str(s))
        if not unicodedata.combining(c)
    ).lower().strip()

# Normalize showtimes movie titles
normalized_shows_available = set(normalize_str(m) for m in shows_available)

# Normalize watchlist columns
watchlist_df['Nom Anglais norm'] = watchlist_df['Nom Anglais'].apply(normalize_str)
watchlist_df['Nom Francais norm'] = watchlist_df['Nom Francais'].apply(normalize_str)

# Only keep movies from watchlist that are in cinemas
available_in_watchlist = watchlist_df[
    watchlist_df['Nom Anglais norm'].isin(normalized_shows_available) |
    watchlist_df['Nom Francais norm'].isin(normalized_shows_available)
]

# Map showtime days (in French) to watchlist entries
showtimes_with_days = showtimes_df.copy()
showtimes_with_days['showtime_day_french'] = showtimes_with_days['showtime_day'].apply(lambda d: date_to_french(d, True))

# Normalize for matching
showtimes_with_days['movie_norm'] = showtimes_with_days['movie'].apply(normalize_str)

# Group showtimes by movie
movie_days_map = (
    showtimes_with_days
    .groupby('movie_norm')
    .apply(lambda df: " / ".join(
        # Sort by the raw date value
        [date_to_french(d, True) for d in sorted(df['showtime_day'].unique())]
    ))
    .to_dict()
)

# Add column to available_in_watchlist
available_in_watchlist['Showtime Days'] = available_in_watchlist.apply(
    lambda row: movie_days_map.get(row['Nom Anglais norm']) 
                or movie_days_map.get(row['Nom Francais norm']),
    axis=1
)

st.write("Films de la watchlist culturation en salle:")
st.dataframe(
                available_in_watchlist[['Nom Francais','Nom Anglais','Showtime Days','Classification','Lien trailer']],
                use_container_width=True,
                hide_index=True
            )





