import pygame

pygame.init()
 
#Global Variable
WIDTH = 800
HEIGHT = 600
#set framerate
FPS = 60
#FPS
clock = pygame.time.Clock()
#define status game
game_status = True 
#define player action variables
moving_left = False
moving_right = False
#screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Cyber Shooter')

class Soldier(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        
        self.x = x
        self.y = y
        self.scale = 3
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.jump = False
        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
        temp_list = []
        for i in range(1,5):
            img = pygame.image.load(f'Hero/cyborg/idle{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        temp_list = [] 
        for i in range(1,7):
            img = pygame.image.load(f'Hero/cyborg/run{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][int(self.frame_index)]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        #reset movement var
        dx = 0

        #assign movement var if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = -1
       
        #update rect
        self.rect.x += dx

    def animation(self):
        #update animation
        animation_cooldown = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index +=1
        #if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
        
    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #reset 
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
    

#player
player = Soldier( 200, 300, 5)

#while True:
while game_status:
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            game_status = False
            
        #keyboard press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True

        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    #screen blit
    screen.fill('white')
    player.draw()
    player.move(moving_left, moving_right)
    player.animation()

    #update player action
    if moving_left or moving_right:
        player.update_action(1)
    else:
        player.update_action(0)

    pygame.display.update()
    clock.tick(60)


