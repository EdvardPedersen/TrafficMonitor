from flask import Flask, request, render_template, session, redirect, url_for, abort, send_file
import trafficmon_service as tf
import argparse
import imp
from algorithm_factory import Factory as algFac
import io

def serve_web():
	""" Web server implementation using Flask """
	traffic = tf.Manager()
	serv = Flask(__name__)
	
	def before_req():
		""" 
			Update all cameras before every request
			If the interval for cameras is set to 0, this adds a huge latency to requests
		"""
		traffic.update_all_cams()
		return
	
	@serv.route('/')
	def main_menu():
		""" Handles the login, redirect to camera list if logged in """
		username = request.args.get('username', '')
		if(username != ''):
			session['username'] = username
			traffic.add_user(username)
		if check_session():
			return redirect(url_for('camera_list'))
		return render_template('index.html')
	
	@serv.route('/cams')
	def camera_list():
		""" Shows the list of cameras, the logic is in index.html """
		if not check_session():
			return redirect(url_for('main_menu'))
		cams = dict()
		for cam in traffic.users[session['username']].get_cameras():
			cams[cam] = traffic.cameras[cam]
		return render_template('index.html', cameras=cams)
	
	@serv.route('/register', methods=['POST', 'GET'])
	def register_cam():
		""" 
			Register a new camera for use
			GET returns the creation interface
			POST adds the camera to the manager, and returns to the camera list
		"""
		#TODO: Improve user interface
		#TODO: Add selection of subset
		if not check_session():
			return redirect(url_for('main_menu'))
		
		if(request.method == 'GET'):
			return render_template('createcam.html', algorithms=algFac.algs)
		else:
			alg = request.form['alg']
			url = request.form['url']
			desc = request.form['desc']
			lat = request.form['lat']
			lon = request.form['lon']
			try:
				traffic.add_camera(desc, url, algorithm=alg, cam_lat=lat, cam_lon=lon)
			except IOError:
				return redirect(url_for('camera_list'))
			return redirect(url_for('camera_list'))
	
	@serv.route('/img/<cam_id>')
	def serve_image(cam_id):
		""" Serves images from memory, they are already encoded as PNG """
		if(traffic.cameras[cam_id].output_image == False):
			return
		(retval, img) = traffic.cameras[cam_id].output_image
		return send_file(io.BytesIO(img), mimetype="image/png")
		
			
	
	@serv.route('/subscribe')
	def subscribe_cam():
		""" 
			Either list the cameras that can be subscribed to (in order of distance)
			or return to the camera list if there is data in the request
		"""
		if not check_session():
			return redirect(url_for('main_menu'))
		cam = request.args.get('cam', '')
		if(cam != ''):
			traffic.subscribe_camera(session['username'], cam)
			return redirect(url_for('camera_list'))
		newlist = dict()
		for element in traffic.cameras:
			newlist[element] = traffic.cameras[element]
			
		lat = request.args.get('lat', '')
		lon = request.args.get('lon', '')
		
		
		sortedList = list()
		comparelist = traffic.users[session['username']].get_cameras()
		for (key, element) in traffic.cameras.items():
			if(lat != '' and lon != '' and key not in comparelist):
				sortedList.append((long(element.get_distance(lat, lon)), key, element))
			elif(key not in comparelist):
				# Using 10000 km as the "magic token" for "no geolocation data at one end"
				sortedList.append((long(10000.0), key, element))
		sortedList.sort(key=lambda element: element[0])
		return render_template('index.html', subcams = sortedList)
	
	@serv.route('/unsubscribe')
	def unsubscribe_cam():
		""" Unsubscribe from a camera, redirects to the camera list """
		if not check_session():
			return redirect(url_for('main_menu'))
		cam = request.args.get('cam', '')
		if(cam != ''):
			traffic.unsubscribe_camera(session['username'], cam)
		return redirect(url_for('camera_list'))
	
	@serv.route('/logout')
	def logout():
		""" Logs the user out of the session, returns to login """
		session.pop('username', None)
		return redirect(url_for('main_menu'))
	
	def check_session():
		""" Utility function to check if the user is logged in """
		if('username' in session):
			return True
		return False
	
	# Not a very good key...
	serv.secret_key = 'This is a secret key'
	
	# Register the before_req function to be called before every request
	serv.before_request(before_req)

	# Run the server, open to the world, on port 80
	# Remove the arguments to run the server only for localhost, and on port 5000
	serv.run(host='0.0.0.0', port=80)
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="TrafficMonitor web service")
	args = parser.parse_args()

	serve_web()
