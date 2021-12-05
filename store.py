from google.cloud import firestore
import streamlit as st

#name of collection
STASH='stash'

def get_db():
    return firestore.Client.from_service_account_json("./secrets/firestore-key.json")

def test_firestore():
    # Authenticate to Firestore with the JSON account key.
    db = get_db()

    # Create a reference to the Google post.
    doc_ref = db.collection(STASH).document("mDbxTzqZf4Q") #Μελίνα Ασλανίδου - Ζω Τη Ζωή - Official Music Video

    # Then get the data at that reference.
    doc = doc_ref.get()

    # Let's see what we got!
    st.write("The id is: ", doc.id)
    st.write("The contents are: ", doc.to_dict())


def get_lyrics_for_id(audio_id):
    # Note: Use of CollectionRef stream() is prefered to get()
    db = get_db()
    docs = db.collection(STASH).where(u'videoId', u'==', audio_id).stream()

    lyrics = ''
    for doc in docs:
        #print(f'{doc.id} => {doc.to_dict()}')    
        lyrics =  doc.lyrics
        break

    return lyrics

def save_native_lyrics(video_id, title, native_lyrics=''):

    db = get_db()
    db.collection(STASH).add({
        'videoId': video_id,
        'title': title,
        'lyrics:': native_lyrics
    })
