#!python3

import logging
import os

log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs') #creating a file path for the log files
os.makedirs(log_dir, exist_ok=True)	#making dir for logs
log_file = os.path.join(log_dir, 'app.log')	#Ensuring the log file is created inside the log folder

#Setting up the logger with its format, level and file where it will be saved
logging.basicConfig(
	level = logging.INFO,
	format='%(asctime)s -%(name)s - %(levelname)s - %(message)s',
	handlers =[
		logging.StreamHandler(),
		logging.FileHandler(log_file)
	]
)

#method to create a logger for each file individually
def get_logger(name):
	return logging.getLogger(name)
