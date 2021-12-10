import pandas as pd
import streamlit as st
from appconfig import settings
import store

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode

def lyrics_form_callback():

    store.update_stash_lyrics(st.session_state.cur_videoId, 
                              st.session_state.lyrics_text, 
                              st.session_state.artist_text, 
                              st.session_state.title_text,
                              st.session_state.translation_text)


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

    # allow these selected columns to be editted
    gb.configure_column('artist', editable=True)
    gb.configure_column('title', editable=True)
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
        cur_title = data['selected_rows'][0]['title']
        cur_artist = data['selected_rows'][0]['artist']
        cur_snips = data['selected_rows'][0]['snips']
        cur_videoId = data['selected_rows'][0]['videoId']
        cur_lyrics = data['selected_rows'][0]['lyrics']
        cur_translation = data['selected_rows'][0]['translation']

        st.session_state.cur_videoId = cur_videoId

        st.write('make changes as required below:')
        col1,col2 = st.columns(2)
        with col1:
            new_lyrics = st.text_area('🖊️ Lyrics',value=cur_lyrics, key='lyrics_text', height=400)
            new_artist = st.text_input('Artist', value=cur_artist, key='artist_text')
        with col2:
            new_translation = st.text_area('🖊️ Translation',value=cur_translation, 
                                key='translation_text', height=400)
            new_title = st.text_input('Title', value=cur_title, key='title_text')

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
        # if new_lyrics != cur_lyrics:
        #     store.update_stash_lyrics(cur_videoId, new_lyrics, cur_artist, cur_title)

        st.write(settings['LYRICS_SEARCH_LINK'])
        
        return st.form_submit_button(label="Save changes and|or Change song", 
                    help = 'Click to save lyrics changes, change selection or, remove selection then click to reset.', 
                    on_click=lyrics_form_callback)
    else:
        st.write('Select ☑️ a song above, then click the button below')

    return st.form_submit_button(label="Play / Edit selected song Lyrics", 
                help="To play and or edit lyrics, select a row then click here")
