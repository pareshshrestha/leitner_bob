#!python3
# test_database.py - Testing the database.py 

import os, json, pytest, shutil
from unittest.mock import patch, mock_open, MagicMock

from app.database import Database 
from app.models import Card, Box

#Fixutre for 'data' path 
@pytest.fixture
def test_data_path():
	base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')

	#Setup: create directory if it doesn't exist
	if not os.path.exists(base_path):
		os.mkdir(base_path)

	yield base_path

	#Teardown: clean up after tests
	if os.path.exists(base_path):
		shutil.rmtree(base_path)

#mock the base path to use our test directory
@pytest.fixture
def mock_database(test_data_path):
	with patch.object(Database, 'get_basepath', return_value=test_data_path):
		db = Database('test_user')
		yield db 

		#teardown 
		user_path = os.path.join(test_data_path, 'test_user')
		if os.path.exists(user_path):
			shutil.rmtree(user_path)

#Fixture for a Box object 
@pytest.fixture
def sample_box():
	box = Box()

	for i in range(5):
		card = Card(
			f'Answer {i}',
			[f'Question {i}', None]
		)
		box.box1.append(card)
	return box 

def test_database_creation(mock_database):
	assert mock_database.username == 'test_user'
	assert mock_database.filenames == ['box1.json', 'box2.json', 'box3.json', 'box4.json', 'box5.json']

	#checking username based dir 
	user_path = os.path.join(mock_database.basepath, 'test_user')
	assert os.path.exists(user_path)

	#checking creation os default files 
	for filename in mock_database.filenames:
		file_path = os.path.join(user_path, filename)
		assert os.path.exists(file_path)

	#checking username.json file
	user_data_path = os.path.join(user_path, 'test_user.json')
	assert os.path.exists(user_data_path)

def test_check_dir(test_data_path):
	user_path = os.path.join(test_data_path, 'existing_user')

	with patch.object(Database, "get_basepath", return_value=test_data_path):
		db = Database('existing_user')

		assert os.path.exists(user_path)

		for filename in db.filenames:
			file_path = os.path.join(user_path, filename)
			assert os.path.exists(file_path)

		user_data_path = os.path.join(user_path, 'existing_user.json')
		assert os.path.exists(user_data_path)

	#cleanup
	shutil.rmtree(user_path)

def test_load_userdata_newuser(mock_database):

	user_data_path = os.path.join(mock_database.basepath, 'test_user', 'test_user.json')
	with open(user_data_path, 'w') as f:
		json.dump({},f)

	data = mock_database.load_userdata()
	assert data == {}

def test_load_userdata_existing_user(mock_database):

	mock_data = {"session_data":[60,70], "pomodoro":600}

	user_data_path = os.path.join(mock_database.basepath,'test_user', 'test_user.json')
	with open(user_data_path, 'w') as f:
		json.dump(mock_data, f)

	data = mock_database.load_userdata()
	assert data == mock_data
	assert 'session_data' in data
	assert 'pomodoro' in data 
	assert data['session_data'][0] == 60

def test_save_userdata(mock_database):

	user_data_path = os.path.join(mock_database.basepath, 'test_user', 'test_user.json')
	with open(user_data_path, 'w') as f:
		json.dump({},f)

	userdata = {"session_data":[60,70], 
	"pomodoro":600}

	mock_database.save_userdata(userdata)

	data = mock_database.load_userdata()
	assert data == {"session_data":[60,70], 
	"pomodoro":600}

def test_save_cards(mock_database, sample_box):

	mock_database.save_cards(sample_box)

	box1_path = os.path.join(mock_database.basepath, 'test_user', 'box1.json')
	with open(box1_path, 'r') as f:
		data = json.load(f)

	assert len(data) == 5

	assert data[0]['answer'] == "Answer 0"
	assert data[0]['questions'] == ["Question 0", None]
	assert len(data[0]['history']) == 10

	for box in sample_box.boxlist:
		assert len(box) == 0

	for i in range(5):
		file_path = os.path.join(mock_database.basepath, 'test_user', f'box{i+1}.json')
		with open(file_path, 'r') as f:
			data = json.load(f)

			if i == 0:
				assert len(data) == 5
			else:
				assert len(data) == 0

def test_load_cards(mock_database):

	for i in range(5):
		card = Card(f'answer{i+1}', [f'question{i+1}'])
		file_path = os.path.join(mock_database.basepath, 'test_user', f'box{i+1}.json')
		with open(file_path, 'w') as f:
			json.dump([card.to_dict()], f)

	box = Box()
	mock_database.load_cards(box)

	for i in range(5):
		card = box.boxlist[i][0]
		assert card.get_answer() == f'answer{i+1}'
		assert card.get_question(0) == f'question{i+1}'

	#check for if files are empty as everything is loaded
	for i in range(5):
		file_path = os.path.join(mock_database.basepath, 'test_user', f'box{i+1}.json')
		with open(file_path, 'r') as f:
			data = json.load(f)
			assert len(data) == 0

def test_load_cards_many(mock_database):
	cardlist = []
	for i in range(60):
		card = Card(f'answer{i}', [f'question{i}', None])
		cardlist.append(card) 

	box = Box()
	box.box1.append(Card('answer0', ['question0', None]))
	box.box2.extend(cardlist)

	mock_database.save_cards(box)

	box_other = Box()
	mock_database.load_cards(box_other)

	assert len(box_other.box1) == 1
	assert len(box_other.box2) == 50

	box2_path = os.path.join(mock_database.basepath, 'test_user', 'box2.json')
	with open(box2_path, 'r') as file:
		data = json.load(file)
		assert len(data) == 10  












