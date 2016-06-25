from __future__ import unicode_literals
from tkinter import *
import youtube_dl
import urllib
import re
import os
import shutil
import threading
import queue as Queue
import io

youtube_dl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

song_list = []
desktop_path = "/Users/michael/Desktop/"


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Mix-tape Maker")
        master.geometry("500x500")

        self.label = Label(master, text="Enter the directory to song list:")
        self.label.pack()

        self.entry = Entry(master, width=45)
        self.entry.pack()

        self.button = Button(master, text="Download", command=self.download_button_click)
        self.button.pack()

        self.text = Text(master)
        self.text.pack()

    def download_button_click(self):
        buffer = io.StringIO()
        # print("Starting download...", file=buffer)
        # self.update_text_widget(buffer)

        global song_list
        song_list = self.read_file(self.entry.get())
        self.queue = Queue
        DownloadVideosThread(self.queue).start()
        self.master.after(100, self.update_text_widget(buffer))

        # print("All downloads complete!", file=buffer)
        # self.update_text_widget(buffer)

    def update_text_widget(self, buffer):
        output = buffer.getvalue()
        self.text.insert(END, output)
        self.text.see(END)

    def read_file(self, file_name):
        global desktop_path
        file = desktop_path + file_name
        with open(file, "r") as f:
            songs = f.read().splitlines()
        desktop_path += songs.pop(0) + "/"
        return songs


class DownloadVideosThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        video_urls = self.find_video_urls(song_list)
        self.download_videos(video_urls, song_list)
        self.create_desktop_directory(song_list)

    def find_video_urls(self, songs):
        videos = list()
        # index = 1
        for song in songs:
            
            # print("Song #" + str(index) + ": " + song, file=buffer)
            # self.update_text_widget(buffer)

            query_string = urllib.parse.urlencode({"search_query": song})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())

            if len(search_results) is not 0:
                videos.append("https://www.youtube.com/watch?v=" + search_results[0])
        return videos

    def download_videos(self, urls, songs):
        index = 0
        for url in urls:
            with youtube_dl.YoutubeDL(youtube_dl_options) as ydl:
                song = songs[index].split('-')
                ydl.download([url])
                file = ydl.prepare_filename({'title': song[0], 'ext': 'mp3', 'id': song[1]})
                print(file)
            index += 1
            # print("Downloads Complete")

    def create_desktop_directory(self, songs):
        if not os.path.exists(desktop_path):
            os.makedirs(desktop_path)
            print(desktop_path)

        program_path = "/Users/michael/PycharmProjects/MixtapeMaker/"
        contents = os.listdir(program_path)

        song_number = 0
        for content_part in contents:
            filename, file_extension = os.path.splitext(program_path + content_part)
            if file_extension == ".mp3":
                shutil.move(program_path + content_part, desktop_path + songs[song_number] + ".mp3")
                song_number += 1


root = Tk()
root.resizable(width=False, height=False)
gui = GUI(root)
root.mainloop()



