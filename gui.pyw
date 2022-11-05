import tkinter
import tkinter.ttk as tk
import threading
import json
import re
import os

import InfoParser
import YoutubeHandler
import YoutubeFrame

from tkscrolledframe import ScrolledFrame
from tkinter.filedialog import askdirectory

import os.path


def create_file(file_name, string=''):
    try:
        with open(file_name, 'x') as check_log:
            check_log.write(string)
    except FileExistsError:
        pass


def create_dir(dir_):
    try:
        os.mkdir(dir_)
    except FileExistsError:
        pass

def select_download_location():
    location = askdirectory()
    with open("download_location.txt", "w") as download_location:
        download_location.write(location)

class GUI:

    blue_light = "#f0fff0"
    light_green = "#f0fff0"

    def __init__(self):

        self.download_thread = threading.Thread(
            target=self.download_button_event)

        #----- Root Window ----------------------#
        self.root = tkinter.Tk()
        self.root.geometry("1000x750")
        self.root.maxsize(1000, 750)
        self.root.configure(bg="#add8e6")

        #----- Menu Difiniton -------------------#
        self.the_menu = tkinter.Menu(self.root, tearoff=0)
        self.the_menu.add_command(label="Cut")
        self.the_menu.add_command(label="Copy")
        self.the_menu.add_command(label="Paste")
        self.the_menu.add_command(label="Select all")

        #----- Upper Frame ----------------------#
        self.upper_frame = tkinter.Frame(self.root, bg="#add8e6", height=100)

        self.link_entry = tkinter.Entry(self.upper_frame)

        self.combo_box = tk.Combobox(
            self.upper_frame, width=15, state="readonly")
        self.combo_box["values"] = (
            "1080p", "720p", "480p", "360p", "240p", "144p")
        self.combo_box.current(1)

        self.download_button = tk.Button(
            self.upper_frame, text="Download", width=15, command=lambda: self.download_button_event_thread())

        self.change_location = tk.Button(
            self.upper_frame, text="Select Location", width=20, command=select_download_location)

        # self.download_thread.start

        # packing Upper Frame--------------------#

        self.link_entry.grid(column=0, row=0, pady=10,
                             padx=30, ipadx=200, ipady=5)
        self.combo_box.grid(ipady=6, padx=10, pady=10, column=1, row=0)
        self.download_button.grid(ipady=7, padx=10, pady=10, column=2, row=0)
        self.change_location.grid(ipady=7, padx=10, pady=10, column=3, row=0)

        self.link_entry.bind_class(
            "Entry", "<Button-3><ButtonRelease-3>", self.show_menu)

        self.upper_frame.pack(fill=tkinter.X)

        #-----------------------------------------#

        #----- ScrollBar Frame -------------------#

        self.scrollbar = ScrolledFrame(self.root, bg="#add8e6")
        self.scrollbar.pack(side="top", expand=1, fill="both")
        self.scrollbar.bind_arrow_keys(self.root)
        self.scrollbar.bind_scroll_wheel(self.root)

        self.lower_frame = self.scrollbar.display_widget(
            tkinter.Frame, fit_width=True)

        self.root.mainloop()

    def show_menu(self, e):
        w = e.widget

        def select_all():
            w.focus()
            w.selection_range(0, len(w.get()))
        self.the_menu.entryconfigure("Cut",
                                     command=lambda: w.event_generate("<<Cut>>"))
        self.the_menu.entryconfigure("Copy",
                                     command=lambda: w.event_generate("<<Copy>>"))
        self.the_menu.entryconfigure("Paste",
                                     command=lambda: w.event_generate("<<Paste>>"))
        self.the_menu.entryconfigure('Select all',
                                     command=select_all)
        self.the_menu.tk.call("tk_popup", self.the_menu, e.x_root, e.y_root)

    def download_button_event_thread(self):
        threading.Thread(target=self.download_button_event).start()

    def download_button_event(self):
        self.download_button["state"] = "disabled"
        entry_input = self.link_entry.get()
        combo_box_res = self.combo_box.get()
        print("combo_box_res: ", combo_box_res)
        playlist_match = re.search(
            InfoParser.PlayList.playlist_regex, entry_input)
        video_match = re.search(InfoParser.PlayList.video_regex, entry_input)

        if os.path.isfile("download_location.txt"):
            with open("download_location.txt") as location:
                os.chdir(location.read())

        if playlist_match:
            # -------------------------------------------------------
            # This section of code exports json data of the playlist
            # -------------------------------------------------------
            # Returns the id of the playlist from the regex match
            list_id = playlist_match.group(1)
            url = InfoParser.PlayList.playlistid_to_link(
                list_id)  # Returns the whole url from the list_id

            # Creates a directory with the name of the playlist id
            create_dir(list_id)
            os.chdir(list_id)

            # Checks if the json file already exists
            if not os.path.exists(f"{list_id}.json"):
                InfoParser.PlayList(url, combo_box_res).thread_export(
                    f"{list_id}.json")
            # -------------------------------------------------------
            # This section of code download the thumbnails
            # -------------------------------------------------------
            handler = YoutubeHandler.YoutubeHandler(f"{list_id}.json")
            handler.download_thumbnails()
            # Inflates all the YoutubeFrames inside the self.lower_frame
            handler.inflate(self.lower_frame)
            handler.download()

        elif video_match:
            # ----------------------------------------------------------
            # This section of code downloads a youtube video from link
            # ---------------------------------------------------------
            # Returns the id of the video from the regex match
            video_id = video_match.group(1)
            # Returns the whole url from the video_id
            url = InfoParser.PlayList.videoid_to_link(video_id)

            info = InfoParser.PlayList.get_vid_info(url, combo_box_res)

            create_dir(".thumbs")
            # downloads the thumbnail
            YoutubeHandler.download_file(
                info["thumbnail_url"], f".thumbs/{video_id}.jpg")

            # Creates a directory with the name of the playlist id

            youtube_frame = YoutubeFrame.YoutubeFrame(
                self.lower_frame, info, 0)
            youtube_frame.pack(anchor=tkinter.W, fill=tkinter.X)
            youtube_frame.download()

            # ----------------------------------------------------------

        self.download_button["state"] = "normal"


main = GUI()
