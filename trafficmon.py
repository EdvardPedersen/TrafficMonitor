import pygame
import xml.etree.ElementTree as et
import cv2
import numpy
import urllib as ur

WIDTH=1600
HEIGHT=1200

HESSIAN = 1400

class DataLogger:
	def __init__(self, length, window_size):
		self.datapoints = list()
		self.limit = length
		self.average = list()
		self.window_size = window_size
		self.out_x = 300
		self.out_y = 300
		self.max_value = 1

	def add_point(self, datapoint):
		self.datapoints.append(datapoint)
		if len(self.datapoints) > self.limit:
			self.datapoints.pop(0)
		if(len(self.datapoints) > self.window_size):
			average = sum(self.datapoints[:self.window_size])/self.window_size
			self.average.append(average)
		if len(self.average) > self.limit - self.window_size:
			self.average.pop(0)
		self.max_value = max(max(self.datapoints),50)

	def draw_image(self):
		retsur = pygame.Surface((self.out_x, self.out_y))
		retsur.fill((255,255,255))
		increment_x = self.out_x / self.limit
		scale_y = self.out_y / self.max_value
		prev_x = 0
		if(len(self.datapoints) > 0):
			prev_y = int(self.out_y - (self.datapoints[0] * scale_y))
		cur_x = 0
		for element in self.datapoints:
			cur = int(self.out_y - (element * scale_y))
			pygame.draw.line(retsur, (255,0,0), (prev_x, prev_y), (cur_x, cur))
			prev_x = cur_x
			prev_y = cur
			cur_x += increment_x
		prev_x = self.window_size*increment_x
		if(len(self.average) > 0):
			prev_y = int( self.out_y - (self.average[0] * scale_y))
		cur_x = self.window_size*increment_x
		for element in self.average:
			cur = int( self.out_y - (element*scale_y) )
			pygame.draw.line(retsur, (0,0,255), (prev_x, prev_y), (cur_x, cur))
			prev_x = cur_x
			prev_y = cur
			cur_x += increment_x
		return retsur
		

class Image():
	def __init__(self, url, process):
		self.url = url
		self.image = False
		self.im_proc = False
		self.keypoints = 0
		self.proc_image = process
		self.update()

	def update(self):
		self.get_image()
		self.image = pygame.transform.rotozoom(self.image, 0, float((HEIGHT/2.0))/self.image.get_height())

	def get_image(self):
		(f,h) = ur.urlretrieve(self.url)
		self.image = pygame.image.load(f)
		if(self.proc_image):
			pimg = cv2.cvtColor(cv2.imread(f)[530:670,800:1200], cv2.COLOR_BGR2GRAY)
			sift = cv2.BRISK(60)
			self.keypoints = sift.detect(pimg)
			cv2.imwrite('sift_keypoints.jpg', cv2.drawKeypoints(pimg, self.keypoints))
			self.im_proc = pygame.image.load('sift_keypoints.jpg')
			print("Keypoints: " + str(len(self.keypoints)))
			
		

class Monitor:
	def __init__(self):
		pygame.display.init()
		pygame.init()
		# CONFIG
		self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
		self.running = True
		self.clock = pygame.time.Clock()
		self.timer = 0
		self.loggertimer = 0
		self.wcs = Image("http://weather.cs.uit.no/cam/cam_east.jpg", True)
		self.vvs = Image("http://webkamera.vegvesen.no/kamera?id=674473", False)
		self.font = pygame.font.SysFont("Times", 30)
		self.logger = DataLogger(300, 5)
		
	
	def _load_config(self):
		pass

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				exit()

	def run(self):
		while self.running:
			self.screen.fill(pygame.Color("black"))
			# CONFIG
			self.clock.tick(10)
			self.timer += 1
			self.loggertimer += 1
			# CONFIG
			if self.timer == 300:
				self.update_images()
				self.timer = 0
			self.handle_events()
			self.screen.blit(self.wcs.image, (20,20))
			self.screen.blit(self.wcs.im_proc, (WIDTH-self.wcs.im_proc.get_width()-20, 20))
			self.screen.blit(self.vvs.image, (20,600))
			text = self.font.render("Traffic level " + str(len(self.wcs.keypoints)), True, (min(255, len(self.wcs.keypoints)*5), 0,0))
			self.screen.blit(text, (WIDTH-400, 200))
			pygame.draw.circle(self.screen, (255,0,0) , (17*(WIDTH/20),HEIGHT/3), len(self.wcs.keypoints))
			if(self.loggertimer == 600):
				self.logger.add_point(len(self.wcs.keypoints))
				self.loggertimer = 0
			self.screen.blit(self.logger.draw_image(), (WIDTH-400, HEIGHT-400))
			pygame.display.flip()

	def update_images(self):
		try:
			self.wcs.update()
			self.vvs.update()
		except:
			pass
			
		

if __name__ == "__main__":
	mon = Monitor()
	mon.run()
