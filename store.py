import re,json
from google.cloud import firestore
import streamlit as st
from appconfig import settings

def get_db():
    #return firestore.Client.from_service_account_json("./secrets/firestore-key.json")
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="lyrics-stash")


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


def get_stash_snapshot_by_videoId(audio_id):
    # Note: Use of CollectionRef stream() is prefered to get()
    db = get_db()
    col_ref = db.collection(settings['STASH'])
    results = col_ref.where(u'videoId', u'==', audio_id).get()

    #one value assumed only, so return first 
    for item in results:
        return item

    # empty
    return None

def get_stash_stream():

    db = get_db()
    return db.collection(settings['STASH']).stream()

def add_to_stash(video_id, artist_and_title, native_lyrics, num_snips):

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
    db.collection(settings['STASH']).add({
        'artist': artist,
        'title': title,
        'lyrics': native_lyrics,
        'videoId': video_id,
        'translation': '',
        'snips': num_snips,
    })

def update_stash_lyrics(videoId, lyrics):

    item = get_stash_snapshot_by_videoId(videoId)

    db = get_db()
    col_ref = db.collection(settings['STASH'])
    doc = col_ref.document(item.id)

    doc.update({'lyrics': lyrics})

def add_or_update_stash(video_id, artist_and_title, native_lyrics, num_snips):

    doc = get_stash_snapshot_by_videoId(video_id)
    if doc is None:
        add_to_stash(video_id, artist_and_title, native_lyrics, num_snips)
    else:
        update_stash_lyrics(doc.videoId, native_lyrics)

# def split_file(fp, marker):
#     BLOCKSIZE = 4096
#     result = []
#     current = ''
#     for block in iter(lambda: fp.read(BLOCKSIZE), ''):
#         current += block
#         while 1:
#             markerpos = current.find(marker)
#             if markerpos == -1:
#                 break
#             result.append(current[:markerpos])
#             current = current[markerpos + len(marker):]
#     result.append(current)
#     return result

def store_snip(videoId, snip_count, bytes):

    db = get_db()
    doc_ref = db.collection(settings['SNIPS']).document(f"{videoId}_{snip_count}") 
    doc_ref.set({
        'soundbite': bytes,
    })

def store_audio_as_snips(videoId):

    # it is assumed this file exists
    audio_fqn = f"./temp/{videoId}.mp3"

    file = open(audio_fqn, 'rb')
    snip_count=0
    while True:
        audio_bytes = file.read(settings['AUDIO_SNIP_SIZE'])
        if audio_bytes and len(audio_bytes)>0:
            # store (next) snip
            store_snip(videoId, snip_count, audio_bytes)
            snip_count = snip_count+1
        else:
            break
    file.close()
    
    return snip_count


