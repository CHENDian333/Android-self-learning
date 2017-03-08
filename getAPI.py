from flask import jsonify,Flask,request
import MyDatabase
import time
import math

app = Flask(__name__)

@app.route('/api/asgn3/get_chatrooms', methods=['GET'])
def get_chatrooms():
	mydb = MyDatabase.MyDatabase()

	query = "SELECT * FROM chatrooms"
	mydb.cursor.execute(query)

	chatroom_list = mydb.cursor.fetchall()
	
	return jsonify(status="OK",data=chatroom_list)

@app.route('/api/asgn3/get_messages', methods=['GET'])
def get_messages():
	mydb = MyDatabase.MyDatabase()
	message_list = []

	chatroom_id = request.args.get("chatroom_id", 0, type=int) 
	page = request.args.get("page", 1, type=int)

	query = "SELECT chatroom_id,user_id,name,message,timestamp FROM messages WHERE chatroom_id = %s ORDER BY  id desc"
	params = (chatroom_id)
	mydb.cursor.execute(query,params)

	count = 0
	total_page = 1
	count_msg = 0
	while 1:
		message = mydb.cursor.fetchone()
		if message is None :
			break
		else :
			message_list.append(message)
		count+=1
		
		if count > 10*total_page:
			total_page = total_page + 1
		if count > 10:
			count_msg = count - (total_page-1)*10
		else:
			count_msg+=1
	
	chat_message = []
	if page == total_page:
		for j in range(count_msg):
			chat_message.append(message_list[(page-1)*10+j])
	elif page < total_page:
		for i in range(10):
			chat_message.append(message_list[(page-1)*10+i])
		
	return jsonify(status="OK",total_pages=total_page,page = page,data=chat_message)

@app.route('/api/asgn3/send_message', methods=['POST'])
def send_message():
	mydb = MyDatabase.MyDatabase()
	msg = request.form.get("message")
	name = request.form.get("name")
	chatroom_id = request.form.get("chatroom_id")
	user_id = request.form.get("user_id")

	if msg == None or chatroom_id == None or chatroom_id == '' or not chatroom_id.isdigit() or name == None or user_id == None :
		return jsonify(status="ERROR", message="missing parameters")
	else :
		insert_query = "INSERT INTO messages (chatroom_id,user_id,name,message,timestamp) VALUES (%s,%s,%s,%s,%s)"

		params = (chatroom_id,user_id,name,msg,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()+8*3600)))
		mydb.cursor.execute(insert_query,params)
		mydb.db.commit()
		return jsonify(status="OK")
	
if __name__ == '__main__': 
	app.run(host='0.0.0.0')





