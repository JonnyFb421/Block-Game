from os import stat
import pygame
import random

BLACK  = (   0,   0,   0)
WHITE  = ( 255, 255, 255)
RED    = ( 255,   0,   0)
GREEN  = (   0, 255,   0)
BLUE   = (   0,   0, 255)
BROWN  = ( 139,  39,  19)
GOLD   = ( 255, 215,   0)
PI = 3.141592653589793

class Block(pygame.sprite.Sprite):
    """
    This class represents all the blocks in the game.
    """
    def __init__(self, color, width, height):
        #Call the parent class (Sprite) constructor
        super().__init__()
        self.color = color
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.update_block = True
        self.snitch = False
        
    def reset_pos(self):
        """ Reset position to the top of the screen """
        if self.snitch:
            self.rect.x = random.randrange(screen_width)
            self.rect.y = random.randrange(-90000, -5000)
        elif self.update_block == True:
            self.rect.y = random.randrange(-300, -20)
            self.rect.x = random.randrange(5, screen_width - 5)
        else:
            self.kill()
    def update(self, speed):
        """ Called each frame """
        # Move block down one pixel
        self.rect.y += speed
        if self.rect.y > 410:
            self.reset_pos()
        
# --- Declare functions before game loop        
def populate_blocks(starting_block_amount):
    """ Populates game with initial black blocks
        Spawns one golden block worth: Score+6 Speed+2 """
    for i in range(starting_block_amount):
        block = Block(BLACK, 20, 15)
        block.rect.x = random.randrange(screen_width)
        block.rect.y = random.randrange(-75, 0)    
        block_list.add(block)
        all_sprites_list.add(block)
    golden_block = Block(GOLD, 20, 15)
    golden_block.snitch = True
    golden_block.rect.x = random.randrange(screen_width)
    golden_block.rect.y = random.randrange(-2500, -220)
    block_list.add(golden_block)
    all_sprites_list.add(golden_block)    
    
def spawn_red_blocks(spawn_number):
    """ Spawns red blocks every time score is changed """
    for i in range(spawn_number):
        new_block = Block(RED, 20, 15)
        new_block.rect.x = random.randrange(screen_width)
        new_block.rect.y = random.randrange(-500, -25)        
        red_block_list.add(new_block)
        block_list.add(new_block)
    
def load_score():
    """ Loads high_score from "./score" and returns int """
    if stat("score").st_size == 0:
        return str(0)
    else:
        try:
            with open("score", 'r+') as high_score_file:
                high_score = high_score_file.read()
        except (IOError, ValueError) as e:
            print("An I/O error or a ValueError occurred: " + e)
        finally:
            high_score_file.close() 
        return int(high_score)
        
def save_score(high_score):
    """ Saves high score to "./score" before closing game """
    try:
        with open("score", 'w+') as high_score_file:
            high_score_file.write(str(high_score))
    except (IOError, ValueError):
        print("An I/O error or a ValueError occurred")
    finally:
        high_score_file.close() 
    
# --- Set Up & Initialize Window 
pygame.init()
screen_width =  700
screen_height = 400
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("Block Game")
pygame.mouse.set_visible(False)
font = pygame.font.SysFont('Calibri', 23, True, False)

# --- Initializing variables outside of game loop
score = 0
high_score = load_score()
speed = 1
starting_block_amount = 5
#block_list will manage all sprites which can not be passed: blocking
block_list = pygame.sprite.Group()
red_block_list = pygame.sprite.Group()
#This is a list of every sprite, including blocking sprites
all_sprites_list = pygame.sprite.Group()
#Create Green block for player
player = Block(GREEN, 20, 15)
all_sprites_list.add(player)

#Populate blocks 
populate_blocks(starting_block_amount)

#Images
#Sounds
#background music
#Downloaded from: http://www.freesound.org/people/JimiMod/sounds/277481/
pygame.mixer.music.load('sound/music.ogg')
#http://www.freesound.org/people/leviclaassen/sounds/107789/
red_block_hit_sound = pygame.mixer.Sound("sound/hit1.ogg")
#http://www.freesound.org/people/gado77/sounds/271397/
black_block_hit_sound = pygame.mixer.Sound("sound/hit2.ogg")
pygame.mixer.music.play()
# Main loop
done = False
#Used to manage how fast the screen updates
clock = pygame.time.Clock()
# -------- Start Main Program Loop --------
while not done:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
    # --- Game logic should go here
    pos = pygame.mouse.get_pos()
    player.rect.x = pos[0]
    player.rect.y = pos[1]
    prev_score = score
    if score > high_score:
        high_score = score   
    #Check for player/block_list collision
    block_hit_list = pygame.sprite.spritecollide(player, block_list, False)
    for block in block_hit_list:
        #Player hit gold box
        if block.color == GOLD:
            score += 6
            speed += 2
        #Player hit red box
        if block.color == RED:
            red_block_hit_sound.play()
            if score >= 3: 
                score -= 3 
            else: 
                score = 0
            if speed > 1: 
                speed -= 1
        #Player hit black box
        else:
            score += 1
            if score % 3 == 1 and prev_score != score:
                speed += 1
            black_block_hit_sound.play()
        if score < len(red_block_list):
            for i in range(len(red_block_list) - score):
                red_block_list.sprites()[i].update_block = False        
        #Reset collected blocks to top of window
        block.reset_pos()
     
    #Spawn red blocks as player earns points
    if score > prev_score:
        spawn_red_blocks(score - prev_score)
    all_sprites_list.add(red_block_list)
    
    # Clear screen before drawing
    screen.fill(WHITE)    
    # --- Drawing code should go here        
    #Draw all sprites
    all_sprites_list.draw(screen)
    block_list.update(speed)
    display_score = font.render(str(score), True, BLUE)
    display_high_score = font.render(str(high_score), True, GOLD)
    screen.blit(display_score, [screen_width-30, 30])
    screen.blit(display_high_score, [screen_width-30, 5])
    # --- Go ahead and update the screen with what we've drawn
    pygame.display.flip()
    # --- Limit to 60 FPS
    clock.tick(60)

# Close the window and quit
save_score(high_score)
pygame.quit()