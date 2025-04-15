#! python3
# gui.py - Handles all the gui based application of lietner bob.

"""
This module contains the primary GUI implementation for the Leitner Box application.
It handles all UI components, event handling, and serves as the integration point
for database operations, flashcard presentation, and statistics tracking.

The main class, LeitnerApp, orchestrates the entire application flow and UI rendering.
"""

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image

import os 
import random

from app.database import Database
from app.models import Box, Card
from app.graph import create_graphframe
from app.pomodoro import PomodoroTimer
import app.logic as logic
from app.window import QuestionWindow, QuestionListbox, HelpWindow
from app.flashcard import FlashCard

from app.app_logging import get_logger
logger = get_logger(__name__)

class LeitnerApp:
	'''
	Main application class that creates and manages the Leitner Box learning system GUI.

	Thi scalss is responsible for initializing all the UI, handling user actions, and coordinates between
	the user and various components (e.g. database, flashcards, etc.)

	Attributes:
		leitner_box (Box):	Object of Box class that contains all the cards for the session. 
		database (Database):	Object of Database class and handles all the data storage and retrieval. 
								Handles all the file IO operations. 
		userdata (Dict):	Username-specific user data. Has keys "session_data" and "pomodoro" for 
							% correct questions per session and total focus time, respectively.
		root(Tk):			Main application window. 
		workframe (Frame):	Content area that handles number of questions per session. 
							Also the staging area for flash cards for questions. 
		graphframe (Frame):	Area for displaying user's stats. 
							The y-axis is the percentage of questions that the user got right per session.
							The x-axis is session(s).
		quickframe (Frame):	Contains buttons (links) for frequently excecuted/common functions.
		pomodoroframe (Frame):	Frame containing the Pomodoro timer and displays user's total time 
								spent on focused studying.
	'''
	def __init__(self, username):
		'''
		Initializes the LeitnerApp class which also creates all the GUI for the app functionality. 
		Is user specific.

		Args:
			username: The username for the database access and personalization.
		'''
		logger.info(f'Initializing LeitnerApp for user: {username}')
		self.leitner_box = Box() #The Leitner boxes are all stored in the big Box
		
		#Open a database for the LeitnerApp
		logger.info(f'Opening database connection')		
		self.database = Database(username)

		#Loading cards onto the app Box
		logger.info(f'Loading flashcards from database')
		self.database.load_cards(self.leitner_box)
		
		#Loading user data 
		self.userdata = self.database.load_userdata()

		#creating base window for the entire app
		logger.debug(f'Seeting up main application window for {username}')
		self.root = Tk()
		self.root.title("Leitner BoB!")
		self.root.config(bg='Light blue')
		self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

		#autosaving on accidental or intentional window exit
		self.root.protocol("WM_DELETE_WINDOW", self.quit_program)

		#creating and implementing the menu bar
		logger.debug("Creating application menu")
		self.menubar = Menu(self.root)
		self.root.config(menu=self.menubar)
		self.create_menu(self.menubar)

		logger.debug(f'Setting up UI component frames for {username}')
		#creating and implementing frame that holds commands for running the lietner app
		self.workframe = Frame(self.root, bd=5, relief=RIDGE, width=900, height=500, bg='white')
		self.workframe.place(x=230, y=20)
		self.create_workframe(self.workframe)

		#creating and implementing frame that shows user's sessiondata as a graph
		self.graphframe = Frame(self.root, bd=5, relief=RIDGE, width=1330, height=120, bg='white')
		self.graphframe.place(x=15, y=530)
		create_graphframe(self.graphframe, self.userdata) #calling method to implement the UI and logic

		#creating and implementing the quick access frame
		#holds quick links to frequently used functions
		self.quickframe = Frame(self.root, bd=5, relief=RIDGE, width=200, height=500, bg='white')
		self.quickframe.place(x=15,y=20)
		self.create_quickframe(self.quickframe, self.database, self.leitner_box)

		#creating and implementing frame that holds a pomodoro timer clock 
		self.pomodoroframe = Frame(self.root, bd=5, relief=RIDGE, width=200, height=500, bg='white')
		self.pomodoroframe.place(x=1150, y=20)
		self.pomodoro = PomodoroTimer(self.pomodoroframe, self.userdata)	#calling method to implement the UI and logic

		logger.info('Creation and intialization of LeitnerApp class complete')

	def create_menu(self, menubar):
		'''
		Creates the application menu bar with all drop down menus.
		The main menu options are:
			- File menu
			- Edit menu
			- View menu
			- Help menu

		Args:
			menubar: Root or parent menu widget that is to be modified.
		'''

		#FILE MENU
		logger.debug('Setting up the File menu') 
		filemenu = Menu(menubar, tearoff = 0)

		#Open command accessses the database and loads cards for the session
		#Recalling the command saves and loads cards for session which will be different than before (random selection of questions)
		filemenu.add_command(label='Open', command = lambda: self.database.load_cards(self.leitner_box))
		filemenu.add_separator()

		#Save command saves all the cards and user data from the session to the database 
		#It leaves the main Box object empty with no cards. You need to call Open command to run the quiz.
		filemenu.add_command(label='Save', command = lambda: self.database.save_cards(self.leitner_box))
		filemenu.add_separator()

		#Quit command quits the entire app 
		#However it also runs the save command and saves all current user data.
		filemenu.add_command(label='Quit', command = self.quit_program)
		menubar.add_cascade(label='File', menu = filemenu)

		#EDIT MENU
		logger.debug('Setting up Edit menu')
		editmenu = Menu(menubar, tearoff=0)

		#Add question command 
		#Launches QuestionWindow from window.py which takes in answer and question inputs to create Card object 
		#Adds the card to the box 
		editmenu.add_command(label='Add question', command=lambda: QuestionWindow(self.root, self.leitner_box))
		editmenu.add_separator()

		#Edit question command
		#Launches the QuestionListbox from window.py which will allow the user to choose a box, view the questions inside
		#the box, choose a question to edit and then launch a QuestionWindow to edit the selected question
		editmenu.add_command(label='Edit question', command=lambda: QuestionListbox(self.root, self.leitner_box,'EDIT'))
		editmenu.add_separator()

		#Remove question command 
		#Launches the QuestionListbox from window.py which will allow the user to choose a box, view the questions inside 
		#the box, choose a question and remove or delete it from the box and hence the database
		editmenu.add_command(label='Remove question', command=lambda: QuestionListbox(self.root, self.leitner_box, 'DELETE'))
		menubar.add_cascade(label='Edit', menu=editmenu)

		#VIEW MENU 
		logger.info('Setting up View menu')
		viewmenu = Menu(menubar, tearoff=0)

		#View stats command 
		#TODO 
		viewmenu.add_command(label='View Stats', command=...)
		viewmenu.add_separator()

		#View questions by box command
		#Launches the QuestionListbox from window.py and allows the user to view all questions of choosen box
		#It has both the edit and delete button and can perform both actions
		viewmenu.add_command(label='View questions by box', command=lambda: QuestionListbox(self.root, self.leitner_box, 'VIEW'))
		menubar.add_cascade(label='View', menu = viewmenu)

		#HELP MENU
		#Allows the user to ask for help
		helpmenu = Menu(menubar, tearoff=0)
		helpmenu.add_command(label='Help', command =lambda: HelpWindow(self.root))
		menubar.add_cascade(label='Help', menu = helpmenu)

	def create_workframe(self, frame):
		'''
		Implements all the UI for the user's main work area for the leitner learning system. 
		Allows the user to choose how many questions they want to quiz themselves with. 
		Gives 4 options: 10, 20, 50 and 100 questions. 

		Args:
			- frame: frame inside root that have the GUI implemetation 
		'''
		logger.info('Creating work frame')
		#get absolute path for images
		base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
		abs_image_path = os.path.abspath(base_dir)

		#Using the app logo as a background
		image = Image.open(os.path.join(abs_image_path, 'tiles.png'))
		self.photo = ImageTk.PhotoImage(image.resize((600,400)))
		logo_label = Label(frame, image=self.photo, bd=0)
		logo_label.place(x=130, y=20)

		#Text UI 
		Label(frame, text='Welcome to Leitner BoB!',
			font=('Ariel', 20, 'bold'), bg ='white').place(x=270, y=5)
		Label(frame, text='Your very own Leitner learning app.', 
			font =('Ariel', 10, 'italic'), bg='white').place(x=320, y=40)
		Label(frame, text='Choose your difficulty for the day:', 
			font=('Ariel', 20, 'bold'), bg='white').place(x=220, y=340)

		#Creating buttons with image so user can choose difficulty of session
		button = Image.open(os.path.join(abs_image_path, 'button.png'))
		self.button_photo = ImageTk.PhotoImage(button.resize((120, 70)))

		diff = [10, 20, 50, 100]			#text for difficulty levels
		x_positions = [80, 280, 480, 680]	#x-position for the four buttons

		logger.info('Creating the four difficulty levels')
		#Implementing the four buttons for four different difficulty levels 
		#The button launches flashcard frame that will overlap the current frame and will handle the quiz mechanism
		for i, dif in enumerate(diff):
			btn = Button(frame, text = str(dif), image = self.button_photo, compound= 'center', 
				font=('Ariel', 20), command = lambda d=dif: self.create_flashcard_frame(self.root, self.leitner_box, d), 
				bg='white',	borderwidth=0, highlightthickness=0)
			btn.place(x=x_positions[i], y=390)

	def create_flashcard_frame(self, root, leitner_box, question_num):
		'''
		Handles the creation and implementation of flashcard frame which will come to overlap the workframe. 
		It handles the actual presentation of questions in the form of flashcards and quizzes the user according to their 
		chosen difficulty level. 
		The question handling is actually done by Flashcard class imported. 

		Args:
			root:			main window for the application
			leitner_box:	box that contains all the question cards for the current session
			question_num:	difficulty level/total questions as selected by the user in workframe
		'''
		logger.debug('Creating flashcard frame')
		#Creating the flashcard frame inside root
		flashcard_frame = Frame(root, bd=5, relief=RIDGE, width=900, height=500, bg='white')
		flashcard_frame.place(x=230, y=20)

		logger.debug('Creating FlashCard object and executing the quiz')
		#Creating Flashcard object to control the quizzing and handle the UI implementation inside the frame
		flashcard = FlashCard(flashcard_frame, leitner_box, question_num)

		#collecting user's performance in the current session
		total_correct = flashcard.get_stat()

		#displying user their stats for the current session 
		messagebox.showinfo('Info', f'You got {total_correct} questions right out of {question_num} questions.')

		#storing the user activity
		logger.debug('Updating the userdata regarding quiz session')
		self.userdata['session_data'].append((total_correct/question_num)*100)
		#TODO: allow the user to view all the questions again whether right or wrong

		#removing the default created 40 session history
		if self.userdata['session_data'][0] == 0:
			self.userdata['session_data'].pop(0)

		#Updating the graph with new data
		self.update_graph()

	def create_quickframe(self, root, database, box):
		'''
		Frame that holds buttons for frequently executed actions for ease of access. 
		Has the following buttons:
			reset button:	Same as open or load questions button. 
							Saves all the cards in the current box and then loads another random set of questions to replace 
							the saved questions. 
			save button:	Quickly saves all the data for the user currently (cards).
							Leaves the box attribute of the app class empty and data needs to be loaded again before use.
			add_question:	Button that launces the QuestionWindow and allows the user to add question(s). 

		Args:
			root: 		Tk() root window with all the UI implements 
			database:	Database class object that handles file IO 
			box:		Box object that holds the Card objects for the current session
		'''
		logger.info('Implementing the quick access frame with quick access links')

		Label(root, text='Quick Acess:', font=('Ariel', 15, 'bold'), bg='white').place(x=15, y=4)

		base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
		abs_image_path = os.path.abspath(base_dir)

		reset = Image.open(os.path.join(abs_image_path, 'reset.png'))
		self.reset_photo = ImageTk.PhotoImage(reset.resize((120,100)))

		reset_button = Button(root, text='Reset Questions', image=self.reset_photo,
			compound="top", font=('Ariel', 10, 'bold'), command = lambda : database.load_cards(box), 
			bg='white', borderwidth=0, highlightthickness=0)
		reset_button.place(x=25, y=41)

		save = Image.open(os.path.join(abs_image_path, 'saveicon.png'))
		self.save_photo = ImageTk.PhotoImage(save.resize((120,100)))

		save_button = Button(root, text='Save Progress', image=self.save_photo,
			compound="top", font=('Ariel', 10, 'bold'), command = lambda : database.save_cards(box), 
			bg='white', borderwidth=0, highlightthickness=0)
		save_button.place(x=25, y=191)

		addq = Image.open(os.path.join(abs_image_path, 'addquestion.png'))
		self.addq_photo = ImageTk.PhotoImage(addq.resize((120,100)))

		addq_button = Button(root, text='Add Question', image=self.addq_photo,
			compound="top", font=('Ariel', 10, 'bold'), command= lambda: QuestionWindow(self.root, self.leitner_box), 
			bg='white', borderwidth=0, highlightthickness=0)
		addq_button.place(x=25, y=341)

	def run(self):
		self.root.mainloop()

	def quit_program(self):
		'''
		Function that is run every time the user performs an action that closes the app. 
		Saves all user data (user activity data and card data)
		'''
		logger.info('User choose to quit the application')

		logger.debug('Attempting to save user data before closing')
		logic.arrange_boxes(self.leitner_box)		#arranging the cards in the current session 
		self.database.save_cards(self.leitner_box)	#saving all the user cards back to their box files

		self.pomodoro.save_session_time()			#saving user focus time
		self.database.save_userdata(self.userdata)	#saving user's success with answering questoins

		logger.debug('Closing and quiting the application')
		self.root.quit()	#quitting the app
		self.root.destroy()	#deleting the window 

	def update_graph(self):
		'''
		Updates the graph with the latest user data.
		Clears the graphframe and redraws the graph with current data.
		'''
		logger.debug('Updating the graph with latest user data')

		#Clear the current contents of graphframe
		for widget in self.graphframe.winfo_children():
			widget.destroy()

		#Recreate the graph with updated data
		create_graphframe(self.graphframe, self.userdata)