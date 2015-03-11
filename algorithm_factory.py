import cv2
import numpy as np

class Algorithm:
	''' The "none" algorithm, does virtually nothing '''
	name = "None"
	description = "Algorithm that returns a black and white image"
	id = "none"
	def __init__(self, sensitivity=30):
		self.keypoints = list()

	def process(self, cur_image, prev_image=False):
		return cv2.cvtColor(cur_image, cv2.COLOR_BGR2GRAY)

class TrafficAlg(Algorithm):
	''' Traffic algorithm, for detecting traffic level '''
	name = "Traffic algorithm"
	description = "Algorithm for detecting traffic using SIFT"
	id = "traffic"
	def __init__(self, sensitivity=30):
		Algorithm.__init__(self)
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

class Factory():
	''' 
		Static class for listing and getting instances of algorithms 
		Close your eyes if you like idiomatic python
	'''
	algs = dict()
	algs["traffic"] = TrafficAlg
	algs["none"] = Algorithm
	
	@staticmethod
	def get_alg(alg):
		''' Returns the algorithm matching the given input, the "none" algorithm if the given algorithm is not found '''
		if(alg in Factory.algs):
			return Factory.algs[alg]()
		else:
			return Factory.algs["none"]()
	
	@staticmethod
	def __str__():
		''' Simple string representation of the algorithm factory '''
		retString = "Algorithm factory containing algs: \n"
		for key in Factory.algs:
			retString += Factory.algs[key].description + "\n"
		return retString
	
	@staticmethod
	def get_printable():
		''' Returns a dict with the following form: output[algorithm_id] = (algorithm_name, algorithm_description) '''
		printable = dict()
		for key in Factory.algs:
			printable[key] = (Factory.algs[key].name, Factory.algs[key].description)

if __name__ == "__main__":
	fac = Factory()
	print(fac)
	ta = fac.get_alg("traffic")
	print(ta)