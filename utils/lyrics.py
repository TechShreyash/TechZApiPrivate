import lyricsgenius as lg

api_key = "3w1IXc4ipZ2D7Ef3g2dogPVXnr2VBeUhBqzn5Vr6D_wQVzFFsHRDo_ycV7f8hYwT"

y = lg.Genius(
    api_key,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True,
)
y.verbose = False


async def get_lyrics(query: str):
    x = y.search_song(query, get_full_info=False)
    return {"success": "True", "results": x.lyrics}
