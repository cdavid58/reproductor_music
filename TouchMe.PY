from tkinter import filedialog, messagebox
import threading, json, random, os, time, requests
from pygame import mixer, display
from tkinter import *
from api_music import Api_Music

class Repro(Api_Music):

	def __init__(self):
		self.root = Tk()
		self.root.title("TouchMe")
		self.root.iconbitmap('logo.ico')
		self.root.geometry('1080x640')
		self.root.resizable(0,0)
		self.root.protocol("WM_DELETE_WINDOW", self.handler)

		self.CHUNK = 1024
		self.currentDir = StringVar()
		self.currentDir.set(os.getcwd())
		self.filename = StringVar()
		self.playing = False
		self.file_path = ""
		mixer.init()
		display.init()
		self.paused = False
		self.stopped = False
		self.random_mode = False
		self.running = False
		self.c = 0

		with open("music_favs.json") as f:
		   self.audio_list = json.load(f)

		self.timer = Label(self.root,text="0:00:00",bg="black",fg="green",font=("arial","34"),width=13,height=2)
		self.timer.place(x=9,y=0)
		Button(self.root,text="PLAY",width=10,bg="goldenrod1",command=self.init_task).place(x=356,y=18)
		self.btnPause = Button(self.root,text="PAUSE",width=10,bg="goldenrod1", command=self.pause)
		self.btnPause.place(x=437,y=18)
		Button(self.root,text="STOP",width=10,bg="goldenrod1",command=self.stop).place(x=518,y=18)
		self.items = Label(self.root,text=('{} Canciones en la lista'.format(len(self.audio_list))),font=("arial",10),width=39,height=2,bg="black",fg="red")
		self.items.place(x=601,y=18)
		Button(self.root,text="ELIMINAR LISTA DE REPRODUCCIÓN",width=44, command=self.remove_playlist).place(x=601,y=100)#215
		Button(self.root,text="ELIMINAR DE LA LISTA DE REPRODUCCIÓN",width=44, command = self.remove_from_list).place(x=601,y=70)#249
		self.btnPlayall = Button(self.root,text="Reproducir toda la lista",width=44,command=self.init_task2)
		self.btnPlayall.place(x=601,y=130)
		self.canvas = Canvas(self.root)
		self.canvas.place(x=9,y=147)
		self.scrollbar = Scrollbar(self.canvas,orient=VERTICAL)
		self.scrollbar.pack(side=RIGHT,fill=Y)
		self.fav_list = Listbox(self.canvas,width=94,height=25,bg="gray96")
		self.fav_list.pack()
		self.fav_list.config(yscrollcommand = self.scrollbar.set)
		self.scrollbar.config(command = self.fav_list.yview)
		self.btnPlayall.bind(self.init_task2)
		self.Time_Show_List()
		self.root.mainloop()
		self.empty = 0

	def init_task2(self):
		if len(self.audio_list)>0 and self.playing == False:
			self.btnPlayall.configure(state="disabled")
			t2 = threading.Thread(target=self.play_loop)
			t2.setDaemon(True)
			t2.start()

	def play(self):
		self.playing = True
		try:
			mixer.music.load(self.file_path)
			mixer.music.play()
			self.update_timer()
		except:
			self.playing = False

	def init_task(self):
		if self.playing == False:
			self.any_selected = self.is_any_selected()
			if self.any_selected:
				self.file_path = self.my_list[self.fav_list.curselection() [ 0 ] ]
				self.key = self.get_key(self.file_path)
				self.filename.set(self.key)
				if self.file_path:
					if os.path.exists(self.file_path):
						self.timer['text']="0:00:00"
						t = threading.Thread(target=self.play)
						t.setDaemon(True)
						t.start()
		else:
			messagebox.showwarning("NO FILE",'''Path not found, file may have been deleted or moved.''')

	def Time_Show_List(self):
		t = threading.Thread(target = self.show_list)
		t.setDaemon(True)
		t.start()

	def show_list(self):
		n = 0
		# value = self.fav_list.get_key(0,END)
		# print(value)
		while True:
			print(n)
			n += 1
			with open("music_favs.json") as f:
				self.audio_list = json.load(f)
			if len(self.audio_list) > 0:
				self.my_list = []
				c = 1
				self.fav_list.delete('0','end')
				for i in (self.audio_list):
					self.fav_list.insert(END,(str(c)+"- "+i))
					self.my_list.append(self.audio_list[i])
					c+=1
				self.empty = 1
				if self.empty:
					self.init_task2()
			else:
				self.empty = 0
			time.sleep(5)

	def is_any_selected(self):
		self.num_selected = 0
		for i in range(0,self.fav_list.size()):
			if self.fav_list.selection_includes(i):
				self.num_selected += 1
				sel = True
				break
			else:
				sel = False
		return sel

	def stop(self):
		mixer.music.stop()
		self.stopped = True
		self.running = False
		self.btnPlayall.configure(state="normal")

	def pause(self):
		if self.playing == True:
			mixer.music.pause()
			self.paused = True
			self.btnPause.configure(text="CONTINUE",command=self.unpause)

	def unpause(self):
		mixer.music.unpause()
		self.stopped = False
		self.paused = False
		self.btnPause.configure(text="PAUSE",command=self.pause)

	def get_key(self,val):
		for key, value in self.audio_list.items():
			if val == value:
				return key

	def play_loop(self):
		self.playing = True
		self.stopped = False
		self.paused = False
		self.c = 0
		if self.random_mode == False:
			self.playlist = self.my_list[::-1]
		else:
			self.listado = self.create_list(self.my_list,self.c)
			self.playlist = self.my_list
		self.running = True
		while self.running:
			if len(self.playlist) > 0 and self.stopped == False:
				if mixer.music.get_busy() == 0 and self.paused == False:
					if self.random_mode == False:
						current = self.playlist.pop()
						self.url_music = current
						print("eliminar 1")
						self.Update_State("Sonando")
					else:
						current = self.playlist[self.listado[self.c]]
						print('eliminar 2')
					try:
						mixer.music.load(current)
						self.filename.set(self.get_key(current))
						any_selected = self.is_any_selected()
						if any_selected:
							self.fav_list.selection_clear(self.fav_list.curselection()[0])
							self.Update_State("Eliminada")
							self.Delete_Music()
							self.Delete_First_Music()
							print('eliminar 3')
						if self.random_mode == False:
							self.fav_list.selection_set(self.c)
							self.fav_list.see(self.c)
							self.c+=1
							print('eliminar 4')
						else:
							self.fav_list.selection_set(self.listado[self.c])
							self.fav_list.see(self.listado[self.c])
							print('eliminar 5')
							if self.c < len(self.listado)-1:
								self.c+=1
								print("eliminar 6")
							else:
								self.listado = self.create_list(self.my_list,self.listado[self.c])
								self.c = 0
								print("eliminar 7")
						self.playing = True
						mixer.music.play()
						self.update_timer()

					except:
						if self.random_mode == False:
							self.c+=1
						else:
							if self.c < len(self.listado)-1:
								self.c += 1
								print("Repito 1")
							else:
								self.listado = self.create_list(self.my_list,self.listado[self.c])
								self.c = 0
								print("Repito 2")
			else:
				if self.c != 0:
					self.c = 0
					self.playlist = self.my_list[::-1]
				# self.fav_list.selection_clear(self.fav_list.curselection()[0])
				# self.Delete_First_Music()

		self.playing = False

	def update_timer(self):
		pos_time = mixer.music.get_pos()
		s = pos_time//1000
		m, s = divmod(s, 60)
		h, m = divmod(m, 60)
		h, m, s = int(h), int(m), int(s)
		self.timer['text']=f"{h:01}:{m:02}:{s:02}"
		self.process = self.root.after(500, self.update_timer)
		if h == -1:
			self.timer['text']="0:00:00"
			self.root.after_cancel(self.process)
			self.btnPause.configure(text="PAUSE",command=self.pause)
			self.playing = False
 
	def remove_playlist(self):
		if self.fav_list.size() > 0:
			message = messagebox.askquestion("ELIMINAR LISTA DE REPRODUCCIÓN",'¿Quieres eliminar toda la lista de reproducción?')
			if message == "yes":
				self.playing = False
				self.running = False
				self.btnPlayall.configure(state='normal')
				self.my_list = []
				self.fav_list.delete(0,END)
				self.audio_list = {}
				d = {}
				with open("music_favs.json", "w") as f:
					json.dump(d, f)
				self.items.configure(text='0 Canciones en la lista')

	def remove_from_list(self):
		if self.fav_list.size() > 0:
			self.any_selected = self.is_any_selected()
			if self.any_selected:
				message = messagebox.askquestion("Quitar Cancion",'Eliminar el elemento seleccionado de la lista de reproducción?')
				if message == "yes":
					if self.running == False:
						mixer.music.stop()
					else:
						self.running = False
						self.btnPlayall.configure(state='normal')
					self.file_path = self.my_list[self.fav_list.curselection()[0] ]
					self.key = self.get_key(self.file_path)
					del self.audio_list[self.key]
					self.fav_list.delete(0,END)
					with open("music_favs.json", "w") as f:
						json.dump(self.audio_list, f)
					with open("music_favs.json") as f:
						self.audio_list = json.load(f)
					if len(self.audio_list) > 0:
						self.my_list = []
						c = 1
						self.fav_list.delete('0','end')
						for i in (self.audio_list):
							self.fav_list.insert(END,(str(c)+"- "+i))
							self.my_list.append(self.audio_list[i])
							c+=1
					self.items.configure(text='{} Canciones en la lista'.format(len(self.audio_list)))
		else:
			messagebox.showwarning("No ha seleccionado una cancion","Seleccione el elemento que desea eliminar.")

	def handler(self): 
		message = messagebox.askquestion("Salida",'¿Seguro que quieres salir?')
		if message == 'yes':
			self.root.quit()

	def Delete_First_Music(self):
		with open("music_favs.json") as f:
			value = json.load(f)
		list_data = []
		url = []
		for i,k in value.items():
			list_data.append(i)
			url.append(k)
		data = {}
		firstData = [x for x in list_data if not x[0] in list_data ]
		for i in range(len(list_data)):
			if i > 0:
				try:
					data[list_data[i]] = url[i]
					with open("music_favs.json", "w") as f:
						json.dump(data, f)
				except IndexError as e:
					break
			else:
				os.remove('./Music/'+str(list_data[0]))

	def Delete_Music():
		self.file_path = self.my_list[self.fav_list.curselection()[0] ]
		self.key = self.get_key(self.file_path)
		del self.audio_list[self.key]
		self.fav_list.delete(0,END)
		with open("music_favs.json", "w") as f:
			json.dump(self.audio_list, f)
		with open("music_favs.json") as f:
			self.audio_list = json.load(f)
		if len(self.audio_list) > 0:
			self.my_list = []
			c = 1
			self.fav_list.delete('0','end')
			for i in (self.audio_list):
				self.fav_list.insert(END,(str(c)+"- "+i))
				self.my_list.append(self.audio_list[i])
				c+=1
		self.items.configure(text='{} Canciones en la lista'.format(len(self.audio_list)))

	def Update_State(self,state):
		url = "https://apimusic.pythonanywhere.com/user/Update_State_First/"
		payload = json.dumps({
		  "code": '2AFUDSBP0d',
		  "state":state
		})
		headers = {
		  'Content-Type': 'application/json'
		}
		response = requests.request("POST", url, headers=headers, data=payload)

if __name__ == '__main__':
	code = "2AFUDSBP0d"
	api_music = Api_Music(code)
	value = ""
	def Time_Execute():
		global value
		while True:
			api_music.Elements()
			api_music.Get_Music()
			api_music.Donwload_Song()
			api_music.Elements()
			time.sleep(3)
	t = threading.Thread(target=Time_Execute)
	t.setDaemon(True)
	t.start()
	Repro()

