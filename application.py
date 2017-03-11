from flask import Flask
from flask import render_template
from flask.ext.socketio import emit
from flask.ext.socketio import SocketIO
from elasticsearch import Elasticsearch
import threading
import twitter_stream

elastic = Elasticsearch([{'host':'search-tweet-map-sibehtynscobaboaftsayz6vwy.us-west-2.es.amazonaws.com', 'port':80}])
# if elastic.indices.exists(index = 'tweet_test') :
    # elastic.indices.delete(index = 'tweet_test')
# mapping = {
# 	'mappings' : {
# 		'tweets' : {
# 			'properties' : {
# 				'create_date' : {
# 					'type' : 'date',
# 					'format' : 'yyyy-MM-dd HH:mm:ss'
# 				},
# 				'coordinates' : {
# 					'type' : 'geo_point'
# 				}
# 			}
# 		}
# 	}
# }
# elastic.indices.create(index = 'tweet_test', ignore = 400, body = mapping)


application = Flask(__name__)
socketio = SocketIO(application)


@application.route('/')
def get_index_page():
	return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
	print 'conntected!'
	send_thread = Send_Thread()
	send_thread.start()

@socketio.on('search', namespace='/test')
def search_keyword(data):
	print data
	result = elastic.search(
	index = 'tweet_test',
	doc_type='tweets',
	body={
		'query': {
			'match' : {
				'text' : data['data']
			}
		}
    })
	socketio.emit('search_response', {'data': result['hits']['hits']}, namespace = '/test')

@socketio.on('my event', namespace='/test')
def test_message(message):
	print message

class Send_Message(object):
	def sending(self):
		while True:
			socketio.emit('my_response', {'data': 2}, namespace = '/test')

class Send_Thread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		my_stream = twitter_stream.My_Stream(elastic, socketio)
		my_stream.run()

if __name__ == "__main__":
	socketio.run(application)