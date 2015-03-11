from flask import Flask, request, render_template, session, redirect, url_for
import trafficmon_service as tf
import argparse
import imp

def serve_web():
	traffic = tf.Manager()
	traffic.add_user("Testman")
	serv = Flask(__name__)
	
	@serv.route('/')
	def main_menu():
		username = request.args.get('username', '')
		if(username != ''):
			session['username'] = username
			traffic.add_user(username)
		return render_template('index.html')
	
	@serv.route('/cams')
	def camera_list():
		if not check_session():
			return redirect(url_for('main_menu'))
		cams = dict()
		for cam in traffic.users[session['username']].get_cameras():
			traffic.cameras[cam].update()
			cams[cam] = traffic.cameras[cam]
		return render_template('index.html', cameras=cams)
	
	@serv.route('/users')
	def user_list():
		if not check_session():
			return redirect(url_for('main_menu'))
		list_of_users = traffic.users.values()
		#for user in traffic.users.values():
		#	list_of_users.append(user.user_id)
		return render_template('index.html', users=list_of_users)
	
	@serv.route('/register')
	def register_cam():
		if not check_session():
			return redirect(url_for('main_menu'))
		
		return render_template('index.html')
	
	@serv.route('/subscribe')
	def subscribe_cam():
		if not check_session():
			return redirect(url_for('main_menu'))
		
		return render_template('index.html')
	
	@serv.route('/logout')
	def logout():
		session.pop('username', None)
		return redirect(url_for('main_menu'))
	
	def check_session():
		if('username' in session):
			return True
		return False
	
	serv.secret_key = 'This is a secret key'

	serv.run(debug=True, use_reloader=False)
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="TrafficMonitor web service")
	args = parser.parse_args()

	serve_web()
