import moviepy.video.io.ImageSequenceClip
import numpy as np
from PIL import Image
import os

# https://www.a1k0n.net/2011/07/20/donut-math.html

# Frame size, in px
HEIGHT = 1080
WIDTH = 1080

# Number of frames per second
FPS = 30

# Duration of the video, in seconds
DURATION = 4

NUMBER_OF_FRAMES = FPS*DURATION

# Colors of the donut
R = 0
G = 255
B = 0

# Dimensions of the donut
R1 = 30
R2 = 60

K2 = 1000
K1 = WIDTH*K2*3/(8*(R1+R2))

THETA_SPACING = np.pi/64
PHI_SPACING = np.pi/128

A_SPACING = np.pi/32
B_SPACING = np.pi/64

LIGHT_DIRECTION = np.array([0,1,-1])/np.sqrt(2)

PATH = os.getcwd() + '/images'

if not os.path.isdir(PATH):
	os.makedirs(PATH)


def Rx(theta):
	c, s = np.cos(theta), np.sin(theta)
	return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def Ry(theta):
	c, s = np.cos(theta), np.sin(theta)
	return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def Rz(theta):
	c, s = np.cos(theta), np.sin(theta)
	return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def generate_image(i):
	A = i*A_SPACING
	B = i*B_SPACING
	RzB = Rz(B)
	RxA = Rx(A)
	image = np.zeros((HEIGHT,WIDTH,3),dtype=np.uint8)
	z_buffer = np.array(np.ones((HEIGHT,WIDTH)) * float('inf')*(-1),dtype=float)
	for theta in np.arange(0, 2*np.pi, THETA_SPACING):
	
		P = np.array([R2 + R1*np.cos(theta),R1*np.sin(theta),0])
		N = np.array([np.cos(theta), np.sin(theta), 0])

		for phi in np.arange(0, 2*np.pi, PHI_SPACING):
			
			M = np.matmul(RzB, np.matmul(RxA, np.matmul(Ry(phi), N)))
			Q = np.matmul(RzB, np.matmul(RxA, np.matmul(Ry(phi), P)))
			L = np.dot(M,LIGHT_DIRECTION)

			[x,y,z] = Q
			x_display = HEIGHT//2 - int(K1*y/(K2 + z))
			y_display = WIDTH//2 + int(K1*x/(K2 + z))

			if z_buffer[x_display, y_display] <= z:
				z_buffer[x_display,y_display] = z
				if (L < 0):
					image[x_display,y_display] = (int(-L*R),int(-L*G),int(-L*B))
				else:
					image[x_display,y_display] = (0,0,0)


	im = Image.fromarray(image)
	im = im.convert('RGB')
	im.save(PATH +'/image_{:05d}.png'.format(i))
	im.close()



for i in range(0,NUMBER_OF_FRAMES):
	generate_image(i)
	print("{:.2f}%".format(100 * i / NUMBER_OF_FRAMES))



image_files = [PATH +'/' + img for img in os.listdir(PATH) if img.endswith(".png")]
image_files.sort()
clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=FPS)
clip.write_videofile(PATH + '/my_video.mp4')