import tkinter
import tkinter.ttk as tk
import threading
import json
import re
import os

import InfoParser
import YoutubeHandler

from tkscrolledframe import ScrolledFrame

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

class GUI:

	blue_light = "#f0fff0"
	light_green = "#f0fff0"

	def __init__(self):

		self.download_thread = threading.Thread(target=self.download_button_event)

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

		self.combo_box = tk.Combobox(self.upper_frame, width=15, state="readonly")
		self.combo_box["values"] = ("1080p", "720p", "480p", "360p", "240p", "144p")
		self.combo_box.current(1)

		self.download_button = tk.Button(self.upper_frame, text="Download", width=15, command=self.download_thread.start)

		# packing Upper Frame--------------------#

		self.link_entry.grid(column=0, row=0, pady=10, padx=30, ipadx=200, ipady=5)
		self.combo_box.grid(ipady=6 ,padx=10, pady=10, column=1, row=0)
		self.download_button.grid(ipady=7, padx=10, pady=10, column=2, row=0)

		self.link_entry.bind_class("Entry", "<Button-3><ButtonRelease-3>", self.show_menu)

		self.upper_frame.pack(fill=tkinter.X)

		#-----------------------------------------#

		#----- ScrollBar Frame -------------------#

		self.scrollbar = ScrolledFrame(self.root, bg="#add8e6")
		self.scrollbar.pack(side="top", expand=1, fill="both")
		self.scrollbar.bind_arrow_keys(self.root)
		self.scrollbar.bind_scroll_wheel(self.root)

		self.lower_frame = self.scrollbar.display_widget(tkinter.Frame, fit_width=True)





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
		command= select_all)
		self.the_menu.tk.call("tk_popup", self.the_menu, e.x_root, e.y_root)

	def download_button_event(self):
		self.download_button["state"] = "disabled"
		entry_input = self.link_entry.get()
		playlist_match = re.search(InfoParser.PlayList.playlist_regex, entry_input)
		video_match = re.search(InfoParser.PlayList.video_regex, entry_input)
		if playlist_match:
			#-------------------------------------------------------
			# This section of code exports json data of the playlist
			#-------------------------------------------------------
			list_id = playlist_match.group(1) # Returns the id of the playlist from the regex match
			url = InfoParser.PlayList.playlistid_to_link(list_id) # Returns the whole url from the list_id

			create_dir(list_id) #Creates a directory with the name of the playlist id
			os.chdir(list_id)

			if not os.path.exists(f"{list_id}.json"): # Checks if the json file already exists
				InfoParser.PlayList(url).thread_export(f"{list_id}.json")
			#-------------------------------------------------------
			# This section of code download the thumbnails
			#-------------------------------------------------------
			handler = YoutubeHandler.YoutubeHandler(f"{list_id}.json")
			handler.download_thumbnails()
			handler.inflate(self.lower_frame) # Inflates all the YoutubeFrames inside the self.lower_frame
			handler.download()

	# 	elif video_match:
	# 		#----------------------------------------------------------
	# 		# This section of code downloads a youtube video from link
	# 		# ---------------------------------------------------------
	# 		video_id = video_match.group(1) # Returns the id of the video from the regex match
	# 		url = PlayList.videoid_to_link(video_id) # Returns the whole url from the video_id

	# 		create_dir("downloads") #Creates a directory with the name of the playlist id
	# 		os.chdir("downloads")

	# 		#----------------------------------------------------------

		self.download_button["state"] = "normal"

main = GUI()
