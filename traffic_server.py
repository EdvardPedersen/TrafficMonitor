from flask import Flask, request, render_template, session, redirect, url_for, abort, send_file
import trafficmon_service as tf
import argparse
import imp
from algorithm_factory import Factory as algFac
import io

def serve_web():
	traffic = tf.Manager()
	traffic.add_user("Testman")
	serv = Flask(__name__)
	
	def before_req():
		traffic.update_all_cams()
		return
	
	@serv.route('/')
	def main_menu():
		username = request.args.get('username', '')
		if(username != ''):
			session['username'] = username
			traffic.add_user(username)
		if check_session():
			return redirect(url_for('camera_list'))
		return render_template('index.html')
	
	@serv.route('/cams')
	def camera_list():
		if not check_session():
			return redirect(url_for('main_menu'))
		cams = dict()
		for cam in traffic.users[session['username']].get_cameras():
			cams[cam] = traffic.cameras[cam]
		return render_template('index.html', cameras=cams)
	
	@serv.route('/register', methods=['POST', 'GET'])
	def register_cam():
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
		if(traffic.cameras[cam_id].output_image == False):
			return
		(retval, img) = traffic.cameras[cam_id].output_image
		return send_file(io.BytesIO(img), mimetype="image/png")
		
			
	
	@serv.route('/subscribe')
	def subscribe_cam():
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
				sortedList.append((long(0.0), key, element))
		sortedList.sort(key=lambda element: element[0])
		return render_template('index.html', subcams = sortedList)
	
	@serv.route('/unsubscribe')
	def unsubscribe_cam():
		if not check_session():
			return redirect(url_for('main_menu'))
		cam = request.args.get('cam', '')
		if(cam != ''):
			traffic.unsubscribe_camera(session['username'], cam)
		return redirect(url_for('camera_list'))
	
	@serv.route('/logout')
	def logout():
		session.pop('username', None)
		return redirect(url_for('main_menu'))
	
	def check_session():
		if('username' in session):
			return True
		return False
	
	serv.secret_key = 'This is a secret key'
	
	serv.before_request(before_req)

	serv.run(debug=True, use_reloader=False)
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="TrafficMonitor web service")
	args = parser.parse_args()

	serve_web()
