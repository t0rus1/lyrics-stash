import pandas as pd
import streamlit as st
from appconfig import settings
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
    df = df[['artist','title','videoId','snips','lyrics','translation']]


    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_selection(selection_mode='single', use_checkbox=True)

    # allow lyrics and translation to be editted
    # gb.configure_column('lyrics', editable=True)
    # gb.configure_column('translation', editable=True)

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
        cur_title = data['selected_rows'][0]['title']
        cur_artist = data['selected_rows'][0]['artist']
        cur_snips = data['selected_rows'][0]['snips']
        cur_videoId = data['selected_rows'][0]['videoId']
        cur_lyrics = data['selected_rows'][0]['lyrics']
        new_lyrics = st.text_area('🖊️ Lyrics - edit and | or sing along!',value=cur_lyrics, key='lyrics_text', height=400)
        #
        # put player here, after piecing together snips from firestore
        #
        if cur_snips > 0:
            with st.spinner('Preparing audio for playback...'):
                audio_to_play = store.piece_together_snips(cur_videoId, cur_snips)
            st.audio(audio_to_play, format='audio/ogg')
        else:
            st.write(f'No audio was stored for this song by {cur_artist} ({cur_title})')


        # save changes if reqd
        if new_lyrics != cur_lyrics:
            store.update_stash_lyrics(cur_videoId,new_lyrics)

        st.write(settings['LYRICS_SEARCH_LINK'])
        
        return st.form_submit_button(label="Save lyrics / Change song", help = 'Click to save lyrics changes, change selection or, remove selection then click to reset.')
    else:
        st.write('Select ☑️ a song above, then click the button below')

    return st.form_submit_button(label="Play / Edit selected song Lyrics", help="To play and or edit lyrics, select a row then click here")
