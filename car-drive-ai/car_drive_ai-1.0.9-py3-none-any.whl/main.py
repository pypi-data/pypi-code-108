import pygame
import neat
import os
import math
import numpy as np
from PIL import Image, ImageFilter
import sys
import os
import requests
import wget

def download_files():
	car_url = "https://raw.githubusercontent.com/timo42453189/car_drive_ai_files/main/car.png"
	red_car_url = "https://raw.githubusercontent.com/timo42453189/car_drive_ai_files/main/red-car.png"
	sample_track_url = "https://raw.githubusercontent.com/timo42453189/car_drive_ai_files/main/track.png"
	config_file_url = "https://raw.githubusercontent.com/timo42453189/car_drive_ai_files/main/config.txt"
	wget.download(car_url)
	wget.download(red_car_url)
	wget.download(sample_track_url)
	wget.download(config_file_url)

print("***** If you dont have any images or config files feel free to use mine at 'https://github.com/timo42453189/car_drive_ai_files' *****")
print("***** if you have no images just call the download_files methode *****")
print("***** There are some arguments for the run function *****")
print("***** w_size=() is the window size, c_size=() is the size of the car, c_speed=8 is the car speed *****")
print("***** config_file='path/to/config_file', d=True/False to download sample tracks, car images and config file *****")

pygame.init()
pygame.font.init()

directory_path = os.getcwd()


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


def convert(track="track.png"):
    try:
        image = Image.open(track)
    except:
        print(f"Error No such file '{track}'")
        sys.exit(1)

    image_data = image.load()
    height,width = image.size
    for loop1 in range(height):
        for loop2 in range(width):
            r, g, b, z = image_data[loop1,loop2]
            if b != 255:
                image_data[loop1,loop2] = r ,g , b, 255

            elif b == 255 and r != 255:
                image_data[loop1,loop2] = r, g, b, 0
    image.save(output_name)
    return output_name

def calculate_start_pos():
	x = 0
	y = 390
	found_blue = False
	while not found_blue:
		if x >= track_scale[0]:
			return None
			break

		else:	
			color = win.get_at((x, y))

		if color[0] == 0 and color[1] > 100 and color[2] >= 200:
			found_blue = True
			return [x + 20, y]
		else:
			x += 1

def setup(w_size, c_size, c_speed):
	global track, TRACK_BORDER, TRACK_BORDER_MASK, purple_car, car_max_speed, red_car, track_scale, draw_radar, track_x, track_y, img_name, output_name, win
	track_scale = w_size
	car_max_speed = c_speed
	draw_radar = True
	track_x, track_y = 0, 0
	img_name = "track.png"
	output_name = "track_transparent.png"
	win = pygame.display.set_mode(track_scale)
	converted_name = convert(track=img_name)
	track = pygame.image.load(os.path.join(img_name))
	track = pygame.transform.scale(track, track_scale)
	TRACK_BORDER = pygame.transform.scale(pygame.image.load(os.path.join(converted_name)), track_scale)
	TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
	purple_car = pygame.image.load(os.path.join("car.png"))
	purple_car = pygame.transform.scale(purple_car, c_size)
	red_car = pygame.image.load(os.path.join("red-car.png"))
	red_car = pygame.transform.scale(red_car, c_size)


FONT = pygame.font.SysFont('Comic Sans MS', 30)
FPS = 60

gen = 0

class Car():
	def __init__(self, max_vel, rotation_vel, start_pos):
		self.max_vel = car_max_speed
		self.vel = 0
		self.rotation_vel = rotation_vel
		self.angle = 0
		self.img = purple_car
		self.start_pos = start_pos#[204, 390]
		self.acceleration = 8
		self.radars = []
		self.drawing_radars = []
		self.center = [self.start_pos[0] + purple_car.get_width() / 2, self.start_pos[1] + purple_car.get_height() / 2]

	def rotate(self, left=False, right=False):
		if left:
			self.angle += self.rotation_vel
		if right:
			self.angle -= self.rotation_vel

	def draw(self, win, image):
		blit_rotate_center(win, image, self.start_pos, self.angle)

	def draw_radar(self, win):
		for radar in self.radars:
			position = radar[0]
			pygame.draw.line(win, (0, 255, 0), self.center, position, 1)
			pygame.draw.circle(win, (0, 255, 0), position, 5)

	def check_radar(self, degree):
		self.center = [self.start_pos[0] + purple_car.get_width() / 2, self.start_pos[1] + purple_car.get_height() / 2]
		length = 1
		x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
		y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
		try:
			while track.get_at((x, y)) != (255, 255, 255, 255):
				length += 0.1
				x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
				y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
		except:
			pass

		dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
		# if img is at x 0 and y 0 this works but change this to whereever your picture is
		self.radars.append([(x, y), dist])

	def move_forward(self):
		self.vel = min(self.vel + self.acceleration, self.max_vel)
		self.move()

	def move(self):
		radians = math.radians(self.angle)
		vertical = math.cos(radians) * self.vel
		horizontal = math.sin(radians) * self.vel
		self.start_pos[1] -= vertical 
		self.start_pos[0] -= horizontal

	def reduce_speed(self, speed_after):
		self.vel = max(self.vel - self.acceleration/2)
		self.move()

	def collide(self, mask, x, y):
		car_mask = pygame.mask.from_surface(red_car)
		offset = (int(self.start_pos[0] - x), int(self.start_pos[1] - y))
		collision = mask.overlap(car_mask, offset)
		return collision

	def get_data(self):
		radars = self.radars
		return_values = [0, 0, 0, 0, 0]
		for i, radar in enumerate(radars):
			return_values[i] = int(radar[1] / 30)

		return return_values

def get_best_fitness(ge):
	fitness_of_cars = []
	for i in ge:
		fitness_of_cars.append(i.fitness)

	return np.argmax(fitness_of_cars)



def eval_genomes(genomes, config): 
	global gen
	angle = 0

	gen += 1

	cars = []
	nets = []
	ge = []

	win.blit(track, (track_x, track_y))

	for genome_id, genome in genomes:
		start_point = calculate_start_pos()
		if start_point == None:
			print("Didn't found any point to start, please try another track")
			sys.exit(1)

		genome.fitness = 0 
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)
		cars.append(Car(8, 6, start_point))
		ge.append(genome)


	clock = pygame.time.Clock()
	run = True
	while run:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break

		win.blit(track, (track_x, track_y))
		text = FONT.render(f"{str(len(cars))} alive", False, (0, 0, 0))
		win.blit(text, (0, 0))
		generation = FONT.render(f"{str(gen - 1)}. generation", False, (0, 0, 0))
		win.blit(generation, (0, 40))

		index_of_best_car = get_best_fitness(ge)

		for x, car in enumerate(cars):
			if x == index_of_best_car:
				car.draw(win, red_car)
			else:
				car.draw(win, purple_car)
			if draw_radar:
				car.draw_radar(win)

			car.radars.clear()
			for d in range(0, 225, 45):
				car.check_radar(d)

			output = nets[cars.index(car)].activate(car.get_data())
			out = np.argmax(output)
			if out == 0:
				car.rotate(left=True)
			elif out == 1:
				car.rotate(right=True)

			car.move_forward()

			if car.collide(TRACK_BORDER_MASK, x=track_x, y=track_y) != None:
				ge[cars.index(car)].fitness -= 30
				ge.pop(cars.index(car))
				nets.pop(cars.index(car))
				cars.pop(cars.index(car))

			else:
				ge[cars.index(car)].fitness += 2

		if len(cars) == 0:
			run = False
			break


		pygame.display.update()


def run(config_file="config.txt", d=False, w_size=(1600, 900), c_size=(30, 60), c_speed=8):
    if d:
       download_files()
    setup(w_size, c_size, c_speed)

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 500)