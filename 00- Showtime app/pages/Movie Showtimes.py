import streamlit as st
import pandas as pd
import unicodedata
from pathlib import Path
import datetime
from datetime import date
from streamlit import column_config
import sys
from supabase import Client,create_client

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import branding

branding.apply_branding()
branding.render_sidebar()

import main as scraper_main


st.title("Séances de ciné")

st.markdown(
    """
    :grey[*Tu veux savoir où emmener la miss voir le dernier film de Kad Merad ? Paniques pas poto, le CC a ***rassemblé les séances des cinés les plus stylés de Paname*** pour toi* 😌]"""
)
st.divider()


#Connect to DB and load scrapped movies

SOURCE_LABELS = {
    "UGC_SUPABASE_TABLE": "UGC",
    "PCC_SUPABASE_TABLE": "Paris Cinema Club",
    "DULAC_SUPABASE_TABLE": "Dulac",
}

@st.cache_resource
def create_supabase_client():
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]

    if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your secrets.")

    db_client = create_client(supabase_url, supabase_key)

    return db_client

def load_scraped_movies(table_list):

    db_client = create_supabase_client()

    all_showtimes = pd.DataFrame(columns=['movie','cinema','showtime_day','nb_showings','showtimes'])
    latest_dates_by_source = {}

    for cinema in table_list :
        supabase_table = st.secrets[cinema]

        if not supabase_table:
            raise ValueError(f'{cinema} must be set in your secrets')
        
        cinema_showtimes = (db_client
                             .table(supabase_table)
                             .select("movie, cinema, showtime_day, nb_showings, showtimes")
                             .execute()
                             )
    
        cinema_df = pd.DataFrame(cinema_showtimes.data)
        all_showtimes = pd.concat([all_showtimes, cinema_df], ignore_index=True)

        if not cinema_df.empty and 'showtime_day' in cinema_df.columns:
            latest_dates_by_source[cinema] = cinema_df['showtime_day'].max()
        else:
            latest_dates_by_source[cinema] = None

    if all_showtimes.empty :
            raise ValueError('No showtimes found !')
    
    return all_showtimes.loc[
        lambda x: pd.to_datetime(x.showtime_day, errors='coerce').dt.date >= date.today()
    ], latest_dates_by_source # we only need future showings

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

def format_latest_date(value):
    if value is None or pd.isna(value):
        return "indisponible"
    return date_to_french(str(pd.to_datetime(value).date()))    

table_list=['UGC_SUPABASE_TABLE','PCC_SUPABASE_TABLE','DULAC_SUPABASE_TABLE']
 
showtimes_df, latest_dates_by_source = load_scraped_movies(table_list)

st.write("### Programmation de la semaine")

# Add a button to refresh the showtime programs 
col1, col2, col3 = st.columns([1, 1, 1])
with col1: 
     st.info(
    "Disclaimer: Dernières séances disponibles par groupe de cinema\n"
    + "\n".join(
        f"- {SOURCE_LABELS.get(source_key, source_key)}: {format_latest_date(latest_dates_by_source.get(source_key))}"
        for source_key in table_list
    )
    )
with col3:
    st.write("*Prog du* " + str(min(showtimes_df['showtime_day']))+" *-* "+str(max(showtimes_df['showtime_day'])))
    if st.button("Charger la prog de la semaine"):
        with st.spinner("Mise à jour des programmes en cours..."):
            scraper_main.run_pipeline()

        st.success("Prog chargés jusqu'au " + str(max(showtimes_df['showtime_day'])))
        st.rerun()

shows_available = showtimes_df['movie'].unique() # All movies available
cinemas_available = showtimes_df['cinema'].unique() # All cinemas available

# Allow user to filter either by date (with pills) or by movie name (with a dropdown)
filter_by = st.segmented_control(
    "Recherche par", ["Date", "Film"], selection_mode="single",default="Date"
)


dates_raw = showtimes_df['showtime_day'].unique()
dates = [date_to_french(d) for d in dates_raw]

# si on filtre par date
if filter_by=="Date":

    dates_selection = st.pills("Selectionner une date", dates, selection_mode="single")
    
    cine_selection = st.selectbox(
        "Selectionner un cinema",
        cinemas_available,
        index=None,
        placeholder="On se pète où ?"
        )
    if not dates_selection:
        st.info(' Selectionner une date pour voir le programme', icon="🗓️")
    else:
        # Convert selected French dates back to raw date strings for filtering
            selected_raw_dates = [d for d, f in zip(dates_raw, dates) if f in dates_selection]
        # Prepare DataFrame for display
            # If no cinema is selected display all showtimes
            if cine_selection is None:
                df_display = showtimes_df.loc[
                showtimes_df['showtime_day'].isin(selected_raw_dates) 
                ].copy()

            # If a cinema is selected display the corresponding showtimes
            else: 
                df_display = showtimes_df.loc[
                showtimes_df['showtime_day'].isin(selected_raw_dates) & showtimes_df['cinema'].str.contains(cine_selection) 
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
                width='stretch',
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
                width='stretch',
                hide_index=True,
                column_config=col_config if col_config else None
            )


# Then we get the movies from the watchlist
db_client = create_supabase_client()

watch_list_supabase_table = st.secrets["WATCHLIST_TABLE"]

watchlist=db_client.table(watch_list_supabase_table).select("*").execute()

watchlist_df=pd.DataFrame(watchlist.data)

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

st.write("###Films de la watchlist culturation en salle:")
st.dataframe(
                available_in_watchlist[['Nom Francais','Nom Anglais','Showtime Days','Type','Lien trailer']],
                width='stretch',
                hide_index=True
            )





