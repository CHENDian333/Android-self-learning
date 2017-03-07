import MySQLdb
class MyDatabase: 
	db = None
	def __init__(self): 
		self.connect()
		return
	def connect(self):
		self.db = MySQLdb.connect(
				host = "localhost", 
				port = 3306,
				user = "root",
				passwd = "123", 
				db = "iems5722" 
				use_unicode = True,
				charset = "utf8",
			)
		self.cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
		self.db.commit()
		return