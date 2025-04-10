#! python3
# test_models.py - 	Tests for models for Lietner app. 
#					Test for class Card and Box.
#					Cardlist and box creations is done many times
#					because the tests were not being conducted in correct order and sending errors

import pytest
from app.models import Card, Box

#Card object to be tested
test_card = Card('answer', ['question1', 'question2'])

#testing the card creation
def test_card_creation():
	assert test_card.answer == 'answer'
	assert test_card.questions[0] == 'question1'
	assert test_card.questions[1] == 'question2'
	assert test_card.box == 1
	assert len(test_card.history) == 10
	for session in test_card.history:
		assert session == 0

#testing all get* functions
def test_get_functions():
	assert test_card.get_answer() == 'answer'
	assert test_card.get_question(0) == 'question1'
	assert test_card.get_question(1) == 'question2'
	assert len(test_card.get_history()) == 10 

#testing the correct recording of card history 
def test_session_result():
	#testing correct answer record
	test_card.session_result(True)
	history = test_card.get_history()
	assert history[9] == 1 		#newest record should be 1 or correct
	assert len(history) == 10	#new record should not increase history length

	#testing incorrect answer record 
	test_card.session_result(False)
	history = test_card.get_history()
	assert history[9] == 0		#newest record should be 0 or incorrect
	assert len(history) == 10	#total length should remain 10, constant	

#testing changing box state function
def test_change_box():
	assert test_card.box == 1
	test_card.change_box(2)		#changing box
	assert test_card.box == 2	#making sure the change is registered

#testing to_dict function
def test_to_dict():
	card_dict = test_card.to_dict()
	assert type(card_dict) == dict 
	assert card_dict['answer'] == test_card.get_answer()
	assert card_dict['questions'] == ['question1', 'question2']
	assert card_dict['box'] == test_card.box 
	assert card_dict['history'] == test_card.get_history()

#testing box creation without card list
def test_box_creation():
	#Box object to be tested 
	test_box = Box()

	assert len(test_box.boxlist) == 5
	for i in range(5):
		box_name = f'box{i+1}'
		assert hasattr(test_box, box_name)
	for box in test_box.boxlist:
		assert box == []

def test_box_creation_withCards():
	#creating a card list for creation test with cards
	cards = [] #card list

	#making cards and have then be in all 5 boxes 
	for i in range(5):
		card = Card(f'answer{i+1}', [f'question{i+1}', None])
		card.change_box(i+1)
		cards.append(card)

	#making box object with card list 
	test_box2 = Box(cards)

	for i in range(5):
		card = test_box2.boxlist[i][0] #getting card per box 
		assert card.get_answer() == f'answer{i+1}'

def test_change_box():
	#creating a card list for creation test with cards
	cards = [] #card list

	#making cards and have then be in all 5 boxes 
	for i in range(5):
		card = Card(f'answer{i+1}', [f'question{i+1}', None])
		card.change_box(i+1)
		cards.append(card)

	test_box3 = Box(cards)
	#get card to be moved to new box
	card = test_box3.box1[0]

	#moving the card from box1 to box2
	test_box3.change_box(card, 2)

	assert len(test_box3.box2) == 2 	#checking if card moved
	assert test_box3.box2[1].get_answer() == 'answer1'	#checking if the card moved is the right now
	assert test_box3.box2[1].box == 2 	#checking if the internal value is changed accordingly

def test_add_question():
	#creating a card list for creation test with cards
	cards = [] #card list

	#making cards and have then be in all 5 boxes 
	for i in range(5):
		card = Card(f'answer{i+1}', [f'question{i+1}', None])
		card.change_box(i+1)
		cards.append(card)

	test_boxFour = Box(cards)

	test_boxFour.add_question('answer0', ['question0',None])
	assert len(test_boxFour.box1) == 2
	assert test_boxFour.box1[1].get_answer() == 'answer0'


        