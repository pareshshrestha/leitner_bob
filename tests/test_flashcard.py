#! python3
#! test_flashcard.py - Pytest for ensuring that flashcard acts as expected 

import pytest
from unittest.mock import patch, MagicMock

from app.models import Card, Box
import app.logic as logic
from app.flashcard import FlashCard

from tkinter import *

@pytest.fixture
def mock_root():
	root = Tk()
	root.withdraw()

	yield root

	root.destroy()

@pytest.fixture
def mock_box():

	mock_box = Box()
	card1 = Card('4', ['What is 2+2?', None])
	card2 = Card('Paris', [None,'What is the capital of France?,London,Berlin,Rome'])
	card3 = Card('Egg', ['Why can you not eat raw cookie dough?', 'Why can you not eat raw cookie dough?,flour,sugar,chocolate'])

	mock_box.box1.append(card1)
	mock_box.box1.append(card2)
	mock_box.box1.append(card3)
	
	return mock_box

@pytest.fixture
def flashcard_instance(mock_root, mock_box):
	with patch('app.logic.get_session_cards', return_value = [mock_box.box1[0],mock_box.box1[1],mock_box.box1[2]]) as mock_get_cards:
		fc = FlashCard(mock_root,mock_box,3)
		yield fc 

def test_innit(mock_root, mock_box, flashcard_instance):
	assert flashcard_instance.root == mock_root
	assert flashcard_instance.box == mock_box
	assert flashcard_instance.num == 3
	assert flashcard_instance.session_cards == mock_box.box1

def test_format_question(mock_box, flashcard_instance):
	card_input = mock_box.box1[0]
	
	question, answer, options = flashcard_instance.format_question(card_input)

	assert question == 'What is 2+2?'
	assert answer == '4'
	assert options == None

def test_format_question_mcq(mock_box, flashcard_instance):
	card_mcq = mock_box.box1[1]

	with patch('random.shuffle', side_effect=lambda x:None):
		mcq_question, mcq_answer, mcq_options = flashcard_instance.format_question(card_mcq)

	assert mcq_question == 'What is the capital of France?'
	assert mcq_answer == 'Paris'
	assert mcq_options == ['Paris','London','Berlin','Rome']

def test_check_answer_correct_input(mock_box, flashcard_instance):

	card = mock_box.box1[0]

	flashcard_instance.answer_box = MagicMock()
	flashcard_instance.answer_box.get.return_value = '4'
	flashcard_instance.answer_box.winfo_exists.return_value = True 

	flashcard_instance.curr_question = 0
	flashcard_instance.num = 3

	with patch('tkinter.messagebox.showinfo') as mock_showinfo:
		with patch.object(flashcard_instance, 'run_card') as mock_run_card:
			
			flashcard_instance.check_answer(card.get_answer(), card)

			mock_showinfo.assert_called_once()

			assert flashcard_instance.correct_answers == 1 
			assert card.history[-1] == True 
			assert flashcard_instance.curr_question == 1 

			mock_run_card.assert_called_once()

def test_check_answer_incorrect_input(mock_box, flashcard_instance):
	card = mock_box.box1[0]

	flashcard_instance.answer_box = MagicMock()
	flashcard_instance.answer_box.get.return_value = '2'
	flashcard_instance.answer_box.winfo_exists.return_value = True 

	flashcard_instance.curr_question = 0
	flashcard_instance.num = 3

	with patch('tkinter.messagebox.showerror') as mock_showerror:
		with patch.object(flashcard_instance, 'run_card') as mock_run_card:
			
			flashcard_instance.check_answer(card.get_answer(), card)

			mock_showerror.assert_called_once()

			assert flashcard_instance.correct_answers == 0
			assert card.history[-1] == False
			assert flashcard_instance.curr_question == 1 

			mock_run_card.assert_called_once()

def test_check_answer_correct_mcq(mock_box, flashcard_instance):

	card = mock_box.box1[1]

	flashcard_instance.answer_box = MagicMock()
	flashcard_instance.answer_box.winfo_exists.return_value = False

	flashcard_instance.answer_value = MagicMock()
	flashcard_instance.answer_value.get.return_value = 'Paris'

	flashcard_instance.curr_question = 0
	flashcard_instance.num = 3

	with patch('tkinter.messagebox.showinfo') as mock_showinfo:
		with patch.object(flashcard_instance, 'run_card') as mock_run_card:

			flashcard_instance.check_answer('Paris', card)

			mock_showinfo.assert_called_once()

			assert flashcard_instance.correct_answers == 1
			assert card.history[-1] == True 
			assert flashcard_instance.curr_question == 1

			mock_run_card.assert_called_once()

def test_check_answer_incorrect_mcq(mock_box, flashcard_instance):

	card = mock_box.box1[1]

	flashcard_instance.answer_box = MagicMock()
	flashcard_instance.answer_box.winfo_exists.return_value = False

	flashcard_instance.answer_value = MagicMock()
	flashcard_instance.answer_value.get.return_value = 'London'

	flashcard_instance.curr_question = 0
	flashcard_instance.num = 3

	with patch('tkinter.messagebox.showerror') as mock_showerror:
		with patch.object(flashcard_instance, 'run_card') as mock_run_card:

			flashcard_instance.check_answer(card.get_answer(), card)

			mock_showerror.assert_called_once()

			assert flashcard_instance.correct_answers == 0
			assert card.history[-1] == False
			assert flashcard_instance.curr_question == 1

			mock_run_card.assert_called_once()

def test_completion(mock_box,flashcard_instance):
	card = mock_box.box1[0]

	flashcard_instance.answer_box = MagicMock()
	flashcard_instance.answer_box.get.return_value = '4'
	flashcard_instance.answer_box.winfo_exists.return_value = True 

	flashcard_instance.curr_question = 3
	flashcard_instance.num = 3

	flashcard_instance.root = MagicMock()
	flashcard_instance.root.destroy = MagicMock()

	with patch('tkinter.messagebox.showinfo') as mock_showinfo:
		with patch.object(flashcard_instance, 'run_card') as mock_run_card:
			
			flashcard_instance.check_answer(card.get_answer(), card)

			assert mock_showinfo.call_count == 2

			flashcard_instance.root.destroy.assert_called_once()
