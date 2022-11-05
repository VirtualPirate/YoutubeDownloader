import tkinter
import threading
import requests
import tkinter.ttk as tk
import time
import re
import os

import InfoParser
# import YoutubeHandler

from PIL import ImageTk, Image

light_green = "#f0fff0"


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

# This is the reuseable Frame class that contains the progress bar and download speed


class DownloaderFrame(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress = tk.Progressbar(
            self, orient=tkinter.HORIZONTAL, length=300, mode="determinate")
        self.speed = tkinter.Label(self, text="0kbps", bg="#fff")

        self.progress.grid(column=0, row=0, padx=10, pady=10)
        self.speed.grid(column=1, row=0, padx=10, pady=10)

# This downloader class runs a function on a thread every second and holds information for data downloaded per second


class Downloader:
    def __init__(self, url, downloader_frame):
        self.url = url
        self.download_frame = downloader_frame
        self.data_per_sec = 0
        self.total_data = 0
        self.continue_thread = False
        self.request = requests.get(self.url, stream=True)
        # print(self.request.headers)

    def download(self, filename, thread_func=None):
        if thread_func:
            thread = threading.Thread(target=thread_func)
        else:
            thread = threading.Thread(target=self.observer)
        self.request.raise_for_status()

        with open(filename, 'wb') as f:
            self.continue_thread = True
            thread.start()
            for chunk in self.request.iter_content(chunk_size=1024):
                self.data_per_sec += 1
                f.write(chunk)
            self.continue_thread = False
            thread.join()
        print("Download finished")
        for thread in threading.enumerate():
            print("Running: ", thread.name)

    def observer(self):
        while self.continue_thread:
            self.total_data += self.data_per_sec
            self.download_frame.speed.configure(
                text=f"{self.data_per_sec}kbps")
            self.download_frame.progress['value'] = 100 * (
                self.total_data / (int(self.request.headers["Content-Length"])/1024))
            self.data_per_sec = 0
            time.sleep(1)
        self.download_frame.progress["value"] = 100


# This reuseable frame class contains thumbnail image, video_title and a DownloaderFrame
class YoutubeFrame(tkinter.LabelFrame):

    def __init__(self, root, video_info, index, *args, **kwargs):
        # print("current dir:", os.getcwd())
        super().__init__(root, bg="#f0fff0", *args, **kwargs)
        self.video_info = video_info

        self.index = index
        self.img = ImageTk.PhotoImage(Image.open(
            f".thumbs/{video_info['video_id']}.jpg"))

        self.thumb_panel = tkinter.Label(self, image=self.img)
        self.title = tkinter.Label(
            self, text=video_info["title"], font=("Arial", 13), bg=light_green)
        self.progressbar_frame = DownloaderFrame(self, bg="#fff")

        self.thumb_panel.grid(rowspan=2, column=0, row=0)
        self.title.grid(column=1, row=0, padx=20, sticky=tkinter.W)
        self.progressbar_frame.grid(column=1, row=1, padx=20, sticky=tkinter.W)

    def download(self):
        # if the link is expires the video is repased
        if self.link_expired():
            self.video_info = InfoParser.PlayList.get_vid_info(InfoParser.PlayList.videoid_to_link(
                self.video_info["video_id"]), res=self.video_info["res"])

        video_name = f"{get_valid_filename(self.video_info['title'])}.mp4"

        # if the file has already been downloaded
        if self.video_info["is_downloaded"]:
            self.progressbar_frame.progress["value"] = 100
            return

        self.downloader = Downloader(
            self.video_info["video_url"], self.progressbar_frame)
        self.downloader.download(video_name)
        self.video_info["is_downloaded"] = True

    def link_expired(self):
        link_date = re.search(r"expire=(\d+)", self.video_info["video_url"])
        if link_date and time.time() < int(link_date.group(1)):
            return False
        print("The link has been expired")
        return True

    def commit(self, handle):
        handle.json_object["playlist"][self.index] = self.video_info
        handle.commit()


# root = tkinter.Tk()
# info = {
#    "title": "Custom Brushes in Adobe Photoshop (Part 3) - Urdu / Hindi",\
#    "thumbnail_url": "https://i.ytimg.com/vi/vheDlkoYXMc/default.jpg",\
#    "video_id": "vheDlkoYXMc",\
#    "video_url": "https://r1---sn-g5pauxapo-jj0e.googlevideo.com/videoplayback?expire=616964060&ei=fJVgYI3bAZaoz7sPv-eMoAg&ip=202.168.84.217&id=o-ACRX1Up_ObGbs83YPTisIzoOwGL6EOKbOC2C_DAEEJ4p&itag=22&source=youtube&requiressl=yes&mh=9P&mm=31%2C29&mn=sn-g5pauxapo-jj0e%2Csn-ci5gup-qxae7&ms=au%2Crdu&mv=m&mvi=1&pl=24&initcwndbps=678750&vprv=1&mime=video%2Fmp4&ns=LE4NsECoUL-f3D8rLAuQOXUF&cnr=14&ratebypass=yes&dur=511.907&lmt=1532089379832277&mt=1616942203&fvip=7&fexp=24001373%2C24007246&c=WEB&n=9Inz-rVIGAmAJdvJoDPB8&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Ccnr%2Cratebypass%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAORPIUe3UKd5ucQRIYae4vMoLN15N9XGwMVDuLLEPjgjAiEAk59aMjriyCp0ENAPfBYYVlBbS55egqJFkl4Hlw_Zfsk%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRgIhAIqX3-rCRAfQNuN1iRqbSAuTfhqfkPEUPw2K0XaBT6UwAiEA0Q3oB4y6zytkQxY6bDY3WzgfgmL-YdZSgRowHcTzvy0%3D",\
#    "res": "720p",\
#    "is_downloaded": False}
# fram = YoutubeFrame(root, info , bg=light_green)
# fram.pack()
# download_thread = threading.Thread(target=fram.download)
# download_thread.start()

# root.mainloop()
