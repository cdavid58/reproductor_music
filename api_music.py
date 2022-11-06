import webbrowser, pafy, os, json, requests, time, threading, pathlib
from youtubesearchpython import VideosSearch
from moviepy.editor import *
from plyer import notification

class Api_Music:

	def __init__(self,code):
		self.code = code
		self.list_music = []
		self.audio_list = {}
		self.number = 1
		self.url_list = []
		self.count = 10

	def Update_State(self,state):
		url = "https://apimusic.pythonanywhere.com/user/Update_State/"
		payload = json.dumps({
		  "pk_music": self.pk_music,
		  "state":state
		})
		headers = {
		  'Content-Type': 'application/json'
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		# self.list_music = json.loads(response.text)

	def Get_Music(self):
		url = "https://apimusic.pythonanywhere.com/user/Get_List_Music/"
		payload = json.dumps({
		  "code": self.code
		})
		headers = {
		  'Content-Type': 'application/json'
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		self.list_music = json.loads(response.text)


	def Count_Link(self,video):
		count = 0
		for ele in self.url_list:
			if ele == video:
				count += 1
		return count

	def Donwload_Song(self):
		for i in self.list_music:
			self.Youtube_Music(i['name'],i['artist'],i['pk'],i['user_pk'])
		self.Update_State("En lista")

	def normalize(self,s):
	    replacements = (
	        ("á", "a"),
	        ("é", "e"),
	        ("í", "i"),
	        ("ó", "o"),
	        ("ú", "u"),
	    )
	    for a, b in replacements:
	        s = s.replace(a, b).replace(a.upper(), b.upper())
	    return s

	def Youtube_Music(self,music,artist,pk,pk_user):
		self.pk_music = pk
		videosSearch = VideosSearch(music+' '+artist, limit = 1)
		video = ""
		title = ""
		for i in range(1):
		    video = (videosSearch.result()['result'][i]['link'])
		    title = str(videosSearch.result()['result'][i]['title']).replace('"','_')
		self.url_list.append(video)
		if self.Count_Link(video) <= self.count:
			video = pafy.new(video)
			bestaudio = video.getbestaudio()
			bestaudio.download()
			audio = AudioFileClip(title+'.webm')
			audio.write_audiofile('./Music/'+str(self.number)+self.normalize(title)+'.mp3')
			audio.close()
			os.remove(title+'.webm')
			self.number += 1
			# self.Delete_Music(pk, pk_user)
		else:
			notification.notify(
				title='ERROR',
				message='Lo sentimos la cancion '+str(music)+" ya fue colocada más de "+str(self.count)+" veces",
				app_icon='logo.ico',
				timeout = 15
		   );self.Delete_Music(pk, pk_user)


	def Delete_Music(self,pk, pk_user):
		url = "https://apimusic.pythonanywhere.com/user/Delete_Music/"
		payload = json.dumps({
		  "pk": pk,
		  'pk_user':pk_user
		})
		headers = {
		  'Content-Type': 'application/json'
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		print("TERMINADO\n\n\n")

	def Elements(self):
		name_folder = "Music"
		folder = os.listdir(name_folder)
		path = str(pathlib.Path().absolute()).replace('\\','/')+'/Music/'
		with open("music_favs.json") as f:
			value = json.load(f)
		
		key = []
		items = []

		for k,v in value.items():
			key.append(k)
			items.append(v)
		n = 0
		for i in folder:
			self.audio_list[os.path.join(i)]=path+i
			with open("music_favs.json", "w") as f:
				json.dump(self.audio_list, f)