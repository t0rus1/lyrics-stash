import os
import os.path
import re #, requests, subprocess, urllib.parse, urllib.request
#from bs4 import BeautifulSoup
import inspect
import json
#from pprint import pprint

from apiclient.discovery import build
from google.cloud import firestore

import streamlit as st
from streamlit_player import st_player

from youtube_dl.utils import DownloadError

import downloader
import store

VERSION = '0.01'
MAX_RESULTS = 50
WATCH_STEM='https://www.youtube.com/watch?v='

#pp = PrettyPrinter()
youtube = build('youtube', 'v3', developerKey = 'AIzaSyC-zbUWUw3N4E3nfuNlqNaZob3Iv3nich8')

def init_folders():
    ''' ensure needed folders exist'''
    try:
        os.mkdir('./temp')
    except OSError as error:
        pass #print(error)

def setup_page():
    ''' streamlit page config, app title etc'''
    st.set_page_config(
        page_title = "Lyrics Stash",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🎶",
        menu_items={
            "About": f"Music & Lyrics app, v{VERSION}, by Leon van Dyk 2021"
        }
    )
    st.title('Lyrics Stash🎶')
    st.subheader("Search Youtube for Music, then pair with lyrics and translation!")

def name_and_args():
    ''' inspect function arguments '''
    caller = inspect.stack()[1][0]
    args, _, _, values = inspect.getargvalues(caller)
    return [(i, values[i]) for i in args]

def lyrics_changed():
    print('lyrics changed')

def submit_youtube_query(query, results_size):
    request = youtube.search().list(q=query, part='snippet', type='video', maxResults=results_size)
    res = request.execute()
    return res

def search_form_callback():
    ''' executed when form is submitted and before re-run '''

    if st.session_state.music_query == '':
        return

    if not hasattr(st.session_state,'title_radio'):
        return

    chosen_title = st.session_state.title_radio[4:] # skip leading number and period eg '01. Yanni...  '
    chosen_index = int(st.session_state.title_radio[0:2])
    # dont download title already in the player
    was_just_retrieved = hasattr(st.session_state,'current_playee') and chosen_title == st.session_state.current_playee

    download_url = st.session_state.urls_by_title[chosen_title]
    if not was_just_retrieved:
        with st.spinner(f"Downloading and extracting audio from '{chosen_title}' youtube video ..."):
            placeholder = st.empty()
            completion_state = downloader.retrieve(download_url, placeholder)
            if completion_state is not None:
                if isinstance(completion_state, DownloadError):
                    st.error(f'This video ({chosen_title}) may only being played on Youtube itself')
                    print(completion_state)
                elif isinstance(completion_state,FileNotFoundError):
                    st.error('File not found - title may contain disallowed characters...')
                else:
                    st.exception(completion_state)
            else:
                st.markdown(f'** {chosen_title} **')

    audio_id = st.session_state.video_id_by_index[chosen_index]
    audio_fn = f"{audio_id}.mp3"
    audio_fqn = f'./temp/{audio_fn}'

    if os.path.isfile(audio_fqn):
        st.session_state.current_playee = chosen_title
        # place audio player - hopefully the file will be an mp3:
        st.audio(audio_fqn, format='audio/ogg')
        st.write(f'Watch video on Youtube {download_url}')
        # download button
        with open(audio_fqn, 'rb') as f:
            st.download_button('Download', f, file_name=audio_fn, help='Add to your offline collection!')
    else:
        st.error(f'Unable to find or play {audio_fn}') 
            

def lyrics_form_callback():
    return    

##############################################
# START

init_folders()
setup_page()
#store.test_firestore()

youtube = build('youtube', 'v3', developerKey = 'AIzaSyC-zbUWUw3N4E3nfuNlqNaZob3Iv3nich8')

with st.expander("Options"):

    ops_mode = st.radio('mode',('browsing videos', 'Collecting music', 'updating lyrics'), key='ops_mode')
    results_size = int(st.number_input('max number of results to fetch',min_value=1, max_value=100, value=MAX_RESULTS))
    video_links_only = ops_mode == 'browsing videos' #st.checkbox('get youtube videos links only',value=False, help='check this if you only want to watch videos, as opposed to the normal pairing of audio with lyrics')

with st.form('search_form'):
    if ops_mode == 'updating lyrics':
        
        submit_button = st.form_submit_button(label='Update lyrics', on_click=lyrics_form_callback)
    else:
        music_query = st.text_input("Artist and|or name of song video to search for. Submit an empty search to reset.", key='music_query', help='Artist AND song OR just artist OR just song. To begin a new search, clear this text box and click submit below')    
        if not music_query or (hasattr(st.session_state,'current_playee') and st.session_state.current_playee != '') :
            st.session_state.current_playee = ''
            submit_button = st.form_submit_button('search')
            st.warning('please enter a search term eg Αντώνης Ρέμος')
            st.stop()
        else:
            st.session_state.qry_result = submit_youtube_query(music_query, results_size)

            # dump query results to temp file
            pretty_results = json.dumps(st.session_state.qry_result, indent=4)
            with open('./temp/search_results.txt','w') as out:
                out.write(pretty_results)

            titles = []
            st.session_state.urls_by_title = {}
            st.session_state.video_id_by_index = {}

            list_num=1
            for item in st.session_state.qry_result['items']:
                if video_links_only: # eg https://www.youtube.com/watch?v=9i3szgwCXzg
                    # write simple youtube link screen (which user may click to watch video in youtube tab)
                    st.markdown(f"[{item['snippet']['title']}]({WATCH_STEM}{item['id']['videoId']})")
                else:
                    # per usual mode of operating, write numbered title to a list for presentation below as a list of radiobuttons
                    list_prefix = f"{list_num}".zfill(2)
                    titles.append(f"{list_prefix}. {item['snippet']['title']}")
                    #also write to dict of urls keyed on title
                    video_url = f"{WATCH_STEM}{item['id']['videoId']}"
                    st.session_state.urls_by_title[item['snippet']['title']] = video_url
                    st.session_state.video_id_by_index[list_num] = item['id']['videoId']
                    list_num = list_num+1

            if not video_links_only:
                # present a radio button list
                st.radio('Choose a title to convert to audio and play/download', titles, key='title_radio')

            submit_button = st.form_submit_button(label='Get selected audio', on_click=search_form_callback)
