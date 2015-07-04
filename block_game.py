from os import stat
import itertools
import random 
import pygame

SCREEN_WIDTH  = 700
SCREEN_HEIGHT = 400
SCORE_TO_SPEED_RATIO    = 3
SCORE_FROM_BLACK_BLOCK  = 1
SPEED_FROM_BLACK_BLOCK  = 1
SCORE_FROM_GOLD_BLOCK   = 6
SPEED_FROM_GOLD_BLOCK   = 2
PENALTY_SCORE_RED_BLOCK = 3
PENALTY_SPEED_RED_BLOCK = 1
BLOCK_WIDTH = 20
BLOCK_HEIGHT = 15

class Game():
    """
    This class is a container for game variables (ie. speed, score)
    methods get mouse coords, writes score to screen, and 
    also handles pygame events such as keypresses
    """
    def __init__(self):
        # --- Set Up & Initialize Window 
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption("Block Game")
        pygame.mouse.set_visible(False)
        self.sound_controller = Sounds()
        self.font = pygame.font.SysFont('Calibri', 23, True, False)
        self.score = 0
        self.high_score = load_score()
        self.speed = 1
        self.starting_block_amount = 5
        #block_list will manage all sprites which can not be passed: blocking
        self.red_block_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        #Create Green block for player
        self.player = Block(pygame.Color("green"), BLOCK_WIDTH, BLOCK_HEIGHT)
        self.all_sprites_list.add(self.player)   

    def get_mouse_pos(self):
        """ Updates player's position with mouse position """
        pos = pygame.mouse.get_pos()
        self.player.rect.x = pos[0]
        self.player.rect.y = pos[1]
        
    def write_score(self, screen):
        """ Print score onto screen """
        self.margin_width = 50
        self.display_score = self.font.render(str(self.score), True, pygame.Color("blue"))
        self.display_high_score = self.font.render(str(self.high_score), True, pygame.Color("gold"))
        screen.blit(self.display_score, [SCREEN_WIDTH-self.margin_width, 30])
        screen.blit(self.display_high_score, [SCREEN_WIDTH-self.margin_width, 5])
        
    def pygame_event_handler(self):
        """ Checks for events from user 
            such as key presses """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        
class Sounds():
    """ 
    Loads sounds into pygame 
    """
    def __init__(self):
        #Downloaded from: http://www.freesound.org/people/JimiMod/sounds/277481/
        pygame.mixer.music.load('sound/music.ogg')
        pygame.mixer.music.play(-1)
        #Downloaded from: http://www.freesound.org/people/leviclaassen/sounds/107789/
        self.red_block_hit_sound = pygame.mixer.Sound("sound/hit1.ogg")
        #Downloaded from: http://www.freesound.org/people/gado77/sounds/271397/
        self.black_block_hit_sound = pygame.mixer.Sound("sound/hit2.ogg")

    def play_red_hit_sound(self):
        self.red_block_hit_sound.play()
    
    def play_black_hit_sound(self):
        self.black_block_hit_sound.play()   
    
class Block(pygame.sprite.Sprite):
    """
    This class represents all the blocks in the game.
    methods populates blocks, processes collision
    and updates blocks positions if they are bewlow screen
    """
    def __init__(self, color, width, height):
        #Call the parent class (Sprite) constructor
        super().__init__()
        self.color = color
        self.image = pygame.Surface([width, height]).convert()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.update_block = True
        self.snitch = False
    
    def populate_blocks(self, starting_block_amount):
        """ Populates game with initial black blocks
            Spawns one golden block worth """
        self.block_list = pygame.sprite.Group()
        for i in range(starting_block_amount):
            self.block = Block(pygame.Color("black"), BLOCK_WIDTH, BLOCK_HEIGHT)
            self.block.rect.x = random.randrange(SCREEN_WIDTH - BLOCK_WIDTH)
            self.block.rect.y = random.randrange(-75, 0)    
            self.block_list.add(self.block)
        self.golden_block = Block(pygame.Color("gold"), BLOCK_WIDTH, BLOCK_HEIGHT)
        self.golden_block.snitch = True
        self.golden_block.rect.x = random.randrange(SCREEN_WIDTH - BLOCK_WIDTH)
        self.golden_block.rect.y = random.randrange(-2500, -220)
        self.block_list.add(self.golden_block)
        return self.block_list
        
    def spawn_red_blocks(self, spawn_number, red_block_list, block_list):
        """ Spawns red blocks every time score is changed """
        for i in range(spawn_number):
            self.new_block = Block(pygame.Color("red"), BLOCK_WIDTH, BLOCK_HEIGHT)
            self.new_block.rect.x = random.randrange(SCREEN_WIDTH - BLOCK_WIDTH)
            self.new_block.rect.y = random.randrange(-500, -25)        
            self.new_block.add(red_block_list, block_list)
        
    def process_block_collision(self, game):
        """ Check if player is colliding with 
            any blocks and if so process score/speed """
        for self.block in game.block_hit_list:
            #Player hit gold box
            if self.block.color == pygame.Color("gold"):
                game.sound_controller.play_black_hit_sound()
                game.score += SCORE_FROM_GOLD_BLOCK
                game.speed += SPEED_FROM_GOLD_BLOCK
            #Player hit red box
            if self.block.color == pygame.Color("red"):
                game.sound_controller.play_red_hit_sound()
                game.score = game.score - PENALTY_SCORE_RED_BLOCK if game.score >= PENALTY_SCORE_RED_BLOCK else 0 
                if game.speed > PENALTY_SPEED_RED_BLOCK: game.speed -= PENALTY_SPEED_RED_BLOCK
            #Player hit black box
            elif self.block.color == pygame.Color("black"):
                game.score += SCORE_FROM_BLACK_BLOCK
                if game.score % SCORE_TO_SPEED_RATIO == 1 and game.prev_score != game.score:
                    game.speed += SPEED_FROM_BLACK_BLOCK
                game.sound_controller.play_black_hit_sound()
            #Stops red blocks from spawning as score lowers
            if game.score < len(game.red_block_list):
                for self.sprite in itertools.islice(game.red_block_list, 0, len(game.red_block_list) - game.score):
                    self.sprite.update_block = False
            #Reset collected blocks to top of window
            self.block.reset_pos()
        
    def reset_pos(self):
        """ Reset position to the top of the screen """
        if self.snitch:
            self.rect.x = random.randrange(SCREEN_WIDTH - BLOCK_WIDTH)
            self.rect.y = random.randrange(-90000, -5000)
        elif self.update_block:
            self.rect.x = random.randrange(SCREEN_WIDTH - BLOCK_WIDTH)
            self.rect.y = random.randrange(-100, -20)

        else:
            self.kill()
    
    def update(self, speed):
        """ Called each frame """
        #Moves block down the screen by speed(default 1)
        self.rect.y += speed
        if self.rect.y > 410:
            self.reset_pos()
        
# --- Declare functions before game loop          
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
        return int(high_score)
        
def save_score(high_score):
    """ Saves high score to "./score" before closing game """
    try:
        with open("score", 'w+') as high_score_file:
            high_score_file.write(str(high_score))
    except (IOError, ValueError):
        print("An I/O error or a ValueError occurred")
            
def main():        
    game = Game()
    block = Block((0,0,0,0), 0, 0)
    #Populate blocks 
    game.block_list = block.populate_blocks(game.starting_block_amount)
    game.all_sprites_list.add(game.block_list)
    done = False # Main loop
    clock = pygame.time.Clock()
    # -------- Start Main Program Loop --------
    while not done:
        done = game.pygame_event_handler()
        #Player follows mouse
        game.get_mouse_pos()
        game.prev_score = game.score
        game.high_score = max(game.high_score, game.score)
        #Check for player/block_list collision
        game.block_hit_list = pygame.sprite.spritecollide(game.player, game.block_list, False)
        block.process_block_collision(game)    
        #Spawn red blocks as player earns points
        if game.score > game.prev_score:
            block.spawn_red_blocks(game.score - game.prev_score, game.red_block_list, game.block_list)
        game.all_sprites_list.add(game.red_block_list)
        # Clear screen before drawing
        game.screen.fill(pygame.Color("white"))    
        #Draw sprites, score, and update block_list
        game.all_sprites_list.draw(game.screen)
        game.block_list.update(game.speed)
        game.write_score(game.screen)
        # --- Render the drawings
        pygame.display.flip()
        # --- Limit to 60 FPS
        clock.tick(60)
    # Close the window and quit
    if done: 
        save_score(game.high_score)
        pygame.quit()
if __name__ == '__main__': main()