# UGC V2

First version of a new UGC scraper based on the cinema-page endpoint:

`https://www.ugc.fr/showingsCinemaAjaxAction!getShowingsForCinemaPage.action?cinemaId={id}&date={YYYY-MM-DD}`

Current approach:

- discover Paris UGC cinemas from the public UGC cinemas listing page
- fetch one cinema page per date
- parse films and showtimes from the returned HTML
- save the result to `ugc_cinema_showtimes_v2.json`

Notes:

- this is an initialization pass, so the film-block parsing uses flexible selectors
- if UGC changes the cinema-page HTML, `parse_film_blocks()` will need adjustment
- this version is not yet wired to Supabase
