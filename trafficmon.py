import pygame
import xml.etree.ElementTree as et
import cv2
import numpy
import urllib as ur

WIDTH=1600
HEIGHT=1200

HESSIAN = 1400

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
		self.wcs = Image("http://weather.cs.uit.no/cam/cam_east.jpg", True)
		self.vvs = Image("http://webkamera.vegvesen.no/kamera?id=674473", False)
		self.font = pygame.font.SysFont("Times", 30)
		
	
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
			self.screen.fill(pygame.Color("blue"), pygame.Rect((1400, 300), (100, len(self.wcs.keypoints)*10)))
			pygame.display.flip()

	def update_images(self):
		self.wcs.update()
		self.vvs.update()
			
		

if __name__ == "__main__":
	mon = Monitor()
	mon.run()
