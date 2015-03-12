import cv2
import numpy as np

class Algorithm:
	""" The "none" algorithm, does nothing """
	name = "None"
	description = "Algorithm that does nothing"
	id = "none"
	def __init__(self, sensitivity=30):
		self.keypoints = list()

	def process(self, cur_image, prev_image=False):
		""" Method that does any processing, none in this case """
		return cur_image

class TrafficAlg(Algorithm):
	""" Traffic algorithm, for detecting traffic level """
	name = "Traffic algorithm"
	description = "Algorithm for detecting traffic using SIFT"
	id = "traffic"
	def __init__(self, sensitivity=30):
		""" Initializes the engine used """
		Algorithm.__init__(self)
		self.sensitivity = sensitivity
		self.engine = cv2.BRISK(sensitivity)
		self.keypoints = list()

	def process(self, cur_image, prev_image=False):
		""" Generates a diff between two images, and does keypoint detection on that """
		# EqualizeHist enhances contrast, we use a grayscale version of the image
		image = cv2.equalizeHist(cv2.cvtColor(cur_image, cv2.COLOR_BGR2GRAY))
		if(not isinstance(prev_image, np.ndarray)):
			# If there's no previous image, stop processing here
			return image
		# Equalize the previous image as well
		last_image = cv2.equalizeHist(cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY))
		# Get the difference between the two images, using a threshold, values found through experimentation
		(ret,diff_image) = cv2.threshold(cv2.absdiff(image, last_image), 50, 255, cv2.THRESH_TOZERO)
		# Call the detection algorithm, and save the detected keypoints
		self.keypoints = self.engine.detect(diff_image)
		# Returns the processed image
		return cv2.drawKeypoints(diff_image, self.keypoints)

class Factory():
	"""
		Static class for listing and getting instances of algorithms 
		Close your eyes if you like idiomatic python
	"""
	algs = dict()
	algs["traffic"] = TrafficAlg
	algs["none"] = Algorithm
	
	@staticmethod
	def get_alg(alg):
		""" Returns the algorithm matching the given input, the "none" algorithm if the given algorithm is not found """
		if(alg in Factory.algs):
			return Factory.algs[alg]()
		else:
			return Factory.algs["none"]()
	
	@staticmethod
	def __str__():
		""" Simple string representation of the algorithm factory """
		retString = "Algorithm factory containing algs: \n"
		for key in Factory.algs:
			retString += Factory.algs[key].description + "\n"
		return retString
	
	@staticmethod
	def get_printable():
		""" Returns a dict with the following form: output[algorithm_id] = (algorithm_name, algorithm_description) """
		printable = dict()
		for key in Factory.algs:
			printable[key] = (Factory.algs[key].name, Factory.algs[key].description)

if __name__ == "__main__":
	fac = Factory()
	print(fac)
	ta = fac.get_alg("traffic")
	print(ta)