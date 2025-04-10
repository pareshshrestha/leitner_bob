#! python3
# logic.py - Handles the core leitner logic. 
#				- Returns the correct number of cards per session from correct boxes. 
#				- Arranges the cards in boxes according to their history

from app.models import Card, Box 
import random

def get_session_cards(box: Box, total_question:int)-> list:
	'''
	Returns list of questions from boxes 1 - 5 according leitner logic and user requested difficulty level. 
	The 4 difficulty levels are 10, 20, 50 and 100 questions.
	'''

	session_cards = []

	#logic for how many quesiton from box 1-5 according to total cards of the session
	if total_question == 10:
		box_allocation = [4, 3, 2, 1, 0]
	elif total_question == 20:
		box_allocation = [8, 6, 4, 2, 0]
	elif total_question == 50:
		box_allocation = [20, 14, 9, 5, 2]
	else:
		box_allocation = [40, 28, 18, 10, 4]

	curr_num = 0 #record of how many questions need to be loaded
	
	for i in range(5, 0, -1): #working in reverse: in beginning box3-5 might not have enough questions
		if box_allocation[i-1] == 0: #if zero questions are required, skip logic
			continue
		else:
			curr_num = curr_num + box_allocation[i-1]
			box_length = len(box.boxlist[i-1])

			if curr_num <= box_length: #there are enough questions in the box to fulfill requirement
				cards = random.sample(box.boxlist[i-1], curr_num)
				session_cards.extend(cards)
				curr_num = 0 #all required questions got
			else: #not enough questions
				if box_length == 0:
					continue
				else:
					session_cards.extend(box.boxlist[i-1])
					curr_num -= box_length #number of cards required remaining

	random.shuffle(session_cards) #shuffle the questions
	return session_cards

def arrange_boxes(box: Box): 
	'''
	Loops through all the boxes and their cards. 
	Checks their history and sums up correct questions. 
	According to the sum of successful attemps, arranges into the 1-5 boxes according to leitner logic. 
	The logic being, the more times you get it correct the higher numbered box it will end up in.
	'''

	cards_to_move = []

	for box_index, individual_box in enumerate(box.boxlist):
		for card in individual_box:

			card_value = sum(card.get_history())

			if card_value >= 8:
				target_box = 5
			elif card_value >= 6:
				target_box = 4
			elif card_value >= 4:
				target_box = 3
			elif card_value >=2:
				target_box = 2
			else:
				target_box = 1

			if card.box != target_box:
				cards_to_move.append((card, target_box))

	for card, target_box in cards_to_move:
		box.change_box(card, target_box)