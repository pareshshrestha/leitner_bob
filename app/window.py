#! python3
#windows.py - File initializes and displays different small windows according to function in the root Tk()

from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import os

from app.app_logging import get_logger
logger = get_logger(__name__)

class QuestionWindow(Toplevel):
	'''
	Class created while inheriting Toplevel to display a small window on the main Tk() root window. 
	The purpose of the window is to display the user-input attributes of the Card class in order for the user to easily
	add or edit a Card object through a GUI.

	Args:
		root:	The main Tk() window over which the QuestionWindow will be displayed. 
		box:	Box object which will either hold the newly created card or card to be edited. 
		card:	Is None in the case where the user is creating a Card object. 
				Holds the Card object in the case where the user wants to edit a question. 

	'''
	def __init__(self, root, box, card=None):
		'''
		Creates and displays the window for question values for Card class.
		If card has a Card object, extracts the answer and questions and displays it in the window.
		'''
		logger.info('Creating QuestionWindow for')
		super().__init__(root) 

		self.root = root			#main window 
		self.leitner_box = box  	#box that holds or will hold the Card with the values inputted in the window
		self.card = card 			#If not None, is the card to be edited 

		#window configuration
		self.title('Question(s)')
		self.config(bg='Light blue')
		self.geometry('400x350')
		self.resizable(False, False)

		#Creating labels and entries for Question window

		#Input based Questions 
		#Label and entry for question where the under just enteres the correct answer 
		Label(self, text='Question Type: User inputs answer:', bg='white', bd=2,
			font=('Ariel', 10, 'bold')).place(x=7, y=10)
		self.enter_question = Entry(self, bg='white', bd=2, relief=RIDGE, width=45)
		self.enter_question.place(x=7, y=40)

		#Multiple-Choice based Questions (MCQs)
		
		#Label and entry for MCQ question 
		Label(self, text='Question Type: Multiple choice:', bg='white', bd=2,
			font=('Ariel', 10, 'bold')).place(x=7, y=80)
		self.enter_mcq = Entry(self, bg='white', bd=2, relief=RIDGE, width=45)
		self.enter_mcq.place(x=7, y=110)

		#Label and entry for MCQ options
		Label(self, text='Choices for the MCQ:(3 seperated by ,)', bg='white', bd=2,
			font=('Ariel', 10, 'bold')).place(x=7, y=150)
		self.enter_mcq_options = Entry(self, bg='white', bd=2, relief=RIDGE, width=45)
		self.enter_mcq_options.place(x=7, y=180)

		#Label and Entry for The correct answer
		Label(self, text='Correct Answer:', bg='white', bd=2,
			font=('Ariel', 10, 'bold')).place(x=7, y=220)
		self.enter_answer = Entry(self, bg='white', bd=2, relief=RIDGE, width=45)
		self.enter_answer.place(x=7, y=250)
		logger.debug('Successful creation of QuestionWindow')

		#Case where Card is to be edited and self.card holds a Card object
		if self.card != None:
			logger.debug('Importing values of Card into QuestionWindow.')
			#extracting and displaying questions, options and answers for the Card object

			#Displaying the answer
			self.enter_answer.insert(0,self.card.get_answer())

			#Checking which type of question exists for the answer 
			#Displying the question if not None
			if self.card.get_question(0) != None:
				self.enter_question.insert(0,self.card.get_question(0))	#Displaying Input Question
			if self.card.get_question(1) != None:
				mcq = self.card.get_question(1).split(',')	#Breaking up questions and options for MCQ
				self.enter_mcq.insert(0,mcq[0])				#Displaying MCQ Question
				self.enter_mcq_options.insert(0, (mcq[1]+','+mcq[2]+','+mcq[3]))	#Displaying MCQ options

		#Button to submit the new question or edited question for saving
		Button(self, text='Submit', font=('Ariel', 10, 'bold'), 
			command=lambda: self.submit_question(card), padx=20, pady=10).place(x=150, y= 290)


	def submit_question(self, card):
		'''
		Function called when the Submit button is pressed. 
		Obtains questions and answers from the Entry boxes in Question Window. 
		Formats the questions to be saved in the Card object. Creates new Card object if one does not exist. 
		If one already exists for it, updates the changes brought by editing. 

		Args:
			card:	Card object whose values have been edited.
					If a new Card is being created, the value passed will be None.

		'''
		logger.info('Attempting to create/update a Card')

		#Getting values from the Question Window question Entry objects
		input_question = self.enter_question.get().strip() #question index 0

		#Getting mcq questions and it's options
		mcq_question = self.enter_mcq.get().strip() #question index 1 
		mcq_options_joined = self.enter_mcq_options.get().strip()

		if len(mcq_options_joined) > 0:
			mcq_options = mcq_options_joined.split(',')
			#Cleaning the options
			mcq_options = [option.strip() for option in mcq_options]
			mcq_options_joined = ','.join(mcq_options)
		else:
			mcq_options = ''

		#Getting answer from Answer Entry 
		answer = self.enter_answer.get().strip()

		#Making sure that the new or edited question has the minimun required values for Card object

		#condition that it needs to have an answer
		if len(answer) == 0:
			messagebox.showerror('Error', 'Please enter an answer for the question.', parent=self)
			logger.debug('Card not created due to lack of answer input from user')
			return
		#condition that it needs to have one type of question 
		elif len(input_question) == 0 and len(mcq_question) == 0:
			messagebox.showerror('Error', 'Please enter at least one question for the flashcard.', parent=self)
			logger.debug('Card not created due to lack of question input from user')
			return
		#condition that it needs 3 options if it is an MCQ type question
		elif len(mcq_question) > 0 and len(mcq_options) != 3:
			messagebox.showerror('Error', 'Please enter exactly 3 mcq options seperated by "," .', parent=self)
			logger.debug('Card not created due to lack of mcq options input from user')
			return

		#The minimum conditions for a question Card is met
		else:
			question = [None, None]	# Configuration for at least one question existing, None for no question_type
			
			#Double check for question being more than one character
			if len(input_question) > 0:
				question[0] = input_question		#Question type 0 set

			#Double check for MCQ question conditions
			if len(mcq_question) > 0 and len(mcq_options) == 3:
				question[1] = mcq_question+','+mcq_options_joined	#Joining the question with options for Card creation

			#New Card creation
			if card == None:
				self.leitner_box.add_question(answer, question) #New card creation and addition to box1
				messagebox.showinfo('Info','The question has been added successfully.', parent=self)
				logger.debug('Successful creation of card')

				#Clearing the Entrys re-use as it is a sustained-activity
				self.enter_question.delete(0, END)
				self.enter_mcq.delete(0, END)
				self.enter_mcq_options.delete(0, END)
				self.enter_answer.delete(0, END)
			
			#Editing an existing card
			else:
				card.answer = answer 		#Updating Card answer
				card.questions = question 	#Updating Card questions
				messagebox.showinfo('Info', 'The question has been edited.', parent=self)
				logger.debug('Successful editing of card')
				#Destroying window as editing is One time activity 
				self.destroy()

class QuestionListbox(Toplevel):
	'''
	Class created while inheriting Toplevel to display a small window on the main Tk() root window.
	This window opens the user chosen box attribute in Box object and displays the questions.
	According to type, one or both types of button will be displayed. 
	The types are EDIT, DELETE or else which has a value of VIEW.

	Args:
		root:	Main Tk() window reference. 
		box:	Box object that holds the question Card objects to be displayed.
		type:	Type of action to be executed (EDIT, DELETE, VIEW)
				EDIT - 		Displays only edit button
				DELETE - 	Displys only delete button
				VIEW - 		Displays both buttons  

	'''
	def __init__(self, root, box, type):
		'''
		Creates the window that displays the question. 
		The user can choose the box to view questions through a drop down list and submit button. 
		Then the user can view the questions in the chosen box and scroll using a vertical scrool bar. 
		The button is created according to the type value.

		'''
		logger.info('Attemting creation of QuestionList window')
		super().__init__(root)
		self.root = root
		self.leitner_box = box
		self.type = type

		#Config for the created topwindow
		self.title('Questions List')
		self.geometry('400x350')
		self.config(bg='Light blue')
		self.resizable(False, False)

		#Implementation of box selection by user

		#Label for selection combo box
		Label(self, text='Choose the box:', bg='white', bd=2,
			font=('Ariel', 10, 'bold')).place(x=7, y=10)

		#Creation and deploying of combobox 

		#Creating and deploying the drop down list (Combobox)
		self.select_box = ttk.Combobox(self, values=[1,2,3,4,5], width=5, state='readonly')
		self.select_box.place(x=130, y=12)

		#Creating and deploying an area for questions (Listbox)
		self.question_listbox = Listbox(self, height=12, width=45, 
			selectmode=SINGLE)
		self.question_listbox.place(x=7, y=50)			

		#Creating and deplying button to take user selection from combobox and display the questions in the listbox
		Button(self, text='Submit', font=('Ariel', 10, 'bold'), 
			command=self.display_questions).place(x=200, y=8)

		#Adding a scroll bar to the listbox in order to display all questions
		scrollbar = Scrollbar(self, orient=VERTICAL, command=self.question_listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.question_listbox.config(yscrollcommand=scrollbar.set)

		#Creating and deplying buttons according to value of type arg
		if self.type == "EDIT":			#Displays only Edit button
			Button(self, text='Edit', font=('Ariel', 10, 'bold'),
				command=self.edit_selected_question).place(x=180, y=300)
			logger.debug('Successful creation of EDIT questionlist window')
		elif self.type == 'DELETE':		#Displays only Delete button
			Button(self, text='Delete', font=('Ariel', 10, 'bold'),
				command=self.delete_selected_question).place(x=180, y=300)
			logger.debug('Successful creation of DELETE questionlist window')
		else:							#Displays both buttons (usual value "VIEW")
			Button(self, text='Edit', font=('Ariel', 10, 'bold'),
				command=self.edit_selected_question, padx=15).place(x=110, y=300)
			Button(self, text='Delete', font=('Ariel', 10, 'bold'),
				command=self.delete_selected_question).place(x=220, y=300)
			logger.debug('Successful creation of VIEW questionlist window')

	def display_questions(self):
		'''
		Gets the user choice box value from Combobox. 
		Loops through the selected box, gets a question from each Card and displays it. 
		'''

		self.question_listbox.delete(0, END) #making sure that listbox is empty

		#Making sure the user has selected one box value
		selected_value = self.select_box.get()
		if selected_value:
			selected_box = int(selected_value) - 1 #getting the value of box to display questions
		else:
			messagebox.showerror('Error', 'You have not selected a box to view', parent=self)
			return 

		logger.info(f'Attemting to display question for selected box: {selected_box}')

		#Loop through the box to display all questions
		for card in self.leitner_box.boxlist[selected_box]:

			#Get question from Card object 
			#Ideal selection is Input question (0)
			question = card.get_question()	#Get question type 0
			if question == None: #No question type 0
			#Get question type 1 after formatting the return value
				question_and_options = card.get_question(1)
				questions_options_split = question_and_options.split(',')
				question = questions_options_split[0]

			self.question_listbox.insert(END, card.get_question()) #Displaying the question inside listbox
		logger.debug(f'Successfully displyed questions of cards inside user selected box: {selected_box}')
	
	def edit_selected_question(self):
		'''
		Action upon pressing the "Edit" button.
		It takes the user selection(s) from Listbox and opens QuestionWindow of the selected question's Card. 
		'''
		logger.info('Attempting to edit the user selected question from Edit Window')
		selected_indices = self.question_listbox.curselection()		#fetching selected card indices

		#Making sure that the user has selected at least one card
		if selected_indices == ():
			messagebox.showerror('Error', 'You have selected no questions to edit', parent=self)
			return

		#Looping through the indices to view each selected card
		for index in selected_indices:
			card = self.leitner_box.boxlist[int(self.select_box.get())-1][index]
			QuestionWindow(self.root, self.leitner_box, card)		#Displaying the selected card
			logger.debug('Edit window is attempting to call method to display Question Window.')
			self.display_questions()	#refreshing the window
		logger.info('Successfully edited user selected question(s)')

	def delete_selected_question(self):
		'''
		Action upon pressing the "Delete" button. 
		It takes the user selection(s) from Listbox and deletes the Card from the chosen box.
		'''
		logger.debug('Attempting to delete user selected question in Delete/View Window')
		selected_indices = self.question_listbox.curselection()		#fetching user selections

		#Making sure that the user has selected at least one card
		if selected_indices == ():
			messagebox.showerror('Error', 'You have selected no questions to delete.', parent=self)
			return

		#Looping through the indices to delete each selected card
		for index in selected_indices:
			self.leitner_box.boxlist[int(self.select_box.get())-1].pop(index)		#Deleting the selected card
			messagebox.showinfo('Info','Question deleted successfully.', parent=self)
			self.display_questions()	#refreshing the window
		logger.info('Successfully deleted user selected question')


class HelpWindow(Toplevel):
	'''
	TODO: Actually write the information necessary for Help window. 

	Class created by inheriting Toplevel to create a top window over the root Tk().
	This class just opens the 'leitner_bob/data/help.txt' file and displays it's content. 
	'''
	def __init__(self, root):
		logger.info('User asked for help!')
		super().__init__(root)

		#Configuring the window
		self.root = root
		self.title('Help Window')
		self.geometry('400x350')
		self.resizable(False, False)
		self.config(bg='Light blue')

		#Obtaining the correct file path for 'help.txt'
		main_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
		helpfile = os.path.join(main_dir, 'data', 'help.txt')

		#opening help file
		with open(helpfile, 'r') as file:
			help_instructions = file.read()

		#Creating frame and text box to display it's content
		#creating frame for the text box
		frame = Frame(self)
		frame.pack(fill=BOTH, expand=True, pady=10, padx=10)

		#Creating and deploying text box
		text = Text(frame, font=('Ariel', 12), wrap='word', bg='white', height=15, width=40)
		
		#Populating the text box with information from 'help.txt'
		text.insert(END, help_instructions)
		text.config(state=DISABLED)			#Making sure the user can't edit the text file
		text.pack(side=LEFT, fill=BOTH, expand=True)

		#Creating and implementing scroll bar for the text box
		scrollbar = Scrollbar(frame, command=text.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		text.config(yscrollcommand=scrollbar.set)

