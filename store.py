import re
from google.cloud import firestore
#import streamlit as st

#name of collection
STASH='stash'

def get_db():
    return firestore.Client.from_service_account_json("./secrets/firestore-key.json")

# def test_firestore():
#     # Authenticate to Firestore with the JSON account key.
#     db = get_db()

#     # Create a reference to the Google post.
#     doc_ref = db.collection(STASH).document("mDbxTzqZf4Q") #Μελίνα Ασλανίδου - Ζω Τη Ζωή - Official Music Video

#     # Then get the data at that reference.
#     doc = doc_ref.get()

#     # Let's see what we got!
#     st.write("The id is: ", doc.id)
#     st.write("The contents are: ", doc.to_dict())


def get_doc_snapshot_by_videoId(audio_id):
    # Note: Use of CollectionRef stream() is prefered to get()
    db = get_db()
    col_ref = db.collection(STASH)
    results = col_ref.where(u'videoId', u'==', audio_id).get()

    #one value assumed only, so return first 
    for item in results:
        return item

    # empty
    return None

def get_stash_stream():

    db = get_db()
    return db.collection(STASH).stream()

def add_to_stash(video_id, artist_and_title, native_lyrics=''):

    # extract the artist from title
    # Xristos Dantis - Den Axizei
    dash_pos = artist_and_title.find(' - ')
    if dash_pos != -1:
        artist = artist_and_title[0:dash_pos]
        title = artist_and_title[len(artist)+3:]
    else:
        artist=''
        title= artist_and_title

    db = get_db()
    db.collection(STASH).add({
        'artist': artist,
        'title': title,
        'lyrics': native_lyrics,
        'videoId': video_id,
        'translation': ''
    })

def update_stash_lyrics(videoId, lyrics):

    item = get_doc_snapshot_by_videoId(videoId)

    db = get_db()
    col_ref = db.collection(STASH)
    doc = col_ref.document(item.id)

    doc.update({'lyrics': lyrics})

def add_or_update_stash(video_id, artist_and_title, native_lyrics=''):

    doc = get_doc_snapshot_by_videoId(video_id)
    if doc is None:
        add_to_stash(video_id, artist_and_title, native_lyrics)
    else:
        update_stash_lyrics(doc.videoId, native_lyrics)
