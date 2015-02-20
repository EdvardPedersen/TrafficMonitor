import flask
import trafficmonitor_service as tf
import argparse

def serve_web():
	traffic = tf.Manager()
	serv = Flask("Test web server")
	
	@serv.route('/user/<user_id>')
	def 

if __name__ == "__main__":
	parser = argparse.ArugmentParser(description="TrafficMonitor web service")
	args = parser.parse_args()


