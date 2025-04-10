#!python3
#test_logic.py - Testing the leitner logic 

import pytest
from app.logic import get_session_cards, arrange_boxes
from app.models import Card, Box

@pytest.fixture
def sample_box():
	test_box = Box()
	for i in range(5):
		for _ in range(50):
			card = Card(f'answer{i+1}', [f'question{i+1}', None])
			card.box = i+1
			test_box.boxlist[i].append(card)	

	return test_box 

def test_get_session_cards(sample_box):
	ten_questions = get_session_cards(sample_box, 10)
	assert len(ten_questions) == 10

	card_box_record = [0,0,0,0,0]
	for card in ten_questions:
		box_num = card.box 
		card_box_record[box_num-1] += 1

	assert card_box_record == [4, 3, 2, 1, 0]

	fifty_questions = get_session_cards(sample_box, 50)
	assert len(fifty_questions) == 50

	card_box_record = [0,0,0,0,0]

	for card in fifty_questions:
		box_num = card.box 
		card_box_record[box_num-1] += 1

	assert card_box_record == [20, 14, 9, 5, 2]

def test_arrange_boxes():
	box = Box()

	for i in range(5):
		card = Card(f'answer{i+1}', ['question{i+1}',None])
		card.history = [0,0,0,0,0,0,0,0,0,i*2]
		box.box1.append(card)

	assert len(box.box1) == 5

	arrange_boxes(box)

	for index, box in enumerate(box.boxlist):
		assert len(box) == 1
		card = box[0]
		assert card.get_answer() == f'answer{index+1}'



	