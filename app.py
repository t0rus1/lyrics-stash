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

import downloader
import store
import browsing
import lyricing

VERSION = '0.01'
MAX_RESULTS = 25
OPS_MODE = ('link browsing', 'Collecting music', 'updating lyrics')

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
    st.subheader("Search Youtube for Music:")

def name_and_args():
    ''' inspect function arguments '''
    caller = inspect.stack()[1][0]
    args, _, _, values = inspect.getargvalues(caller)
    return [(i, values[i]) for i in args]

def lyrics_changed():
    print('lyrics changed')
            

def lyrics_form_callback():
    print('lyrics form submitted')

##############################################
# START

init_folders()
setup_page()
#store.test_firestore()

# TODO hide the dev key in streamlit secrets
youtube = build('youtube', 'v3', developerKey = 'AIzaSyC-zbUWUw3N4E3nfuNlqNaZob3Iv3nich8')

with st.expander("Operating mode & other settings"):

    ops_mode = st.radio('mode',OPS_MODE, key='ops_mode', index=1)
    results_size = int(st.number_input('max number of results to fetch',min_value=1, max_value=100, value=MAX_RESULTS))
    video_links_only = ops_mode == OPS_MODE[0] #st.checkbox('get youtube videos links only',value=False, help='check this if you only want to watch videos, as opposed to the normal pairing of audio with lyrics')

with st.form('search_form'):
    if ops_mode == 'updating lyrics':
        # updating lyrics        
        submit_button = lyricing.render_lyrics_form()
    else:
        # browsing and collecting
        submit_button = browsing.browse_and_collect(youtube, video_links_only, results_size)
