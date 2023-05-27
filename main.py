import pygame
from pygame import mixer
import os
import random
import csv
import button
from abc import ABC, abstractmethod

mixer.init()
pygame.init()

WIDTH = 800
HEIGHT = 640

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Cyber Shooter')

clock = pygame.time.Clock()
FPS = 60

FALL = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLUMN = 150
TILE_SIZE = HEIGHT // ROWS
TILE_TYPES = 36
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1	
start_game = False
start_intro = False

moving_left = False
moving_right = False
shoot = False

pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.mp3')
jump_fx.set_volume(2)
shot_fx = pygame.mixer.Sound('audio/shot.mp3')
shot_fx.set_volume(2)

start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

back1 = pygame.image.load('img/Background/1.png').convert_alpha()
back1 = pygame.transform.rotozoom(back1, 0, 2)
back2 = pygame.image.load('img/Background/2.png').convert_alpha()
back2 = pygame.transform.rotozoom(back2, 0, 2)
back3 = pygame.image.load('img/Background/3.png').convert_alpha()
back3 = pygame.transform.rotozoom(back3, 0, 2)
back4 = pygame.image.load('img/Background/4.png').convert_alpha()
back4 = pygame.transform.rotozoom(back4, 0, 2)
back5 = pygame.image.load('img/Background/5.png').convert_alpha()
back5 = pygame.transform.rotozoom(back5, 0, 2)
back6 = pygame.image.load('img/Background.png').convert_alpha()
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
health_box_img = pygame.image.load('img/icons/health.png').convert_alpha()
health_box_img = pygame.transform.rotozoom(health_box_img, 0, 0.06).convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
ammo_box_img = pygame.transform.rotozoom(ammo_box_img, 0, 0.14).convert_alpha()
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
}

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_bg():
	width = back1.get_width()
	for x in range(5):
		screen.blit(back1, ((x * width) - bg_scroll * 0.5, 0))
		screen.blit(back2, ((x * width) - bg_scroll * 0.6, 0))
		screen.blit(back3, ((x * width) - bg_scroll * 0.7, 0))
		screen.blit(back4, ((x * width) - bg_scroll * 0.8, 0))
		screen.blit(back5, ((x * width) - bg_scroll * 0.9, 0))

def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	spike_group.empty()
	exit_group.empty()

	data = []
	for row in range(ROWS):
		r = [-1] * COLUMN
		data.append(r)

	return data

class Char(ABC, pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		super().__init__()
		self.x = x
		self.y = y
		self.scale = scale

	@abstractmethod
	def update(self):
		pass

class Hero(Char):
	def __init__(self, char_type, x, y, scale, speed, ammo):
		super().__init__(x, y, scale)

		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.gravity = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			temp_list = []
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.update_animation()
		self.check_alive()
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1

	def move(self, moving_left, moving_right):
		screen_scroll = 0
		dx = 0
		dy = 0

		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		if self.jump == True and self.in_air == False:
			self.gravity = -16
			self.jump = False
			self.in_air = True

		self.gravity += FALL
		if self.gravity > 10:
			self.gravity
		dy += self.gravity

		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if self.gravity < 0:
					self.gravity = 0
					dy = tile[1].bottom - self.rect.top
				elif self.gravity >= 0:
					self.gravity = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		if pygame.sprite.spritecollide(self, spike_group, False):
			self.health -= 5
			self.jump = True 
			self.in_air = False

		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		if self.rect.bottom > HEIGHT:
			self.health = 0

		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > WIDTH:
				dx = 0

		self.rect.x += dx
		self.rect.y += dy

		if self.char_type == 'player':
			if (self.rect.right > WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery + (0.01 * self.rect.size[1]), self.direction)
			bullet_group.add(bullet)
			self.ammo -= 1
			shot_fx.play()

	def update_animation(self):
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.action][self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0

	def update_action(self, new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)

	def draw(self): 
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
		
class Enemy(Hero):
	def __init__(self, char_type, x, y, scale, speed, ammo):
		super().__init__(char_type, x, y, scale, speed, ammo)
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		self.unlimited = False
		self.timer = 2

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			if self.ammo < 5 and self.unlimited == False:
				if self.timer == 0:
					self.unlimited = True
				self.timer -= 1
				self.shoot_cooldown = 5
				self.ammo -= 0
			else:
				self.ammo -= 1
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery + (0.01 * self.rect.size[1]), self.direction)	
			bullet_group.add(bullet)
			shot_fx.play()	

	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			if self.vision.colliderect(player.rect):
				self.update_action(0)#0: idle
				#shoot
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: run
					self.move_counter += 1
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		self.rect.x += screen_scroll

class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 17:
						self.obstacle_list.append(tile_data)
					elif tile == 30:
						spike = Spike(img, x * TILE_SIZE, y * TILE_SIZE)
						spike_group.add(spike)
					elif tile >= 18 and tile <= 29:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 33:
						player = Hero('player', x * TILE_SIZE, y * TILE_SIZE, 1.7 , 5, 20)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 34:
						enemy = Enemy('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.7, 2, 10)
						enemy_group.add(enemy)
					elif tile == 32:
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 31:
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 35:
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar

	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Spike(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll
		if pygame.sprite.collide_rect(self, player):
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				pass
			self.kill()

class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		self.health = health
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, 'cyan', (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, 'black', (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, 'cyan', (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		self.rect.x += (self.direction * self.speed) + screen_scroll
		if self.rect.right < 0 or self.rect.left > WIDTH:
			self.kill()
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, WIDTH // 2, HEIGHT))
			pygame.draw.rect(screen, self.colour, (WIDTH // 2 + self.fade_counter, 0, WIDTH, HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, WIDTH, HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, HEIGHT // 2 +self.fade_counter, WIDTH, HEIGHT))
		if self.direction == 2:
			pygame.draw.rect(screen, self.colour, (0, 0, WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= WIDTH:
			fade_complete = True

		return fade_complete

intro_fade = ScreenFade(1, 'black', 4)
death_fade = ScreenFade(2, 'black', 4)

start_button = button.Button(WIDTH // 2 - 130, HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(WIDTH // 2 - 110, HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, restart_img, 2)

enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

world_data = []
for row in range(ROWS):
	r = [-1] * COLUMN
	world_data.append(r)
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

	clock.tick(FPS)

	if start_game == False:
		screen.blit(back6, (0,0))
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if exit_button.draw(screen):
			run = False
	else:
		draw_bg()
		world.draw()
		health_bar.draw(player.health)
		draw_text('AMMO: ', font, 'black', 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))

		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		bullet_group.update()
		item_box_group.update()
		decoration_group.update()
		spike_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		spike_group.draw(screen)
		exit_group.draw(screen)

		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0

		if player.alive:
			if shoot:
				player.shoot()
			if player.in_air:
				player.update_action(2)
			elif moving_left or moving_right:
				player.update_action(1)
			else:
				player.update_action(0)
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVELS:
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)	
		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False

	pygame.display.update()

pygame.quit()
