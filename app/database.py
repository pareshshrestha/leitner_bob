#! python3
#database.py - Handles all file loading and saving for leitnerbox app.

import json, os, random
from app.models import Card, Box

from app.app_logging import get_logger
logger = get_logger(__name__)

class Database:
	'''
	Database class. 
	Takes one value: username.
	Has functions following functions:
		check_dir() :		Checks if a folder exists for the username. 
							If not present, creates a folder with the username inside /leitner_bob/data.
							The folder contains 5 files (box1.json to box5.json) and a username.json file that stores user usage data.
		load_userdata():	Loads user activity data. Specifically data for number of successful answers per session.	
							And data for user's pomodoro activity. 
							Saved inside 'session_data' and 'pomodoro' as keys.
							Returns it as a dictionary.
		save_userdata(userdata):Saves the user activity data.
								Takes a dictionary to save the data in it.	
		load_cards(Box):		First saves data currently in the boxes and cards. 
							Then sequencially opens the files for the 5 boxes, selects 50 questions per file, 
							deletes the selected questions from files, creates Card objects for the questions,
							and finally adds them to the correct attribute (box1 for example) inside
							the Box object passed when calling the function.
		save_cards(Box):	Takes a Box object. 
							Iterates over the 5 boxes saved as attributes. 
							Calls the to_dict() for each card to get the dictionary format of the Card objets.
							Appends the dictionary to the correct box file (e.g. box1.json). 
							After saving, changes the passed Box object into an empty Box object.
	'''

	def __init__(self, username:str):
		self.username = username
		self.filenames = ['box1.json', 'box2.json', 'box3.json', 'box4.json', 'box5.json']
		logger.debug(f'Initializing Database for user: {username}')
		try:
			self.basepath = self.get_basepath('data') #file path for all files created in the class
			self.check_dir() #checking file dir exists, else create one with username and default files
			logger.info(f'Database initialized for user: {self.username}.')
		except Exception as e:
			logger.error(f'Failed to initialize database for user: {username}: {str(e)}')
			raise

	def get_basepath(self, base:str) -> str:
		'''
		Uses os.path to find the current working directory of the user. 
		Then uses os.path.join to create cwd/leitner_bob/data.
		Returns the joined path.
		'''
		try:
			base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', base)
			logger.debug(f'Base path determined: {base_dir}')
			return os.path.abspath(base_dir)
		except Exception as e:
			logger.error(f'Failed to determine base path: {str(e)}')
			raise

	def check_dir(self): #checks if a dir exists for the username
		user_path = os.path.join(self.basepath, self.username)
		logger.debug(f'Checking if dir exists: {user_path}')

		if not os.path.exists(user_path):
			logger.info(f'No dir found for {self.username}. Creating a dir and default files.')
			try:
				os.mkdir(user_path) #makes dir with the username 
				logger.debug(f'Dir created: {user_path}')
				self.create_default_files(user_path) #creates the default files for the username
			except PermissionError:
				logger.error(f'Permission denied when creating directory for {self.username}')
				raise
			except Exception as e:
				logger.error(f'Failed to create dir for {self.username}: {str(e)}')
				raise
		else:
			logger.debug(f'A dir and relevant files already exist for {self.username}.')

	def create_default_files(self, user_path):
		'''
		Creates default files for the lietner_app for the username. 
		The default files are:
			- files for leitner boxes (e.g. box1.json to box5.json)
			- file for user usage data (username.json)
		All box files are started with [] and all data will be appended or deleted from list.
		username.json file is started as a dict {} and all data will be appended to the list returned 
		for the keys 'session_data' and 'pomodoro'.
		'''
		try:
			for filename in self.filenames: #iterating through all the file names
				file_path = os.path.join(user_path, filename)
				with open(file_path, 'w') as file: #creating json file for the filename
					json.dump([], file, indent=4) #starting the list for data to be stored
					logger.debug(f'Created file {file_path}')

			with open(os.path.join(user_path, f'{self.username}.json'), 'w') as file: #creating username.json file
				json.dump({}, file, indent=4) #saved as dict 
				logger.debug(f'New {self.username}.json file created for {self.username}.')

			logger.info(f'All default files created for {self.username}')
		except IOError as e:
			logger.error(f'IO error when creating default files for {self.username}: {str(e)}')
			raise
		except Exception as e:
			logger.error(f'Unexpected error when creating default files for {self.username}: {str(e)}')
			raise

	def load_userdata(self) -> dict:
		'''
		Reads the username.json file and returns the read data. 
		The data in the file is a dict with keys 'session_data' and 'pomodoro'.
		'session_data' saves data regarding % of correct answer per session. 
		'pomodoro' saves data regarding total seconds spent in focus time by uesr.
		'''
		userdata_path = os.path.join(self.basepath, self.username, f'{self.username}.json')
		logger.debug(f'Loading user data from : {userdata_path}')

		try:
			with open(userdata_path, 'r') as file:
				userdata = json.load(file)
			logger.info(f'User data loaded successfully for {self.username}')
			return userdata
		except FileNotFoundError:
			logger.warning(f'Userdata file not found for {self.username}. Returning empty dict.')
			return {}
		except json.JSONDecodeError:
			logger.error(f'Invalid JSON in user data file for {self.username}')
			return {}
		except Exception as e:
			logger.error(f'Failed to load user data for {self.username}: {str(e)}')
			raise

	def save_userdata(self, userdata:dict):
		'''
		Takes the user's action data saved as a dict with keys 'session_data' for % correct answers and
		'pomodoro' for focus time. Then it stores the value in the file {username}.json.
		'''
		userdata_path = os.path.join(self.basepath, self.username, f'{self.username}.json')
		logger.debug(f'Saving user data to: {userdata_path}')

		try:
			with open(userdata_path,'w') as file:
				json.dump(userdata, file, indent=4)
				logger.info(f'Userdata stored successfully for {self.username}.')
		except IOError as e:
			logger.error(f'IO error when saving user data for {self.username}: {str(e)}')
			raise
		except Exception as e:
			logger.error(f'Failed to save user data for {self.username}: {str(e)}')
			raise

	def save_cards(self, box: Box):
		'''
		Takes Box object. 
		Opens files according to the box attributes in Box object. 
		Loads the Card object data from the file, appends the data in the Box object to the loaded data, 
		and finally writes in the same file again.
		Empties the box attribute of Box object after the data in it is saved.
		'''
		logger.info(f'Saving Card data for {self.username}')

		for i in range(5): #going over 5 files and 5 box attributes 
			file_path = os.path.join(self.basepath, self.username, self.filenames[i])
			logger.debug(f'Saving Card data for box{i+1} in {file_path}')

			try:
				logger.info(f'First loading prexisting data from {file_path}')
				with open(file_path, 'r') as file:
					existing_data = json.load(file)
			except (FileNotFoundError, json.JSONDecodeError) as e:
				logger.warning(f'Could not read existing data for box {i+1}: {str(e)}. Starting with empty list.')
				existing_data = []

			logger.debug(f'Adding Card data from box{i+1} to existing data')
			for card in box.boxlist[i]:
				existing_data.append(card.to_dict()) #adding new data to old data

			try:
				with open(file_path, 'w') as file:
					json.dump(existing_data, file, indent=4) #writing both old and new data
				logger.debug(f'Successfully saved Card data for box{i+1} in {file_path}')
			except IOError as e:
				logger.error(f'Failed to save Card data for box {i+1}: {str(e)}')
				raise

			box.boxlist[i] = [] #clearing out the box so there's no data duplication if data is loaded again
			logger.debug(f'Cleared all data from box{i+1}')

	def load_cards(self, box:Box):
		'''
		Takes a Box object and fills it with Card objects made with data in .json files. 
		As we do not want data to be lost or data duplication, we first save data already present in the Box.
		Then we load the data from the files. We load data worth 50 Cards at a time. 
		Then the chosen data for 50 cards is removed from the data inside the files to ensure no data duplication.
		'''
		logger.info(f'Loading cards for {self.username}')

		if len(box.box1) > 0 or len(box.box2) > 0: #checking if box currently holds data (unlikely 2 boxes will be empty)
			logger.debug(f'Box contains existing data. Saving data before loading new cards.')
			self.save_cards(box) #saving data to make sure data is not lost or duplicated

		for i in range(5):
			file_path = os.path.join(self.basepath, self.username, self.filenames[i]) #creating file path per box
			logger.debug(f'Loading Cards from {file_path}')
			try:
				with open(file_path,'r') as file:
					all_data = json.load(file)
				logger.debug(f'File ({file_path}) successfully read for card data.')
			except (FileNotFoundError, json.JSONDecodeError):
				logger.error(f'Could not read data for box{i+1}: {str(e)}. Starting with empty list.')
				all_data = []

			logger.info(f'Attempting to select 50 cards worth of data.')
			select_data = random.sample(all_data, min(50, len(all_data))) #selecting data for 50 Cards randomly
			logger.debug(f'{len(select_data)} data for cards selected for box{i+1}')

			try:
				cards = [Card(data['answer'], data['questions'], data['history'], data['box']) for data in select_data] #card creation
				logger.debug(f'Created {len(cards)} Card objects for box{i+1}')
			except Exception as e:
				logger.error(f'Faield to create Card objects for box{i+1}: {str(e)}')
				continue

			remaining_data = [data for data in all_data if data not in select_data] #sorting data that is not selected to ensure no data duplication
			try:
				with open(file_path, 'w') as file:
					json.dump(remaining_data, file, indent=4)
				logger.debug(f'Updated box {i+1} file with the unselected data')
			except Exception as e:
				logger.error(f'Failed to update box {i+1} file after card selection. All data lost: {str(e)}')
				continue
			try:
				box.boxlist[i].extend(cards)
				logger.debug(f'Box{i+1} successfully extended with newly created Cards')
			except Exception as e:
				logger.error(f'Failed to populate box{i+1} attribute with created Cards: {str(e)}')

		logger.info(f'Successfully loaded cards for {self.username}')




