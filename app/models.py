#! python3
#models.py - Contains the implementation of Card and Box classes.

from app.app_logging import get_logger
logger = get_logger(__name__)

class Card:
	'''
	Class Card: It holds the data for the question and answer. 
				It also holds the identity of which box it is currently in.
	Properties:
	answer:		It is a string and can be in the form of a word or text but is always in string. 

	questions:	It is a list of questions. 
				Input questions or 0 (questions that take in user input through entry)
				Multiple choice or 1 (questions that show multiple options and you have to choose the right one)
				If the type of question does not exist, there will be a None in it's place.

	
	'''
	def __init__(self, answer: str, questions: list=[None,None], history = None, box:int = 1):
		self.answer = answer 
		self.questions = questions #checking and assigning valid questions only
		self.history = [0]*10 if history is None else history #makes sure history is present for 10 sessions
		self.box = box  #Box levels from 1 to 5, new cards are in level 1
		logger.info(f'Card created with answer: {self.get_answer}, in box: {self.box}')

	def get_answer(self):
		return self.answer

	def get_question(self, type:int=0):
		return self.questions[type] #returns quesiton according to type

	def session_result(self, result:bool):
		'''
		Takes the True or False for session result for one question. True is correct answer and False is wrong.
		Then it updates the self.history for the card by appending the new value (1 for True, 0 for False)
		and removing the first value to create a record for the last 10 sessions only.
		'''
		if result:
			self.history.append(1) #record of correct answer
			logger.info(f'Correct answer recorded for card: {self.get_answer}')
		else:
			self.history.append(0) #record of incorrect answer
			logger.info(f'Incorrect answer recorded for card: {self.get_answer}')
		
		del self.history[0] #removing the oldest record
		logger.debug(f'Updated history for card {self.answer}.') 

	def change_box(self, new_box:int):
		'''
		Changes the internal value of which box the card is contained in.
		'''
		self.box = new_box

	def to_dict(self):
		'''
		Returns a dictionary of the card attributes. 
		Details: {'answer':str or int, 'questions': list[question0, question1],
		'box': int, 'history': list[0 and 1s]}
		'''
		return {'answer':self.answer, 'questions':self.questions, 'box':self.box, 'history':self.history}

	def get_history(self):
		return self.history

class Box:
	'''
	Class Box:	Holds five boxes filled with Card objects. 
	
	'''
	def __init__(self, cardlist:list[Card]=None):
		self.box1 = []
		self.box2 = []
		self.box3 = []
		self.box4 = []
		self.box5 = []
		self.boxlist = [self.box1, self.box2, self.box3, self.box4, self.box5] #list of boxes for iterations
		logger.info('An empty leitner box if created successfully.')

		if cardlist is not None: #save cards in respective boxes if a list of card objects is given
			for card in cardlist:
				box_index = card.box-1
				self.boxlist[box_index].append(card)
				logger.info(f'Card {card.get_answer} added to box: {card.box}.')

	def change_box(self, card:Card, new_box:int):
		'''
		Removes the card from the old box and appends it to the list of new box. 
		Also changes the internal box value of the  card.
		'''
		curr_box_index = card.box - 1
		self.boxlist[curr_box_index].remove(card) #removing card from old box 
		self.boxlist[new_box-1].append(card)	#adding card to the new box 
		card.change_box(new_box) 				#changing the internal value of box correctly


		logger.info(f'Card with answer: {card.get_answer()} is moved from box {card.box} to {new_box}')

	def add_question(self, answer:str, question:list):
		'''
		Takes the answer and question(s) and creates a card object from it. 
		It also appends it to box 1 (as it has no record of sessions)
		'''
		new_card = Card(answer, question) #creating card object
		self.box1.append(new_card)	#adding card object to the correct box
		logger.debug(f'Card for answer {new_card.get_answer} and question "{new_card.questions}" created and added to box1.')










	