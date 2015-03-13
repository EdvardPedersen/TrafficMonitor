#import pygame
import json
import cv2
import numpy as np
import urllib as ur
import random
import time
from algorithm_factory import Factory as algFac
import gdbm as dbm
import pickle
import os
import math

class User:
	""" Class that maintains a list of cameras a user is subscribed to """
	def __init__(self, uid):
		""" uid is the name of the user that is used to log in """
		self.user_id = uid
		self.cameras = list()
		
	def add_cameras(self, cams):
		""" Set the user's cameras to the list passed in """
		self.cameras = cams

	def register_camera(self, cam):
		""" Subscribe to the given camera ID """
		if(cam not in self.cameras):
			self.cameras.append(cam)
		return cam
	
	def unregister_camera(self, cam):
		""" Unsubscribe from a camera """
		if(cam in self.cameras):
			self.cameras.remove(cam)
		return cam

	def get_cameras(self):
		return self.cameras

class Camera:
	""" Camera class, contains information about a camera, as well as a reference to algorithm, and images """
	def __init__(self, name=None, url=None, interval=30.0, prev_image=False, dbm_input=None, lat=None, lon=None):
		""" Constructor uses dbm_input when loading from disk, other values otherwise 
			Not a very elegant solution
		"""
		if(dbm_input != None):
			# Load data from dbm
			self._init_dbm(dbm_input)
		else:
			self.subset = False
			self.name = name
			self.url = url
			self.alg = algFac.get_alg("none")
			try:
				# Try/catch to avoid malformed values for lat and lon
				self.latitude = float(lat)
				self.longitude = float(lon)
			except:
				self.latitude = None
				self.longitude = None

		self.update_interval = interval
		self.image = False
		self.output_image = False
		self.prev_image = prev_image
		self.last_updated = time.time()
		self.updated_string = time.ctime()
		self.activity = "0"
		self.update()
		
	def _init_dbm(self, dbm_repr):
		""" Loads a camera from a dbm representation, used when loading from disk """
		self.name = dbm_repr["name"]
		self.subset = dbm_repr["subset"]
		self.url = dbm_repr["url"]
		self.update_interval = dbm_repr["interval"]
		self.alg = algFac.get_alg(dbm_repr["algorithm"])
		try:
			self.latitude = float(dbm_repr["lat"])
			self.longitude = float(dbm_repr["lon"])
		except (ValueError, TypeError):
			self.latitude = None
			self.longitude = None
		
	def get_distance(self, other_lat, other_lon):
		""" Gets the distance in kilometers between the camera and a given lat/lon coordinate """
		# Taken from http://stackoverflow.com/questions/27928/how-do-i-calculate-distance-between-two-latitude-longitude-points
		if(self.latitude == None or self.longitude == None):
			return 10000.0
		radius_of_earth = 6371.0
		oLat = math.radians(float(other_lat))
		oLon = math.radians(float(other_lon))
		sLat = math.radians(float(self.latitude))
		sLon = math.radians(float(self.longitude))
		dLat = oLat - sLat
		dLon = oLon - sLon
		a = (math.sin(dLat/2)**2 + math.cos(sLat) * math.cos(oLat) * math.sin(dLon/2)**2)
		c = 2 * math.asin(math.sqrt(a))
		return radius_of_earth * c

	def get_dbm(self):
		""" Get the json representation of this camera """
		json_repr = dict()
		json_repr["name"] = self.name
		json_repr["subset"] = self.subset
		json_repr["url"] = self.url
		json_repr["interval"] = self.update_interval
		json_repr["algorithm"] = self.alg.id
		json_repr["lat"] = self.latitude
		json_repr["lon"] = self.longitude
		return json.dumps(json_repr)

	def update(self):
		""" Runs the detection algorithm and updates images, quite expensive, so should only be called at self.interval """
		self.last_updated = time.time()
		self.updated_string = time.ctime()
		(f,h) = ur.urlretrieve(self.url)
		# TODO: Remove the disk access, do it in memory
		tempImage = cv2.imread(f)
		if(self.subset):
			tempImage = tempImage[self.subset[1][0]:self.subset[1][1], self.subset[0][0]:self.subset[0][1]]
		if(isinstance(tempImage, np.ndarray) and isinstance(self.image, np.ndarray) and tempImage.shape == self.image.shape):
			# Make sure both the current image and the new image are not the same before updating
			if(np.bitwise_xor(tempImage, self.image).any()):
				self.prev_image = self.image
				self.image = tempImage
		elif(isinstance(self.image, bool)):
			self.image = tempImage
		elif(tempImage.shape != self.image.shape):
			self.image = tempImage
		self.processed_image = self.alg.process(self.image, self.prev_image)
		self.activity = str(len(self.alg.keypoints))
		# The output image is in memory, encoded in PNG format
		self.output_image = cv2.imencode(".png", self.processed_image)
			

	def set_subset(self, x, y):
		""" Selects a subset of the image to use for processing, takes in a tuple of x and y values """
		self.subset = ((x[0],x[1]), (y[0],y[1]))

	def set_algorithm(self, algorithm):
		""" Takes an algorithm, sets the cameras algorithm to this algorithm """
		self.alg = algorithm

class Manager():
	""" The manager class ties the user, cameras and algorithms together, contains a set of each """
	def __init__(self, filename="default"):
		""" Reads users and cameras from disk, and initializes dicts """
		self.users = dict()
		self.cameras = dict()
		self.maxCamId = 0
		self.algorithms = algFac
		self.filename=filename
		
		self.user_db = dbm.open(filename + ".user", 'cs')
		self.camera_db = dbm.open(filename + ".camera", 'cs')
		
		self._load_from_file()
		
	
	def add_user(self, name):
		""" Add a single user to the system, saves to file if the user is new """
		if(name in self.users):
			return False
		else:
			self.users[name] = User(name)
			self._save_to_file()
			return True
	
	def add_camera(self, cam_name, cam_url, subset=None, algorithm=None, cam_lat=None, cam_lon=None):
		""" Add a camera to the system, saves to file, note that duplicates can be added """
		newCamera = Camera(name=cam_name, url=cam_url, lat=cam_lat, lon=cam_lon)
		if(subset):
			newCamera.set_subset(subset[0], subset[1])
		if(algorithm):
			newCamera.set_algorithm(self.algorithms.get_alg(algorithm))
			
		self.cameras[str(self.maxCamId)] = newCamera
		self.maxCamId += 1
		self._save_to_file()
		return self.maxCamId - 1
	
	def subscribe_camera(self, user, cam):
		""" Subscribes a user to a camera """
		self.users[user].register_camera(cam)
		self._save_to_file()
		
	def unsubscribe_camera(self, user, cam):
		""" Unsubscribes a user from a camera """
		self.users[user].unregister_camera(cam)
		self._save_to_file()
	
	def _load_from_file(self):
		""" Load users and cameras from disk """
		key = self.camera_db.firstkey()
		while key != None:
			if(int(key) >= self.maxCamId):
				self.maxCamId = int(key) + 1
			self.cameras[key] = Camera(dbm_input=json.loads(self.camera_db[key]))
			key = self.camera_db.nextkey(key)
			
		key = self.user_db.firstkey()
		while key != None:
			self.users[key] = User(key)
			self.users[key].add_cameras(json.loads(self.user_db[key]))
			key = self.user_db.nextkey(key)

	def _save_to_file(self):
		""" Save users and cameras to disk """
		for (key,value) in self.cameras.items():
			self.camera_db[key] = value.get_dbm()
			
		for (key, value) in self.users.items():
			self.user_db[key] = json.dumps(value.get_cameras())
			
	def update_cameras(self, user_id):
		""" 
			Updates all the cameras a user is subscribed to, not currently used,
			but is needed when there are more cameras.
			Only updates cameras that have not been updated in camera.interval seconds
		"""
		for cam_id in self.users[user_id].get_cameras():
			camera = self.cameras[cam_id]
			if(time.time() - camera.last_updated > camera.update_interval):
				camera.update()
				
	def update_all_cams(self):
		""" Updates all cameras that have not been updated in camera.interval seconds """
		cur_time = time.time()
		for (cam_id, cam) in self.cameras.items():
			if(cur_time - cam.last_updated > cam.update_interval):
				cam.update()

if __name__ == "__main__":
	man = Manager()
	#man.add_user("Edvard")
	#cid = man.add_camera("Rundkjoring breivika", "http://weather.cs.uit.no/cam/cam_east.jpg", ((800,1200),(500,670)), "traffic")
	#man.subscribe_camera("Edvard", "0")
	#man.add_camera("TestCam", "http://weather.cs.uit.no/cam/cam_east.jpg", algorithm="traffic", cam_lat="10", cam_lon="20")
	print(man.cameras)
	
	print(man.cameras["0"].get_dbm())
	
	print(man.cameras["0"].get_distance("69.65", "18.95"))
	
	print(man.users["Edvard"].cameras)
	
	

	man.update_cameras("Edvard")
	for cam in man.users["Edvard"].cameras:
		man.cameras[cam].update()
		cv2.namedWindow(man.cameras[cam].url, cv2.CV_WINDOW_AUTOSIZE)
		#cv2.imshow(man.cameras[cam].url, man.cameras[cam].output_image)
	cv2.waitKey()
