#! python3
# flashcard.py - Holds the logic and simple GUI for Flashcard implementation of Card objects

import random
import app.logic as logic
from tkinter import *
from tkinter import messagebox
import re

from app.app_logging import get_logger
logger = get_logger(__name__)

class FlashCard:
	'''
	Class that holds the logic and GUI implementation required to turn Card objects inside Box object to flashcards to quiz user.
	It takes the root, box object for user and number of questions as an input and displays the number of questions as 
	quiz flash cards from the box object inside the root. 

	Atgs:
		root:			Panel where the flashcard quiz will take place
		leitner_box:	Box object that holds Card objects to be displayed as Flashcards
		question_num:	Total number of Flashcards to be displayed

	'''

	def __init__(self, root, leitner_box, question_num):
		logger.info('Creating the flashcard environment for quiz')
		self.root = root 
		self.box = leitner_box
		self.num = question_num

		self.session_cards = logic.get_session_cards(self.box, self.num)	#Getting self.num number of random questions from self.box using imported logic
		self.correct_answers = 0 					#Recording total correct answers for the session

		self.curr_question = 0

		logger.debug('Starting the quiz, asking the first question')
		self.run_card(self.session_cards[self.curr_question]) #Does the quizzing with the selected cards

	def run_card(self, card):
		'''
		Handles the actual quiz mechanism for the app. 
		Takes a card according to self.curr_question from selected questions. 
		Then it displays the question and takes user answer according to the question type. 
		It has submit button which calls for a check of the user answer and moves the quiz forward. 
		It also has a quit session button which ends the quiz session.

		Args:
			card: Card to be made into flashcard for quiz
		'''

		#clearing the working stage - by clearing the frame of old information or previous question
		for widget in self.root.winfo_children():
			widget.destroy()
		

		#Quiz progression label which shows how many questions attempted out of total as a fraction
		Label(self.root, text=f'Question {self.curr_question+1}/{self.num}',
			font=('Ariel',15, 'bold'), bg='white'). place(x=370, y=5)

		#Extracting the question, answer and, if available, mcq options from the card object
		question, answer, options = self.format_question(card)

		#Display the question
		Label(self.root, text=question, font=('Ariel', 20, 'bold'), bg='white',
			wraplength=640, justify='center').place(x=140, y=120)

		#Answer section of flash card
		#Created according to question type
		if options is None:		#Question type 0 or input question
			#Creating region for user to type in their answer
			
			Label(self.root, text='Enter your answer here:', font=('Ariel',15, 'italic'),
				bg='white').place(x=320, y=280)
			self.answer_box = Entry(self.root,bd=4, relief=RIDGE, width=40, font=('Ariel', 12))
			self.answer_box.place(x=240, y=320, height=40)
			self.answer_value = None

		else:					#Question type 1 or MCQ question
			#Creating region with radio buttons for user to choose one of  options
			
			Label(self.root, text='Choose one of the following:', font=('Ariel', 15, 'italic'),
				bg='white').place(x=320, y=280)

			self.answer_value = StringVar(self.root)	
			x_positions = [130, 310, 450, 630]
			y_position = 320

			for i in range(len(options)):
				Radiobutton(self.root, text=str(options[i]), variable=self.answer_value, 
					value=options[i], font=('Ariel', 12), bg='white').place(x=x_positions[i], y=y_position)

		#Submit the answer button
		Button(self.root, text='Submit', font=('Ariel', 12, 'bold'),
			command=lambda: self.check_answer(answer,card)).place(x=390, y=370)

		#End the session question
		Button(self.root, text='End session', font=('Ariel', 12, 'bold'),
			command=self.exit_session).place(x=760,y=10)

	def exit_session(self): #End the flashcard quiz by destroying the root panel
		logger.info('Session ended before answering all questions')
		self.root.destroy()

	def check_answer(self, correct_answer, card):
		'''
		Takes the user data and compares it to the answer inside the card object. 
		If they match:
			- The user gets a correct answer message 
			- The correct answer for the session is recorded 
			- The card's history attribute is updated 
		If they don't match:
			- The user gets an incorrect answer message 
			- The card's history attribute is updated 

		Then it is checked if the total number of questions has been presented so far. 
		If the current question is the last question for the session, the user gets a completion message and session ends. 
		Else, the next question is presented through the user of run_card method after updated the current question number.

		Args:
			correct_answer: 	the correct answer to the current question
			card:				the card whose question is currently being answered
		'''

		#Two different question types gives two different method to get user answer
		try:
			if hasattr(self, 'answer_box') and self.answer_box.winfo_exists(): #Input type question answer
				user_answer = self.answer_box.get()								#Getting the user input
				self.answer_box.delete(0, END)									#Clearing the Entry box
			else:																#MCQ type question answer
				user_answer = self.answer_value.get()							#Getting the radiobutton value for the option

			#Checking if user answer the question correctly
			result = self.is_correct(user_answer, card.get_answer())

			if result:											#correct answer
				messagebox.showinfo('Info', 'Your answer is correct.', parent=self.root)
				self.correct_answers += 1
				card.session_result(True) #Updating card history
			else:												#Incorrect answer
				messagebox.showerror('Error', 'Your answer is incorrect.', parent=self.root)
				card.session_result(False) #Updating card history

			self.curr_question += 1 		#Moving to next question
			if self.curr_question < self.num:							#Question left to be asked
				logger.info(f'Asking the {self.curr_question} question')
				self.run_card(self.session_cards[self.curr_question])	#Asking the next question
			else:							#Session complete
				messagebox.showinfo('Completed', 'Congratulations on completing this session.')
				logger.info('Quiz session complete')
				self.root.destroy()

		except ValueError: #Making sure that user entered something/prevents unexcpected error to stop the quiz
			messagebox.showerror('Error', 'Please enter a valid answer.', parent=self.root)


	def format_question(self, card):
		'''
		Unpacks the question form card object. 
		Ensures random question type. If random question type does not exist, return the present question. 
		Returns question, answer and options (which is None if input type question)
		'''

		answer = card.get_answer()
		mcq_options = None 

		question_type = [0,1]
		random.shuffle(question_type)

		question = card.get_question(question_type[0])
		q_type = question_type[0]

		if question == None:
			question = card.get_question(question_type[1])
			q_type = question_type[1]

		if q_type == 1:
			mcq_all = question.split(',')
			question = mcq_all[0]
			mcq_options = [answer, mcq_all[1], mcq_all[2], mcq_all[3]]
			random.shuffle(mcq_options)

		return question, answer, mcq_options

	def get_stat(self):  				#User stat for total questions correct 
		return self.correct_answers

	def is_correct(self, user_input, correct_answer):
		answer = correct_answer.strip().lower()
		userinput = user_input.strip().lower()

		#splitting the correct answer 
		correct_cases = re.split(r'[,\s\-\.:;]', answer)

		#creating regex pattern using the split parts of answer to match to user input 
		pattern = ''.join(f'(?=.*{re.escape(case)})' for case in correct_cases)
		full_pattern = f'^{pattern}.*$'

		#matching the userinput against pattern
		match = re.match(full_pattern, userinput, flags=re.IGNORECASE)

		if match:
			return True 	#correct answer
		else:
			return False 	#incorrect answer
			