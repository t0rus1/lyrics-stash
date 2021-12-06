import pandas as pd
import streamlit as st
import store
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode

def render_lyrics_form():

    docs = store.get_stash_stream()

    items = []
    for doc in docs:
        items.append(doc.to_dict())

    df = pd.DataFrame(items)
    # order the columns this way
    df = df[['artist','title','lyrics','videoId','translation']]


    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_selection(selection_mode='single', use_checkbox=True)

    # allow lyrics and translation to be editted
    gb.configure_column('lyrics', editable=True)
    gb.configure_column('translation', editable=True)

    gridOptions = gb.build()    
    
    data = AgGrid(
        df, 
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )
    if len(data['selected_rows'])>0: 
        #st.write(data['selected_rows'][0])
        cur_videoId = data['selected_rows'][0]['videoId']
        cur_lyrics = data['selected_rows'][0]['lyrics']
        new_lyrics = st.text_area('lyrics',value=cur_lyrics, key='lyrics_text')
        if new_lyrics != cur_lyrics:
            print('saving new lyrics...')
            store.update_stash_lyrics(cur_videoId,new_lyrics)
        return st.form_submit_button(label="Update lyrics",)

    return st.form_submit_button(label="Submit", help="To edit lyrics, select a row then click here")
