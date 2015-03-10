import pygame
import xml.etree.ElementTree as et
import cv2
import numpy as np
import urllib as ur
import random
import time

class User:
	def __init__(self, uid):
		self.user_id = uid
		self.cameras = dict()
		self.cam_len = 0

	def register_camera(self, cam):
		self.cameras[self.cam_len] = cam
		self.cam_len += 1
		return self.cam_len - 1 

	def register_algorithm(self, cid, algorithm):
		self.cameras[cid].set_algorithm(algorithm)

	def get_camera(self, cid):
		return self.cameras[cid].get_image()

	def update(self, force=False):
		for (cid, cam) in self.cameras.items():
			print("CID: " + str(cid) + " CAM" + str(cam))
			if(time.time() - cam.last_updated > cam.update_interval or force):
				cam.update()

class Camera:
	def __init__(self, url, interval=0.0, prev_image=False):
		self.subset = False
		self.image = False

		self.update_interval = interval
		self.prev_image = prev_image
		self.url = url

		self.last_updated = time.time()
		self.alg = Algorithm()

		self.update()


	def update(self):
		self.last_updated = time.time()
		(f,h) = ur.urlretrieve(self.url)
		tempImage = cv2.imread(f)
		if(self.subset):
			tempImage = tempImage[self.subset[1][0]:self.subset[1][1], self.subset[0][0]:self.subset[0][1]]
		if(isinstance(tempImage, np.ndarray) and isinstance(self.image, np.ndarray) and tempImage.shape == self.image.shape):
			if(np.bitwise_xor(tempImage, self.image).any()):
				self.prev_image = self.image
				self.image = tempImage
		elif(isinstance(self.image, bool)):
			self.image = tempImage
		elif(tempImage.shape != self.image.shape):
			self.image = tempImage
		self.image = self.alg.process(self.image, self.prev_image)
			

	def set_subset(self, x, y):
		self.subset = ((x[0],x[1]), (y[0],y[1]))

	def get_image(self):
		return self.image

	def set_algorithm(self, algorithm):
		self.alg = algorithm

	def get_keypoints(self):
		return self.alg.keypoints

	def get_image_keypoints(self):
		return cv2.drawKeypoints(self.image, self.alg.keypoints)

class Algorithm:
	def __init__(self, sensitivity=30):
		self.name = "None"
		self.keypoints = list()

	def process(self, cur_image, prev_image=False):
		return cv2.cvtColor(cur_image, cv2.COLOR_BGR2GRAY)

class TrafficAlg(Algorithm):
	def __init__(self, sensitivity=30):
		self.name = "Traffic algorithm"
		self.sensitivity = sensitivity
		self.engine = cv2.BRISK(sensitivity)
		self.keypoints = list()

	def process(self, cur_image, prev_image=False):
		image = cv2.equalizeHist(cv2.cvtColor(cur_image, cv2.COLOR_BGR2GRAY))
		if(not isinstance(prev_image, np.ndarray)):
			return image
		last_image = cv2.equalizeHist(cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY))
		(ret,diff_image) = cv2.threshold(cv2.absdiff(image, last_image), 50, 255, cv2.THRESH_TOZERO)
		self.keypoints = self.engine.detect(diff_image)
		return diff_image

class Manager():
	def __init__(self, filename="default"):
		self.users = dict()
		self.cameras = dict()
		self.algorithms = list()
		self.filename=filename
		if(filename):
			self._loadfromfile(filename)
		
	
	def _load_from_file(filename):
		print("STUB: Loading user data from disk")

	def _save_to_file():
		

	def _register_algs(self):
		print ("STUB: Registering algorithms")

	def test(self):
		return "Testing Manager"

if __name__ == "__main__":
	user = User("Edvard")

	cid1 = user.register_camera(Camera("http://weather.cs.uit.no/cam/cam_east.jpg"))
	user.cameras[cid1].set_subset((800,1200),(500,670))
	user.register_algorithm(cid1, TrafficAlg())

	user.register_camera(Camera("http://webkamera.vegvesen.no/kamera?id=674473"))

	user.update(force=True)
	for cam in user.cameras.values():
		cv2.namedWindow(cam.url, cv2.CV_WINDOW_AUTOSIZE)
		cv2.imshow(cam.url, cam.get_image())
	man = Manager()
	man._register_algs()
	cv2.waitKey()
