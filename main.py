import app.access as access
from app.gui import LeitnerApp

if __name__ == '__main__':
	username = access.get_username()
	app = LeitnerApp(username)
	app.run()

	



