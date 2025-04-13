#! python3
# test_window.py - Pytests for window.py

import pytest
from unittest.mock import MagicMock, patch

from tkinter import *

from app.models import Card, Box
from app.window import QuestionWindow, QuestionListbox

'''
First section of tests: Testing Question Window
'''
@pytest.fixture
def setup_window():

	root = Tk()
	root.withdraw()
	
	box = Box()
	window = QuestionWindow(root, box)

	window.enter_question = MagicMock()
	window.enter_mcq = MagicMock()
	window.enter_mcq_options = MagicMock()
	window.enter_answer = MagicMock()

	yield (root, box, window)
	root.destroy()

@patch('tkinter.messagebox.showerror')
def test_no_answer(mock_error, setup_window):
	root, box, window = setup_window

	window.enter_answer.get.return_value = ""
	window.enter_question.get.return_value = "Sample question"
	window.enter_mcq.get.return_value = ""

	window.submit_question(None)

	mock_error.assert_called_once()

@patch('tkinter.messagebox.showerror')
def test_no_questions(mock_error, setup_window):
	root, box, window = setup_window

	window.enter_answer.get.return_value = "test answer"
	window.enter_question.get.return_value = ''
	window.enter_mcq.get.return_value = ''
	window.enter_mcq_options.get.return_value = 'option1,option2,option3'

	window.submit_question(None)

	mock_error.assert_called_once()

@patch('tkinter.messagebox.showerror')
def test_no_mcq_options(mock_error, setup_window):
	root, box, window = setup_window

	window.enter_answer.get.return_value = "test answer"
	window.enter_question.get.return_value = 'test input question'
	window.enter_mcq.get.return_value = 'test mcq question'
	window.enter_mcq_options.get.return_value = ''

	window.submit_question(None)

	mock_error.assert_called_once()

@patch('tkinter.messagebox.showinfo')
def test_no_mcq(mock_info,setup_window):
	root, box, window = setup_window

	window.enter_answer.get.return_value = "test answer"
	window.enter_question.get.return_value = 'test question'
	window.enter_mcq.get.return_value = ''
	window.enter_mcq_options.get.return_value = ''

	window.submit_question(None)

	card = box.box1[0]

	assert card.answer == 'test answer'
	assert card.questions[0] == 'test question'

@patch('tkinter.messagebox.showinfo')
def test_no_input(mock_info,setup_window):
	root, box, window = setup_window

	window.enter_answer.get.return_value = "test answer"
	window.enter_question.get.return_value = ''
	window.enter_mcq.get.return_value = 'test mcq'
	window.enter_mcq_options.get.return_value = 'option1,option2,option3'

	window.submit_question(None)

	card = box.box1[0]

	assert card.answer == 'test answer'
	assert card.questions[1] == 'test mcq,option1,option2,option3'

@pytest.fixture
def setup_window_with_card():

	root = Tk()
	root.withdraw()

	box = Box()
	card = Card('test answer',
		['test question', 'test mcq,option1,option2,option3'])

	window = QuestionWindow(root, box, card)

	yield (root, box, card, window)

	root.destroy()

@patch('tkinter.messagebox.showinfo')
def test_passing_card(mock_info, setup_window_with_card):
	root, box, card, window = setup_window_with_card

	assert window.enter_answer.get() == 'test answer'
	assert window.enter_question.get() == 'test question'
	assert window.enter_mcq.get() == 'test mcq'
	assert window.enter_mcq_options.get() == 'option1,option2,option3'

'''
Second section of tests: Testing QuestionListbox
'''

@pytest.fixture
def setup_listbox_window():
	def create_window(type):
		root = Tk()
		root.withdraw()

		box = Box()
		for i in range(5):
			box.box1.append(Card(f'answer{i+1}', [f'question{i+1}', None]))

		window = QuestionListbox(root, box, type)

		window.select_box = MagicMock()

		return root, box, type, window

	yield create_window

@patch('tkinter.messagebox.showerror')
def test_no_selected_box(mock_error, setup_listbox_window):
	root, box, type, window = setup_listbox_window("EDIT")

	window.select_box.get.return_value = ''

	window.display_questions()

	mock_error.assert_called_once()
	root.destroy()

@patch('tkinter.messagebox.showerror')
def test_no_selected_card(mock_error, setup_listbox_window):
	root, box, type, window = setup_listbox_window('EDIT')

	window.select_box.get.return_value = '1'

	window.display_questions()

	card = window.question_listbox.get(0)
	assert card == box.box1[0].get_question(0)

	#test condition of no card selected
	window.edit_selected_question()

	mock_error.assert_called_once()
	root.destroy()

@patch('app.window.QuestionWindow')
def test_edit_question(mock_question_window, setup_listbox_window):
	root, box, type, window = setup_listbox_window('EDIT')
	root.withdraw()
	window.select_box.get.return_value = '1'

	window.display_questions()

	window.question_listbox = MagicMock()
	window.question_listbox.curselection.return_value = (0,)

	window.edit_selected_question()

	mock_question_window.assert_called_once_with(root, box, box.box1[0])
	root.destroy()

@patch('tkinter.messagebox.showinfo')
def test_delete_question(mock_info, setup_listbox_window):
	root, box, type, window = setup_listbox_window('DELETE')
	window.select_box.get.return_value = '1'

	window.display_questions()

	window.question_listbox = MagicMock()
	window.question_listbox.curselection.return_value = (0,)

	window.delete_selected_question()

	assert box.box1[0].get_answer() == 'answer2'
	root.destroy()