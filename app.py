import os
import os.path
import re #, requests, subprocess, urllib.parse, urllib.request
#from bs4 import BeautifulSoup
import inspect
import json
from pprint import PrettyPrinter

from apiclient.discovery import build
from google.cloud import firestore

import streamlit as st
from streamlit_player import st_player

from youtube_dl.utils import DownloadError

import downloader

VERSION = '0.01'
MAX_RESULTS = 50
WATCH_STEM='https://www.youtube.com/watch?v='

#pp = PrettyPrinter()
youtube = build('youtube', 'v3', developerKey = 'AIzaSyC-zbUWUw3N4E3nfuNlqNaZob3Iv3nich8')

def test_firestore():
    # Authenticate to Firestore with the JSON account key.
    db = firestore.Client.from_service_account_json("firestore-key.json")

    # Create a reference to the Google post.
    doc_ref = db.collection("pairings").document("mDbxTzqZf4Q") #Μελίνα Ασλανίδου - Ζω Τη Ζωή - Official Music Video

    # Then get the data at that reference.
    doc = doc_ref.get()

    # Let's see what we got!
    st.write("The id is: ", doc.id)
    st.write("The contents are: ", doc.to_dict())



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

    chosen_title = st.session_state.title_radio 
    # dont download title already in the player
    was_just_retrieved = hasattr(st.session_state,'current_playee') and chosen_title == st.session_state.current_playee

    download_url = st.session_state.yt_urls[chosen_title]
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

    # youtube_dl alters some filename chars, so
    # ensure certain disallowed characters in filenames get 
    # substituted in the same way that youtube_dl does them
    scrubbed_title = re.sub(r'[\|/\\]', '_', chosen_title)
    # double quotes become single
    scrubbed_title = re.sub(r'"', "'", scrubbed_title)
    # : becomes -
    scrubbed_title = re.sub(r':', "-", scrubbed_title)

    playee_fn = f'./temp/{scrubbed_title}.mp3'
    if os.path.isfile(playee_fn):
        st.session_state.current_playee = chosen_title
        # place audio player - hopefully the file will be an mp3:
        st.audio(playee_fn, format='audio/ogg')
        st.write(f'Watch video on Youtube {download_url}')
    else:
        st.error(f'Unable to find or play {playee_fn} - the audio player cannot load it due to irregular titling.')
            

##############################################
# START

init_folders()
setup_page()

test_firestore()

youtube = build('youtube', 'v3', developerKey = 'AIzaSyC-zbUWUw3N4E3nfuNlqNaZob3Iv3nich8')

with st.expander("options"):
    results_size = int(st.number_input('max number of results to fetch',min_value=1, max_value=100, value=MAX_RESULTS))
    video_links_only = st.checkbox('get youtube videos links only',value=False, help='check this if you only want to watch videos, as opposed to the normal pairing of audio with lyrics')

with st.form('search_form'):
    music_query = st.text_input("Artist and|or name of song video to search for", key='music_query', help='Artist AND song OR just artist OR just song. To begin a new search, clear this text box and click submit below')    
    if not music_query:
        submit_button = st.form_submit_button('search')
        st.warning('please enter a search term eg Αντώνης Ρέμος')
        st.stop()
    else:
        st.session_state.qry_result = submit_youtube_query(music_query, results_size)
        # inspect search results and extract video urls
        #st.session_state.yt_urls=get_youtube_links(search_results, results_size)

        titles = []
        st.session_state.yt_urls = {}

        for item in st.session_state.qry_result['items']:
            if video_links_only: # eg https://www.youtube.com/watch?v=9i3szgwCXzg
                # write simple youtube link screen (which user may click to watch video in youtube tab)
                st.markdown(f"[{item['snippet']['title']}]({WATCH_STEM}{item['id']['videoId']})")
            else:
                # per usual mode of operating, just write title to a list for presentation below as a list of radiobuttons
                titles.append(item['snippet']['title'])
                #also write to dict of urls keyed on title
                st.session_state.yt_urls[item['snippet']['title']] = f"{WATCH_STEM}{item['id']['videoId']}"

        if not video_links_only:
            # present a radio button list
            st.radio('Choose a title to download and play', titles, key='title_radio')

        submit_button = st.form_submit_button(label='submit', on_click=search_form_callback)
