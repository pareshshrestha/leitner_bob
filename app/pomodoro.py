#! python3
# pomodoro.py - Handles the creation and deployment of pomodoro watch inside the main app

from tkinter import *
from tkinter import messagebox

from app.app_logging import get_logger
logger = get_logger(__name__)

class PomodoroTimer:
	'''
	Class that handles the UI implementation and logic for the pomodoro clock inside app. 
	Allows the user to set the focus and break times and also stores the total focus time for the user to keep track of their 
	progress. 

	Args:
		root:		frame inside the main window where the pomodorotimer will be implemented
		userdata:	previous userdata about their activity in pomodoro timer 

	'''

	def __init__(self, root, userdata):
		logger.info('Creating Pomodoro timer')
		
		self.root = root				#frame where pomodoro clock will be implemented
		self.userdata = userdata		#past user data

		self.focus_time = 25*60			#default focus time in seconds
		self.break_time = 5*60			#default break time in seconds

		self.remaining_time = 25*60		#remaining time in seconds (initially configured for default focus time)
		self.running = False			#checks if the timer is currently running or not

		self.work = False				#is focus time or break time
		self.session_total = 0 			#total focus time for this session

		#Label for the frame title
		Label(self.root, text='Pomodoro Timer:', font=('Ariel', 15, 'bold'), bg='white').place(x=7, y=4)

		#Label and Entry for focus time 
		#User can see and change the focus time for the session 
		Label(root, text='Focus time:', font=('Ariel', 10, 'bold'), bg='white').place(x=7, y=35)		
		self.focus_time_new = Entry(self.root, width=10, bd=2)
		self.focus_time_new.insert(0, 25)
		self.focus_time_new.place(x=7, y=55)
		Button(self.root, text='Submit', command=self.get_focustime).place(x=110, y=53) 

		#Label and Entry for break time
		#User can see and change the break time for the session
		Label(root, text='Break time:', font=('Ariel', 10, 'bold'), bg='white').place(x=7, y=95)		
		self.break_time_new = Entry(self.root, width=10, bd=2)
		self.break_time_new.insert(0, 5)
		self.break_time_new.place(x=7, y=115)
		Button(self.root, text='Submit', command=self.get_breaktime).place(x=110, y=113)

		#Text based CLOCK face
		self.time_label = Label(self.root, text = self.format_time(), bg='white', font=('Ariel', 20, 'bold'))
		self.time_label.place(x=7, y=150)

		#POMODORO buttons to control the timer
		Button(self.root, text='Start', command=self.start).place(x=7,y=230)
		Button(self.root, text='Pause', command=self.pause).place(x=65,y=230)
		Button(self.root, text='Reset', command=self.reset).place(x=125,y=230)	

		#Amount of time spent working for the current session
		self.session_label = Label(self.root, text= self.get_session_text(),
			bg='white', font=('Ariel', 10, 'bold'))
		self.session_label.place(x=10, y=310)

		#Amount of time spent working for the user 
		self.total_progress = Label(self.root, text= self.get_previous_sessions(),
			bg='white', font=('Ariel', 10, 'bold'))
		self.total_progress.place(x=20, y=390)

	def format_time(self):
		#formats and returns the time from seconds to user readable format

		minutes = self.remaining_time // 60
		seconds = self.remaining_time % 60
		return f'{minutes} min(s)\n{seconds} sec(s)'

	def get_focustime(self):
		#Changes the focus time according to the user's edit of focus time in the Entry
		logger.info('Changing the focus time')

		self.focus_time = int(self.focus_time_new.get())*60 #setting the new focus time
		self.focus_time_new.delete(0,END)					#clearing the Entry
		self.remaining_time = self.focus_time     			#remaining time update
		self.time_label.config(text=self.format_time()) #update clock implement with the new focus time

	def get_breaktime(self):
		#Changes the break time according to the user's edit of break time in Entry
		logger.info('Changing the break time')

		self.break_time = int(self.break_time_new.get())*60  	#setting the new break time
		self.break_time_new.delete(0,END)						#clearing the Entry

	def update_timer(self):
		'''
		Main logic for the pomodoro timer. 
		If the start is pressed (self.running is True), counts down from the total time remaining. 
		Also updates the text clock face.
		'''
		if not self.running:				#Timer is not running
			self.update_session_label()		#If work session, update the label that shows total focus time for the session
			return
		if self.running == True and self.remaining_time>0:	#timer is running and there is time left in focus/break time
			self.remaining_time -= 1  						#counting down 1 second 
			if self.work == True:							#if it is focus time, add to the session focus time
				self.session_total += 1
			self.time_label.config(text=self.format_time())	#update the text clock face
			self.root.after(1000, self.update_timer)		#calling itself after the second to count down another session if running is still True
		self.update_session_label()							#if not running, then update the focus time for the session

	def start(self):	#starts the pomodoro timer
		logger.info('Starting the pomodoro timer')
		if self.remaining_time == self.focus_time:		#catergorizing focus time and break time 
			self.work = True
		if not self.running:							#Starts the timer if it is not already running
			self.running = True
			self.update_timer()							#Show the timer in the text clock face

	def pause(self):	#pauses the timer
		logger.info('Pausing the pomodoro timer')
		self.running = False

	def reset(self):	#resets the timer and moves from focus to break or vice versa
		logger.info('Resetting the pomodoro timer')

		self.running = False									#first, stop the timer from ticking down
		if self.remaining_time == self.focus_time:				#True if it is focus time
			self.remaining_time = self.break_time  				#Change to break time
		else:													#Else change to focus time
			self.remaining_time = self.focus_time
		self.time_label.config(text=self.format_time())
		self.update_session_label()
		self.work = False										#to remove false positive and false negatives

	def update_session_label(self):								#updates clock face
		self.session_label.config(text=self.get_session_text())

	def get_session_text(self):									#Shows the amount of focus time for this session
		return f'Work done this session: \n{int(self.session_total)//60}  mins and {int(self.session_total)%60} secs'

	def get_previous_sessions(self):							#Extracts and returns user history of focus work
		try:
			data = self.userdata['pomodoro']					#If data exists
		except:													#If data doesn't exist
			self.userdata['pomodoro'] = 0
			data = self.userdata['pomodoro']

		return f'Work done overall: \n{int(data//360)} hours'	#Returning user data in readable format

	def save_session_time(self):								#saving user's session data in seconds
		logger.debug('Saving user data for pomodoro session')
		self.userdata['pomodoro'] += self.session_total

		
