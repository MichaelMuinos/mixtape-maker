from __future__ import unicode_literals
from tkinter import *
import youtube_dl
import urllib
import re
import io

youtube_dl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}


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

        print("Starting download...", file=buffer)
        self.update_text_widget(buffer)

        song_list = self.read_file(self.entry.get())
        video_urls = self.find_video_urls(song_list, buffer)
        self.download_videos(video_urls, buffer)

        print("All downloads complete!", file=buffer)
        self.update_text_widget(buffer)

    def update_text_widget(self, buffer):
        output = buffer.getvalue()
        self.text.insert(END, output)
        self.text.see(END)

    def read_file(self, file_name):
        with open(file_name, "r") as f:
            songs = f.read().splitlines()
        return songs

    def find_video_urls(self, songs, buffer):
        videos = list()
        index = 1
        for song in songs:
            print("Song #" + str(index) + ": " + song, file=buffer)
            self.update_text_widget(buffer)

            query_string = urllib.parse.urlencode({"search_query": song})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())

            if len(search_results) is not 0:
                videos.append("https://www.youtube.com/watch?v=" + search_results[0])
        return videos

    def download_videos(self, urls, buffer):
        for url in urls:
            with youtube_dl.YoutubeDL(youtube_dl_options) as ydl:
                ydl.download([url])
        print("Downloads Complete")

root = Tk()
root.resizable(width=False, height=False)
gui = GUI(root)
root.mainloop()



