from index import *
try:
	database()
	connection  = database().connect()
	Base.metadata.create_all(bind=database())
	app.run()
except exc.OperationalError:
	print("Database doesn't exists or username/password incorrect")