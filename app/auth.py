#! python3

import hashlib 
from cryptography.fernet import Fernet
import json, os 

#file names
KEY_FILE = 'secret.key' #file that contains the key
USER_DB_FILE = 'user.enc'	# .enc or encrypted file

def generate_key():
	if not os.path.exists(KEY_FILE):
		key = Fernet.generate_key()
		with open(KEY_FILE, 'wb') as key_file:
			key_file.write(key)

def load_key():
	return open(KEY_FILE, 'rb').read()

def hash_password(password):
	return hashlib.sha256(password.encode()).hexdigest()

def load_users():
	if not os.path.exists(USER_DB_FILE):
		return {}

	with open(USER_DB_FILE, 'rb') as file:
		decrypted_data = cipher.decrypt(file.read()).decode()
		return json.loads(decrypted_data)

def save_users(users):
	encrypted_data = cipher.encrypt(json.dumps(users).encode())
	with open(USER_DB_FILE, 'wb') as file:
		file.write(encrypted_data)

generate_key()
cipher = Fernet(load_key())
users = load_users()

def register(username_input, password_input) -> bool:

	if username_input in users.keys():
		return False

	users[username_input] = password_input
	save_users(users)
	return True

def login(username_input, password_input) -> bool:

	if len(username_input) < 5 or len(password_input) < 5:
		return False
	elif username_input in users.keys() and users[username_input] == password_input:
		return True
	else:
		return False

	