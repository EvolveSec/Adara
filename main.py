import wx, wx.animate
import wx.lib.buttons as buttons
import pyvona
import answers
import threading
import speech_recognition1 as sr
import wx.richtext as rt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import urllib

class UI(wx.Frame):

	def __init__(self, parent, id):

		wx.Frame.__init__(self, parent, id, 'ADARA - Virtual Assistant', 
		size=(800, 720))

		#create and start voice recognition thread
		self.recThread = threading.Thread(name="recThread", target=self.voiceRec)
		self.recThread.setDaemon(True)
		self.recThread.start()

		#create the information retrieval thread (although not start)
		self.infoThread = threading.Thread(name="infoThread",
		target=self.retrieveInfo)
		self.infoThread.setDaemon(True)

		#create text-to-speech object
		self.v = pyvona.create_voice("GDNAIEH64WBP7PU3JMTQ",
		"WO72jncHEtZpLUmx47a/kUSiwHbvHiGGQ/BrmW4b")
		self.v.voice_name = "Salli"

		#creating the panel 
		self.panel = wx.Panel(self, -1)
		self.panel.SetBackgroundColour('#FFFFFF')

		#importing and displaying the gif animation 
		self.gif = "images/animation.gif"
		self.gif_ctrl = wx.animate.GIFAnimationCtrl(self.panel, -1, self.gif)
		self.gif_ctrl.GetPlayer().UseBackgroundColour(True)
		self.gif_ctrl.Play()

		#importing and displaying the logo image below gif
		self.image = wx.Image("images/logo.png").ConvertToBitmap()
		self.logo = wx.StaticBitmap(self.panel, -1, self.image, 
		size = (self.image.GetWidth(), self.image.GetHeight()))

		#creating the textboxes for the GUI
		self.Txtbox = wx.TextCtrl(self.panel, -1, style = wx.TE_MULTILINE 
		| wx.TE_NO_VSCROLL | wx.TE_RICH2)
		self.Outbox = rt.RichTextCtrl(self.panel, -1, style = wx.TE_MULTILINE 
		| wx.TE_READONLY | wx.VSCROLL)

		#setting the background colours for the GUI
		self.Outbox.SetBackgroundColour("#FFFFFF")
		self.Outbox.SetForegroundColour("#000000")
		self.Txtbox.SetBackgroundColour("#FFFFFF")
		self.Txtbox.SetForegroundColour("#000000")

		#importing button images
		self.speak_icon = wx.Image("images/microphone.png").ConvertToBitmap()
		self.speak_icon2 = wx.Image("images/microphone_on.png").ConvertToBitmap()

		#creating the button objects
		self.button1 = wx.Button(self.panel, 1, "Send", 
		size = (50, self.Txtbox.GetSize()[1]))
		self.button1.SetForegroundColour("#000000")
		self.button2 = wx.Button(self.panel, 2, "", 
		size = (50, self.Txtbox.GetSize()[1]))
		self.button2.SetForegroundColour("#000000")
		self.button2.SetBitmap(self.speak_icon)

		#button event handlers
		self.Bind(wx.EVT_CLOSE, self.onQuit) 
		self.button1.Bind(wx.EVT_BUTTON, self.onSend)
		self.button2.Bind(wx.EVT_BUTTON, self.onRec)

		#creating a displaying the favicon
		self.favicon = wx.Icon('images/icon.ico', wx.BITMAP_TYPE_ICO, 16, 16)
		wx.Frame.SetIcon(self, self.favicon)

		#logo sizer
		logoSizer = wx.BoxSizer(wx.VERTICAL)
		logoSizer.Add(self.gif_ctrl, flag=wx.EXPAND | wx.RIGHT, border=0)
		logoSizer.Add(self.logo, flag=wx.EXPAND | wx.LEFT, border=2)

		#textbox sizers
		txtSizer = wx.GridBagSizer(0,0)
		txtSizer.Add(self.Outbox, pos = (0,0), span=(2,1), flag=wx.EXPAND 
		| wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
		txtSizer.AddGrowableRow(0)
		txtSizer.AddGrowableCol(0)
		txtSizer.Add(self.Txtbox, pos = (2,0), flag=wx.EXPAND | wx.LEFT 
		| wx.BOTTOM, border=5)
		txtSizer.Add(logoSizer, pos=(0,1), flag=wx.EXPAND | wx.ALL, border=15)
		txtSizer.Add(self.button1, pos=(2,1), flag=wx.EXPAND | wx.RIGHT 
		| wx.LEFT | wx.BOTTOM, border=5)
		txtSizer.Add(self.button2, pos=(1,1), flag=wx.EXPAND | wx.RIGHT 
		| wx.LEFT | wx.BOTTOM, border=5)
		self.panel.SetSizerAndFit(txtSizer)

		#AI state
		self.state = 0

	def onRec(self, e):
		if not self.recording:
			self.recording = True
			self.button2.SetBitmap(self.speak_icon2)
		else:
			self.recording = False
			self.button2.SetBitmap(self.speak_icon)

	def onSend(self, e):
		if not self.infoThread.isAlive():
			self.button1.Enable(False)
			self.infoThread = threading.Thread(name="infoThread", 
			target=self.retrieveInfo, args=(self.Txtbox.Value,))
			self.Txtbox.SetValue("")
			self.infoThread.setDaemon(True)
			self.infoThread.start()

	def onQuit(self, e):
		self.r.stop()
		self.recording = False
		self.active = False

		while self.recThread.isAlive():
			pass

		self.Destroy()

	def retrieveInfo(self, user_input):

		self.outputUser(user_input)

		factoid = ["who", "what", "where", "when", "why", "how"]
		user_input = user_input.encode("utf-8")
		tokenized_input = user_input.split(" ")

		if tokenized_input[0].lower() in factoid:
			if "weather" in tokenized_input:
				self.outputAdara(answers.weather_search())
			elif "date" in tokenized_input:
				date = datetime.date.today()
				self.outputAdara("The date is " + str(date))
			elif "time" in tokenized_input:
				clock = datetime.datetime.now().time()
				time = datetime.time(clock.hour-12, clock.minute)
				self.outputAdara("The time is " + str(time))
			else:
				self.outputAdara(answers.duckduckgo_search(user_input))

		elif tokenized_input[0].lower() == "youtube":
			print(" ".join(tokenized_input[1:]))
			link_list = answers.youtube_search(" ".join(tokenized_input[1:]))

			if self.state == 0:
				self.browser = webdriver.Chrome()

			self.browser.get(link_list[0])
			self.browser.maximize_window()
			self.browser.get(link_list[0])
			self.state = 1

		elif tokenized_input[0].lower() == "search":
			if self.state == 0:
				self.browser = webdriver.Chrome()
				self.browser.maximize_window()

			query = urllib.quote(" ".join(tokenized_input[1:]))
			self.browser.get("https://duckduckgo.com/?q=" + query)
			self.state = 1

		elif user_input == "exit" or user_input == "close":
			if self.state == 0:
				self.outputAdara("Goodbye sir")
				self.onQuit(None)
			elif self.state == 1:
				self.browser.close()
				self.state = 0

		elif tokenized_input[0].lower() == "say":
			self.outputAdara(" ".join(tokenized_input[1:]))

		wx.CallAfter(self.button1.Enable, True)

	def outputUser(self, user_input):
		if user_input:
			wx.CallAfter(self.Outbox.BeginTextColour, (120, 120, 120))
			wx.CallAfter(self.Outbox.WriteText, user_input)
			wx.CallAfter(self.Outbox.EndTextColour)
			wx.CallAfter(self.Outbox.LineBreak)
			wx.CallAfter(self.Outbox.LineBreak)

	def outputAdara(self, information):

		try:
			wx.CallAfter(self.Outbox.BeginTextColour, (0, 0, 0))
			information.replace("|", ",")
			wx.CallAfter(self.Outbox.WriteText, information)
			wx.CallAfter(self.Outbox.EndTextColour)
			wx.CallAfter(self.Outbox.LineBreak)
			wx.CallAfter(self.Outbox.LineBreak)
			self.v.speak(re.sub("[<>\[\]\~\{\}\*]", "", information))

		except Exception, e:
			wx.CallAfter(self.Outbox.WriteText, "Unable to use Ivona Speech.")
			wx.CallAfter(self.Outbox.LineBreak)
			wx.CallAfter(self.Outbox.WriteText, str(e))
			wx.CallAfter(self.Outbox.LineBreak)
			wx.CallAfter(self.Outbox.LineBreak)

	def voiceRec(self):
		self.r = sr.Recognizer()
		self.m = sr.Microphone()

		self.recording = False
		self.active = True

		try:
			with self.m as source: self.r.adjust_for_ambient_noise(source)
			while self.active:
				if (self.recording) and (not self.infoThread.isAlive()): 
					with self.m as source: audio = self.r.listen(source)
					if self.recording: 
							try:
								value = self.r.recognize_google(audio)
								wx.CallAfter(self.button1.Enable, False)
								self.infoThread = threading.Thread(name="infoThread",
								target=self.retrieveInfo, args=(value,))
								self.infoThread.setDaemon(True)
								self.infoThread.start()
							except Exception, e:
								print(e)

		except KeyboardInterrupt:
			pass

def main():
	ex = wx.App()
	Frame = UI(parent=None, id=-1)
	Frame.Show()
	ex.MainLoop()
	print("\n" + str(threading.enumerate()))

if __name__ == '__main__':
	main()

