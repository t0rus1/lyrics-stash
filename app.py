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

from appconfig import settings

import downloader
import store
import browsing
import lyricing


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
            "About": f"Music & Lyrics app, v{settings['VERSION']}, by Leon van Dyk 2021"
        }
    )
    st.title('Lyrics Stash🎶')

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
dev_key = st.secrets['developerKey']
youtube = build('youtube', 'v3', developerKey = dev_key)
# lets be able to quickly know what videos are in the stash
st.session_state.videoIds = store.build_stash_cache()
st.write(f"**{len(st.session_state.videoIds)}** songs currently in the collection")

with st.expander("Operating mode & other settings", expanded = True):

    col1,col2 = st.columns(2)
    with col1:
        ops_mode = st.radio('Mode',settings['OPS_MODE'], key='ops_mode', index=1)
    with col2:
        results_size = int(st.number_input('Max results to fetch',min_value=1, max_value=100, value=settings['MAX_RESULTS']))
    video_links_only = ops_mode == settings['OPS_MODE'][0] 

with st.form('search_form'):
    if ops_mode == settings['OPS_MODE'][2]:  
        # Playing & updating
        submit_button = lyricing.render_lyrics_form()
    else:
        # browsing and collecting
        submit_button = browsing.browse_and_collect(youtube, video_links_only, results_size)

