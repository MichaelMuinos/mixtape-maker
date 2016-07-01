from __future__ import unicode_literals
from tkinter import *
import urllib.parse
import urllib.request
import re
import threading
import os
import subprocess

song_list = []
desktop_path = os.path.expanduser('~') + '\\Desktop\\'

'''
The following class creates the GUI for interacting in the command line with youtube dl. The inputs include a file name
for the song list, followed by the title of the desired mixtape. As the downloads happen, messages will pop out to the user
to show them there downloads are in progress.
'''
class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Mix-tape Maker")
        master.geometry("750x500")

        self.label = Label(master, text="Enter file name for the song list: ")
        self.label.pack()

        self.entry = Entry(master, width=45)
        self.entry.pack()

        self.label_title = Label(master, text="Title of Mixtape: ")
        self.label_title.pack()

        self.entry_title = Entry(master, width=45)
        self.entry_title.pack()

        self.button = Button(master, text="Download", command=self.download_button_click)
        self.button.pack()

        self.label_help = Label(master, text="\nHOW TO USE:\n1. Create a text file on your desktop listing each song you want line by line."
                                             "\n2. Enter the text file name inside the top most box.\n3. Give a title to your mixtape.\n"
                                             "4. Click download and the mixtape will be created on your desktop."
                                             "\n-----------------------------------------------------------------------------------\n")
        self.label_help.pack()

        self.text = Text(master)
        self.text.pack()

    '''
    On button click, read the inputted file line by line and retrieve all songs. Then start
    a seperate thread.
    '''
    def download_button_click(self):
        global song_list
        # read file user has entered in entry box one
        song_list = self.read_file(self.entry.get())

        # tkinter is single threaded, thus start a seperate thread for the download process
        DownloadVideosThread(self.text).start()

    '''
    Processes the users inputted title for the mixtape and creates a folder on the desktop.
    Reads each line of the file and stores the songs in a list.
    '''
    def read_file(self, file_name):
        global desktop_path
        # path to read text file
        file = desktop_path + file_name

        self.update_text_widget("Reading file " + self.entry.get())

        # read contents of file
        with open(file, "r") as f:
            songs = f.read().splitlines()

        # set new path to include the title of the mixtape as the subdirectory
        desktop_path += self.entry_title.get() + "\\"

        self.update_text_widget("\nFound " + str(len(songs)) + " songs!")

        return songs

    '''
    Update text to the tkinter widget to inform user what is happening.
    '''
    def update_text_widget(self, message):
        # Update text to text widget
        self.text.insert(END, message)
        # Move to the end of the text box if text has gone outside the initial length
        self.text.see(END)


'''
The following class runs on a seperate thread for searching youtube results and downloading
the songs.
'''
class DownloadVideosThread(threading.Thread):
    def __init__(self, text):
        threading.Thread.__init__(self)
        self.text = text

    def run(self):
        video_urls = self.find_video_urls(song_list)
        self.download_videos(video_urls, song_list)

    def update_text_widget(self, message):
        self.text.insert(END, message)
        self.text.see(END)

    '''
    Query youtube results based on the songs entered in the text file
    '''
    def find_video_urls(self, songs):
        videos = list()
        for song in songs:
            self.update_text_widget("\nSong - " + song + " - Querying youtube results ...")

            query_string = urllib.parse.urlencode({"search_query": song})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)

            # retrieve all videos that met the song name criteria
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())

            # only take the top result
            if len(search_results) is not 0:
                videos.append("https://www.youtube.com/watch?v=" + search_results[0])
                self.update_text_widget("\nSong - " + song + " - Found top result!")

        return videos

    '''
    Call command line for youtube dl. Sets the output directory for downloaded files.
    '''
    def download_videos(self, urls, songs):
        self.update_text_widget("\n\nStarting downloads ...")
        index = 0
        for url in urls:
            self.update_text_widget("\nSong - " + songs[index]
                                    + " - Extracting audio from video at " + url + " ...")
            # set flags to ensure the console does not pop up
            no_console = subprocess.STARTUPINFO()
            no_console.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # command line to do downloads
            subprocess.call(['youtube-dl', '-o', desktop_path + songs[index] + ".%(ext)s",
                 "--extract-audio", "--audio-format", "mp3", url], startupinfo=no_console)

            self.update_text_widget("\nSong - " + songs[index] + " - Download complete!")
            index += 1

        self.update_text_widget("\n\nAll downloads complete! Check your desktop for your mixtape!")

root = Tk()
root.resizable(width=False, height=False)
gui = GUI(root)
root.mainloop()



