from flask import Flask, request, render_template
import trafficmon_service as tf
import argparse
import imp

def serve_web():
	traffic = tf.Manager()
	serv = Flask("Test web server")
	
	@serv.route('/test')
	def test_tf():
		return traffic.test()

	serv.run()
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="TrafficMonitor web service")
	args = parser.parse_args()

	serve_web()
