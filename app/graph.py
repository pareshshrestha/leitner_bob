#! python3
# graph.py - 	File that handles the GUI implementation of the visualization of user's session success

import matplotlib.pyplot as plt 
import numpy as np 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from app.app_logging import get_logger
logger = get_logger(__name__)

def create_graphframe(root, userdata):
	'''
	Handles all the GUI application of the graphframe. 
	Processes the user data to create an display a line graph displaying the data. 

	Args:
		userdata: User data stored in the user file
	'''
	logger.info('Creating the graph frame')
	#Check if the user already has activity history, if not create 40 empty (0%) data points
	try:
		session_data = userdata['session_data']
	except KeyError:
		userdata['session_data'] = [0]*40
		session_data = userdata['session_data']
		logger.warning('session_data not found in userdata. Initializing 40 zero values')

	#Taking only the last 40 data points(last 40 sessions), if more than 40 exist, to display in the graph
	if len(session_data) >= 40:
		session_data = session_data[-40:]

	#Creating the line graph

	sessions = np.arange(1, len(session_data)+1)
	fig, ax = plt.subplots(figsize=(13.22, 1.6))

	ax.plot(sessions, session_data, marker="o", linestyle='-', linewidth=4, 
		color ='#4CAF50', markersize=6, label="Success %")

	ax.set_title('User\'s Progress', fontsize=10, fontweight='bold')
	ax.set_ylabel('Success %', fontsize=9)

	ax.set_xticks(range(0, 41, 5))
	ax.set_ylim(0, 100)
	ax.grid(True, linestyle='--', alpha=0.6)
	ax.legend(fontsize=8)

	fig.subplots_adjust(bottom=0.15, top=0.9)
	plt.tight_layout(pad=0.5)

	#Displaying the graph in the frame
	canvas = FigureCanvasTkAgg(fig, master=root)
	canvas.draw()
	canvas.get_tk_widget().pack(fill='both', expand=True)

	return canvas #Return the canvas so it can be updated later