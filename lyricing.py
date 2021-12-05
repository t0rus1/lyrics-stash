import pandas as pd
import streamlit as st
import store
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder


def render_lyrics_form():

    docs = store.get_stash_stream()

    items = []
    for doc in docs:
        items.append(doc.to_dict())

    df = pd.DataFrame(items)


    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gridOptions = gb.build()    
    
    AgGrid(df)

    return st.form_submit_button(label='Ok')
