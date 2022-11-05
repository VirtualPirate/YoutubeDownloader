import os
import re
import requests
import threading

def unique_list(variable):
	new_list = []
	for each_item in variable:
		if each_item not in new_list:
			new_list.append(each_item)
	return new_list

class PlayList:

	video_regex = r"watch\?v=([0-9A-Za-z_-]{11})"
	playlist_regex = r"\?list=([0-9A-Za-z_-]*)"

	resolutions = ("1080p", "720p", "480p", "360p", "240p", "144p")
	def __init__(self, url, res="720p"):
		self.url = url
		self.res = res
		self._log_name = re.search(PlayList.playlist_regex, url).group(1)
		self.playlist = PlayList.parse_vids(url)

	@staticmethod
	def parse_vids(url):
		return unique_list(re.findall(PlayList.video_regex, requests.get(url).text))

	@staticmethod
	def get_vid_info(url, res="720p"):
		from pytube import YouTube
		import re

		vid = YouTube(url)

		vid_stream = vid.streams.get_by_resolution(res)
		if not vid_stream:
			vid_stream = vid.streams.first()

		return {"title": vid.title,\
			"thumbnail_url": vid.thumbnail_url.replace(os.path.basename(vid.thumbnail_url), "default.jpg"),\
			"video_id": re.search(r"\?v=([0-9A-Za-z_-]*)", url).group(1),\
			"video_url": vid_stream.__dict__["url"],\
			"res": vid_stream.__dict__["resolution"],\
			"is_downloaded": False}

	def thread_export(self, filename):
		import json

		_temp_playlist = self.playlist
		playlist_info = {"id": self._log_name, "playlist": []}

		dict_lock = threading.Lock()

		def thread_func():
			while len(_temp_playlist):
				vid_id = _temp_playlist.pop()
				# print("vid_id: ", vid_id)
				vid_info = PlayList.get_vid_info(f"https://www.youtube.com/watch?v={vid_id}", self.res)

				dict_lock.acquire()
				playlist_info["playlist"].append(vid_info)
				dict_lock.release()

		#------------------
		threads = []
		for _ in range(10):
			t = threading.Thread(target=thread_func)
			t.start()
			threads.append(t)

		for thread in threads:
			thread.join()
		#-------------------

		with open(filename, "w") as file:
			json.dump(playlist_info, file, indent=1)

	@staticmethod
	def videoid_to_link(id_):
		return f"https://www.youtube.com/watch?v={id_}"

	@staticmethod
	def playlistid_to_link(id_):
		return f"https://www.youtube.com/playlist?list={id_}"

# PlayList("https://www.youtube.com/playlist?list=PLW-zSkCnZ-gB0RgkvF0NaN-dreQS1DsxB").thread_export("thread-export.json")