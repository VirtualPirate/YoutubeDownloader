import threading
import requests
import tkinter
import json
import os

import YoutubeFrame

lock = threading.Lock()

def download_file(url, filename):
	request = requests.get(url, stream=True)
	request.raise_for_status()
	with open(filename, 'wb') as f:
		for chunk in request.iter_content(chunk_size=1024):
			f.write(chunk)

class DownloadThread(threading.Thread):
	index = 0
	def __init__(self, handle, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.handle = handle

	def run(self):
		try:
			while DownloadThread.index < len(self.handle.frames):
				print("thread run")
				lock.acquire()
				self.frame = self.handle.frames[DownloadThread.index]
				DownloadThread.index += 1
				lock.release()
				self.frame.download()
				self.frame.commit(self.handle)
				print("thread finish")
		except IndexError:
			lock.release()
			print("DownloadThread returned")
			return

class YoutubeHandler:
	def __init__(self, json_file):
		self.json_file = json_file

		with open(self.json_file, 'r') as file:
			self.json_object = json.load(file)
		self.frames = []

	def download_thumbnails(self):
		thumb_dir = ".thumbs"
		try:
			os.mkdir(thumb_dir)
		except FileExistsError:
			pass
		os.chdir(thumb_dir)

		thumb_links = [(each_vid["thumbnail_url"], each_vid["video_id"]) for each_vid in self.json_object["playlist"]]
		def download_thumb():
			while len(thumb_links):
				popped = thumb_links.pop(0)
				image_name = f"{popped[1]}.jpg"
				if not os.path.exists(image_name):
					download_file(popped[0], f"{popped[1]}.jpg")

		download_threads = []
		for _ in range(5):
			t = threading.Thread(target=download_thumb)
			t.start()
			download_threads.append(t)

		for thread in download_threads:
			thread.join()
		os.chdir("../")

	def commit(self):
		lock.acquire()
		with open(self.json_file, 'w') as file:
			json.dump(self.json_object, file, indent=1)
		lock.release()

	def inflate(self, frame):
		index = 0
		for each_vid in self.json_object["playlist"]:
			each_frame = YoutubeFrame.YoutubeFrame(frame, each_vid, index, bg="#f0fff0")
			self.frames.append(each_frame)
			# print('self.frames = ', self.frames)
			each_frame.pack(anchor=tkinter.W, fill=tkinter.X)
			index+=1

	def download(self):
		download_threads = []
		for _ in range(2):
			t = DownloadThread(self)
			t.start()
			download_threads.append(t)

		for each_thread in download_threads:
			each_thread.join()
	# def download(self):
	# 	index = 0
	# 	while index < len(self.frames)-1:
	# 		download_threads = []
	# 		for _ in range(2):
	# 			t = DownloadThread(self, self.frames[index])
	# 			t.start()
	# 			download_threads.append(t)
	# 			index += 1

	# 		for each_thread in download_threads:
	# 			each_thread.join()
	# def download(self)
	# 	for first, second in pairwise(self.frames):
	# 		first_thread = threading.Thread(target=first.download)
	# 		second_thread = threading.Thread(target=second.download)
	# 		first_thread.start()
	# 		second_thread.start()
	# 		first_thread.join()
	# 		second_thread.join()
	# 		first.commit(self)
	# 		second.commit(self)
