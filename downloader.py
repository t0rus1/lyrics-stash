from __future__ import unicode_literals
import streamlit as st
import youtube_dl

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):   
    if d['status'] == 'finished': # could alo be 'downloading' or 'error'
        progress_message = '' #'Done downloading, now converting ...')
    elif d['status'] == 'downloading':
        # format a progress message
        # bytes_so_far = d['downloaded_bytes']
        # bytes_total = d['total_bytes']
        eta = d['eta']
        bytes_so_far = "{:,}".format(d['downloaded_bytes']) 
        bytes_total = "{:,}".format(d['total_bytes'])
        progress_message = f"{bytes_so_far} of {bytes_total} bytes. ETA: {eta} seconds ..."
    else:
        progress_message = d['status']

    with ydl_opts['placeholder']:
        st.write(progress_message)

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'outtmpl': './temp/%(title)s.%(ext)s',
    'placeholder': None,
    'continuedl': True,
    #'max_filesize': 10*1024*1024
}

def retrieve(url, placeholder):
    ''' use youtube_dl to download video 
        http://www.youtube.com/watch?v=nrGk0AuFd_9
        or
        https://youtu.be/VamaZaxdO70  

        regex like so 
        /^[A-Za-z0-9_-]{11}$/
        
    '''

    ydl_opts['placeholder'] = placeholder
    dl_error = None
    try:
        #youtube_dl.YoutubeDL( params={'-c': '', '--no-mtime': '', 'outtmpl': './%(uploader)s/%(title)s-%(upload_date)s-%(id)s.%(ext)s'} ).download([url])        
        #youtube_dl.YoutubeDL( params={'-c': '', '--no-mtime': '', 'outtmpl': './%(title)s-%(id)s.%(ext)s'} ).download([url])        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            #print(ydl.params)
            ydl.download([url])
    except youtube_dl.DownloadError as de:
         dl_error = de
    
    return dl_error
