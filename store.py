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


def get_stash_doc_by_videoId(audio_id):
    # Note: Use of CollectionRef stream() is prefered to get()
    db = get_db()
    docs = db.collection(STASH).where(u'videoId', u'==', audio_id).stream()

    #one value assumed only, so return first 
    for doc in docs:
        return doc.to_dict()
    # empty
    return None

def get_stash_stream():

    db = get_db()
    return db.collection(STASH).stream()

def add_to_stash(video_id, title, native_lyrics=''):

    db = get_db()
    db.collection(STASH).add({
        'videoId': video_id,
        'title': title,
        'lyrics': native_lyrics
    })

def update_stash_lyrics(videoId, lyrics):

    doc = get_stash_doc_by_videoId(videoId)
    if doc is not None:
        db = get_db()
        doc_ref = db.collection(STASH).document(doc.id)
        doc_ref.set({
            'lyrics': lyrics
        })

def add_or_update_stash(video_id, title, native_lyrics=''):

    doc = get_stash_doc_by_videoId(video_id)
    if doc is None:
        add_to_stash(video_id, title, native_lyrics)
    else:
        update_stash_lyrics(doc.videoId, native_lyrics)
