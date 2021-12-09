import os
import os.path
import json
import streamlit as st
import downloader,store
from youtube_dl.utils import DownloadError

from appconfig import settings
import dumper

def submit_youtube_query(youtube, query, results_size):
    request = youtube.search().list(q=query, part='snippet', type='video', maxResults=results_size)
    res = request.execute()
    return res

def search_form_callback():
    ''' executed when form is submitted and before re-run '''

    if st.session_state.reset_checkbox:
        return

    if st.session_state.music_query == '':
        return

    if not hasattr(st.session_state,'title_radio'):
        return

    chosen_title = st.session_state.title_radio[4:] # skip leading number and period eg '01. Yanni...  '
    chosen_index = int(st.session_state.title_radio[0:2])
    # dont download title already in the player
    was_just_retrieved = hasattr(st.session_state,'current_playee') and chosen_title == st.session_state.current_playee

    #dumper.dump(st.session_state.urls_by_title, 2)
    download_url = st.session_state.urls_by_title[chosen_title]

    # if st.session_state.video_links_only:
    #     st.info(st.markdown(f"Preview on Youtube here: [{download_url}]({chosen_title})"))
    #     return

    if not was_just_retrieved:
        with st.spinner(f"Downloading and extracting audio from '{chosen_title}' youtube video ..."):
            placeholder = st.empty()
            completion_state = downloader.retrieve(download_url, placeholder)
            if completion_state is not None:
                if isinstance(completion_state, DownloadError):
                    st.error(f'This video ({chosen_title}) may only being played on Youtube itself')
                    #print(completion_state)
                elif isinstance(completion_state,FileNotFoundError):
                    st.error('File not found - title may contain disallowed characters...')
                else:
                    st.exception(completion_state)
            else:
                st.markdown(f'** {chosen_title} ** loaded')

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
            st.download_button('Download (optional)', f, file_name=audio_fn, help='Optionally add to your local, offline collection!')
        stash_item = store.get_stash_snapshot_by_videoId(audio_id)
        if stash_item is None:
            # new song
            # store the audio in a series of soundbites
            with st.spinner("Storing NEW song entry plus it's audio..."):
                num_snips_stored = store.store_audio_as_snips(audio_id)
                # then add music entry to firestore stash
                store.add_to_stash(audio_id, chosen_title, '* needs lyrics!', num_snips_stored)
                # keep tracking the video ids
                st.session_state.videoIds.append(audio_id)
                st.write(f"Just added: {chosen_title} ✔️")
        else:
            #store the audio anew:            
            num_snips_to_delete = stash_item.to_dict()['snips']
            num_snips_deleted = store.delete_all_audio_snips(audio_id, num_snips_to_delete)
            num_snips_stored = store.store_audio_as_snips(audio_id)
            #print(f"deleted {num_snips_deleted} old snips, added {num_snips_stored} new ones")
            #update snip count in the stash collection
            store.update_stash_snips_count(audio_id, num_snips_stored)
            st.info(f'⚠️ This song ({chosen_title}) was already in your stash! Audio has been re-saved in case a fix was needed.')
        
    else:
        st.error(f'Unable to find or play {audio_fn}') 


def browse_and_collect(youtube, video_links_only, results_size):

    if hasattr(st.session_state,'reset_checkbox') and st.session_state.reset_checkbox:
        st.session_state.music_query = ''
        st.session_state.reset_checkbox = False

    music_query = st.text_input("Artist and|or name of song video to search for. Submit an empty search to reset.", key='music_query', help='Artist AND song OR just artist OR just song. To begin a new search, clear this text box and click submit below')    

    if not music_query or (hasattr(st.session_state,'current_playee') and st.session_state.current_playee != '') :
        st.session_state.current_playee = ''
        submit_button = st.form_submit_button('search')
        st.warning('please enter a search term eg Αντώνης Ρέμος')
        st.stop()
    else:
        st.session_state.qry_result = submit_youtube_query(youtube, music_query, results_size)

        titles = []
        st.session_state.urls_by_title = {}
        st.session_state.video_id_by_index = {}
        st.session_state.video_links_only = video_links_only

        list_num=1
        for item in st.session_state.qry_result['items']:
            if video_links_only: # eg https://www.youtube.com/watch?v=9i3szgwCXzg
                # write simple youtube link screen (which user may click to watch video in youtube tab)
                st.markdown(f"[{item['snippet']['title']}]({settings['WATCH_STEM']}{item['id']['videoId']})")
            else:
                # per usual mode of operating, write numbered title to a list for presentation below as a list of radiobuttons
                list_prefix = f"{list_num}".zfill(2)
                # mark if the title is already in the stash

                # performance hit when we search for each videoId like this
                #stash_item = store.get_stash_snapshot_by_videoId(item['id']['videoId'])                               
                #owned = '❗ ' if stash_item is not None else ''

                # instead consult the session_state
                # owned = '❗' if item['id']['videoId'] in st.session_state.videoIds else ''

                titles.append(f"{list_prefix}. {item['snippet']['title']}")
                #also write to dict of urls keyed on title
                video_url = f"{settings['WATCH_STEM']}{item['id']['videoId']}"
                st.session_state.urls_by_title[item['snippet']['title']] = video_url
                st.session_state.video_id_by_index[list_num] = item['id']['videoId']
                list_num = list_num+1

        # let see this
        #dumper.dump(st.session_state.urls_by_title, 1)
        
        # clears the music query with submit
        st.checkbox('Reset search', key='reset_checkbox', help='to begin a new search, check here and submit below. (else leave unchecked to continue selecting songs)')

        if not video_links_only:
            # present a radio button list
            st.radio('Choose a title to convert to audio and play/download', titles, key='title_radio')
            submit_button = st.form_submit_button(label='Get selected audio / reset', on_click=search_form_callback)
        else:
            st.write('click on any of the above links to play in a separate Youtube tab')
            submit_button = st.form_submit_button(label='.')


    return submit_button