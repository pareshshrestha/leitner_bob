#! python3

from tkinter import *
from tkinter import messagebox
import app.auth as auth
from PIL import ImageTk, Image

#global variable
USERNAME = None 

def register():
	username = entry_username.get()
	password = entry_password.get()

	if len(username) < 5:
		messagebox.showerror('Error', 'Please use a longer username.')
	elif len(password) < 5:
		messagebox.showerror('Error', 'Please user a longer password.')
	else:
		register_result = auth.register(username, password)

		if register_result: 
			messagebox.showinfo('Success', 'User registered Successfully.\nLogin to Use B.O.B')
		else:
			messagebox.showerror('Error', 'Registration failed.')

def login():
	global USERNAME 

	username = entry_username.get()
	password = entry_password.get()

	login_result = auth.login(username, password)

	if login_result:
		messagebox.showinfo('Success', 'Login successful.')
		login_window.destroy()
		USERNAME = username 
	else:
		messagebox.showerror('Error', 'Incorrect username or password.')

def get_username():
	global USERNAME
	return USERNAME
'''
GUI implementation is in the same file to reduce file count and keep it secure.
'''
login_window = Tk()
login_window.title("B.O.B LOGIN WINDOW")
login_window.geometry("800x500")
login_window.config(bg='white')
login_window.resizable(width = False, height = False)

tiles = Image.open('assets/tiles.png')
logo = ImageTk.PhotoImage(tiles)
logo_label = Label(login_window, image = logo, bd = 0)
logo_label.pack(side = TOP)

username_label = Label(login_window, text = 'Username:', bg='white', font = ('Ariel'))
password_label = Label(login_window, text = 'Password:', bg='white', font = ('Ariel'))

entry_username = Entry(login_window, bd = 2)
entry_password = Entry(login_window, show='*', bd = 2)

login_button = Button(login_window, text = 'LogIn', command = login, padx=4, pady=2)
signup_button = Button(login_window, text = 'Signup', command = register, padx=4, pady=2)

new_user_label = Label(login_window, text = 'New User?', bg = 'white')

login_window.bind('<Return>', lambda event = None: login())

username_label.place(x = 247, y = 320)
password_label.place(x = 250, y = 350)

entry_username.place(x=330, y=320)
entry_password.place(x=330, y=350)

login_button.place(x=350, y=385)
new_user_label.place(x=343, y=415)
signup_button.place(x=347, y=440)

login_window.mainloop()

