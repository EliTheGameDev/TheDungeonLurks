from random import *
import pygame
pygame.init()

# Game Setup
game_version = 0.2
update_name = "Magic and Mechanisms"

screen = pygame.display.set_mode((560, 480))
pygame.display.set_caption(f"The Dungeon Lurks - v{game_version} - {update_name}")
clock = pygame.time.Clock()
FPS = 60
game_states = ["Menu", "Fight", "Upgrade"]
game_state = game_states[0]
item_chosen = False

# Fonts
font = pygame.font.SysFont("Forte", 16)
card_font = pygame.font.SysFont("@Magic R", 20)
small_card_font = pygame.font.SysFont("@Magic R", 12)
boss_font = pygame.font.SysFont("Impact", 24)
boss_outline_font = pygame.font.SysFont("Impact", 26, bold=True)
title_font = pygame.font.SysFont("Copperplate Gothic", 48)
subtitle_font = pygame.font.SysFont("Copperplate Gothic", 32)

# Colours
D_RED = (191, 0, 0)
RED = (255, 0, 0)
L_RED = (255, 63, 63)
D_ORANGE = (191, 63, 0)
ORANGE = (255, 127, 0)
L_ORANGE = (255, 191, 63)
D_YELLOW = (191, 191, 0)
YELLOW = (255, 255, 0)
L_YELLOW = (255, 255, 63)
D_GREEN = (0, 191, 0)
GREEN = (0, 255, 0)
L_GREEN = (63, 255, 63)
D_BLUE = (0, 0, 191)
BLUE = (0, 0, 255)
L_BLUE = (63, 63, 255)
D_PURPLE = (127, 0, 191)
PURPLE = (191, 0, 255)
L_PURPLE = (255, 63, 255)
D_PINK = (191, 63, 127)
PINK = (255, 127, 191)
BLACK = (0, 0, 0)
D_GREY = (63, 63, 63)
M_GREY = (127, 127, 127)
L_GREY = (191, 191, 191)
WHITE = (255, 255, 255)

# Functions
def inverse_direction(direction):
    if direction == "N":
        return "S"
    elif direction == "E":
        return "W"
    elif direction == "S":
        return "N"
    elif direction == "W":
        return "E"
    elif direction == "NE":
        return "SW"
    elif direction == "SE":
        return "NW"
    elif direction == "SW":
        return "NE"
    elif direction == "NW":
        return "SE"
    else:
        return "N"

def adjacent_direction(direction):
    if direction == "N":
        return ["NW", "NE"]
    if direction == "E":
        return ["NE", "SE"]
    if direction == "S":
        return ["SE", "SW"]
    if direction == "W":
        return["SW", "NW"]

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        if current_line and font.size(candidate)[0] > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate

    if current_line:
        lines.append(current_line)

    return lines

# Player and Enemy Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.rect = self.image.get_rect(center=pos)
        self.image.fill(BLUE)
        
        self.speed = 4
        self.max_health = self.health = 20
        self.direction = "N"
        self.shot_cool = 500
        self.shot_time = 0
        self.super_cool = 3000
        self.super_time = 0
        self.ult_used = False
        self.ult_time = 0
        self.ult_duration = 3000

        self.upgrades = []
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
            self.direction = "N"
        if keys[pygame.K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
            self.direction = "W"
        if keys[pygame.K_s] and self.rect.y < screen.get_height() - 32:
            self.rect.y += self.speed
            self.direction = "S"
        if keys[pygame.K_d] and self.rect.x < screen.get_width() - 32:
            self.rect.x += self.speed
            self.direction = "E"
        if keys[pygame.K_SPACE] and self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (8, 16), 1, 16, self.direction, GREEN, particles=[True, D_GREEN]))
            self.shot_time = pygame.time.get_ticks()
        if keys[pygame.K_e] and self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (108, 24), 2, 2, self.direction, YELLOW, particles=[False, YELLOW]))
            self.super_time = pygame.time.get_ticks()
        if keys[pygame.K_q] and self.health <= 5 and not self.ult_used:
            self.health = self.max_health
            self.ult_time = pygame.time.get_ticks()
            self.ult_used = True
        
        if self.ult_time + self.ult_duration >= pygame.time.get_ticks() and self.ult_used:
            self.health = self.max_health
            main_group.add(Particle(self.rect.center, (4, 4), WHITE, 1, 3), Particle(self.rect.center, (4, 4), WHITE, 2, 3), Particle(self.rect.center, (4, 4), WHITE, 3, 3), Particle(self.rect.center, (4, 4), WHITE, 4, 3))
        
        if self.health <= 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def take_damage(self, damage):
        self.health -= damage
        
class Mage(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Mage"
        self.colour = PURPLE
        self.alt_colour = D_PURPLE
        
        self.speed = 2
        self.max_health = self.health = 20
        self.direction = "N"
        self.shot_cool = 1500
        self.shot_time = 0
        self.super_cool = 3500
        self.super_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 64:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 64:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0: 
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            if self.health > 5:
                main_group.add(Projectile(self.rect.center, (32, 32), 3, 4, self.direction, RED, target_type=Player, particles=[True, ORANGE]))
                if self.health < 10:
                    main_group.add(Projectile(self.rect.center, (32, 32), 3, 4, inverse_direction(self.direction), RED, target_type=Player, particles=[True, ORANGE]))
            else:
                self.shot_cool = self.health * 300
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "N", RED, target_type=Player, particles=[True, ORANGE]))
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "E", RED, target_type=Player, particles=[True, ORANGE]))
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "S", RED, target_type=Player, particles=[True, ORANGE]))
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "W", RED, target_type=Player, particles=[True, ORANGE]))
                
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (16, 16), 2, 3, self.direction, PINK, target_type=Player, particles=[True, D_PINK], seeking=True))
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()

class Bomber(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(D_GREY)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Bomber"
        self.colour = D_RED
        self.alt_colour = D_PINK
        
        self.speed = 2
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 2000
        self.shot_time = 0
        self.super_cool = 10000
        self.super_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 64:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 64:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (20, 20), 1, 8, choice(["N", "E", "S", "W"]), M_GREY, target_type=Player, particles=[True, ORANGE], seeking=True))
            self.shot_cool = self.health * 50 + 500
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            for i in range(50):
                main_group.add(Particle(self.rect.center, (4, 4), L_GREEN, choice([1, 4]), 3))
            self.health += (player.max_health - player.health)//2
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Cleric(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((48, 48))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Cleric"
        self.colour = YELLOW
        self.alt_colour = WHITE
        
        self.speed = 1
        self.max_health = self.health = 20
        self.direction = "N"
        self.shot_cool = 800
        self.shot_time = 0
        self.super_cool = 3000
        self.super_time = 0
        self.spec_cool = 10000
        self.spec_time = 0
        self.spec_duration = 1000
        self.pointing = "N"
        self.seek = False
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 48:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 48:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (16, 32), 1, 7, self.pointing, L_YELLOW, target_type=Player, seeking=self.seek))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            for i in range(50):
                j = choice([1, 4])
                main_group.add(Particle(self.rect.center, (8, 4), L_GREEN, j, 3))
                main_group.add(Particle(self.rect.center, (4, 8), L_GREEN, j, 3))
            self.health += 1
            
            self.super_time = pygame.time.get_ticks()
        
        if self.spec_cool + self.spec_time < pygame.time.get_ticks():
            self.spec_time = pygame.time.get_ticks()
        
        if self.spec_time + self.spec_duration > pygame.time.get_ticks():
            self.shot_cool = 80
            self.pointing = choice(["N", "E", "S", "W"])
            self.seek = True
        else:
            self.shot_cool = 800
            self.pointing = self.direction
            self.seek = False 
        
        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Warper(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((24, 24))
        self.image.fill(D_PINK)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Warper"
        self.colour = PINK
        self.alt_colour = D_PINK
        
        self.speed = 3
        self.max_health = self.health = 20
        self.direction = "N"
        self.shot_cool = 1000
        self.shot_time = 0
        self.super_cool = 3000
        self.super_time = 0
        self.screen_presets = [(560, 480), (480, 560), (720, 240), (320, 320), (960, 120), (120, 640)]
        
    def update(self):
        global screen, player
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 24:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 24:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (16, 16), 3, 1, self.direction, L_PURPLE, target_type=Player, particles=[True, D_PURPLE], seeking=True))
            
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            screen = pygame.display.set_mode(choice(self.screen_presets))
            self.rect.center = (24, 24)
            player.rect.center = (screen.get_width(), screen.get_height())
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            screen = pygame.display.set_mode((560, 480))
            self.kill()
        
        elif self.health > self.max_health:
            self.health = self.max_health

class Defender(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(L_ORANGE)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Solemn Defender"
        self.colour = L_ORANGE
        self.alt_colour = YELLOW
        
        self.speed = 0
        self.max_health = self.health = 80
        self.direction = "N"
        self.shot_cool = 50
        self.shot_time = 0
        self.burst_duration = 10000
        self.burst_cool = 5000
        self.burst_dir = 0 # 0 is Straight, 1 is Diagonal
        self.burst_time = pygame.time.get_ticks()
        self.super_cool = 500
        self.super_time = 0
        
    def update(self):
        now = pygame.time.get_ticks()
        burst_elapsed = now - self.burst_time
        burst_active = burst_elapsed < self.burst_duration

        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 64:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 64:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if burst_active and self.shot_cool + self.shot_time < now:
            if self.burst_dir == 0:
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "N", WHITE, target_type=Player, particles=[False, None]))
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "E", WHITE, target_type=Player, particles=[False, None]))
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "S", WHITE, target_type=Player, particles=[False, None]))
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "W", WHITE, target_type=Player, particles=[False, None]))
            else:
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "NE", WHITE, target_type=Player, particles=[False, None]))
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "NW", WHITE, target_type=Player, particles=[False, None]))
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "SE", WHITE, target_type=Player, particles=[False, None]))
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "SW", WHITE, target_type=Player, particles=[False, None]))

            self.shot_time = now
        
        warning_elapsed = burst_elapsed - (self.burst_duration + self.burst_cool - 2500)
        if (0 <= warning_elapsed < 2250
                and warning_elapsed // 500 != (warning_elapsed - clock.get_time()) // 500):
            main_group.add(ParticleEmitter((140, 120), (2, 2), GREEN, 8, 200))
            main_group.add(ParticleEmitter((420, 120), (2, 2), GREEN, 8, 200))
            main_group.add(ParticleEmitter((140, 360), (2, 2), GREEN, 8, 200))
            main_group.add(ParticleEmitter((420, 360), (2, 2), GREEN, 8, 200))

        if burst_elapsed >= self.burst_duration + self.burst_cool:
            self.burst_time = now
            if self.health > 20 or randint(0, 1):
                self.burst_dir = 0
            else:
                self.burst_dir = 1

        if self.super_cool + self.super_time < pygame.time.get_ticks():
            for i in range(4 - int(self.health/20)):
                if randint(1, 2) == 1:
                    main_group.add(Projectile((17, randint(9, 471)), (24, 64), 1, 24, "E", RED, target_type=Player, particles=[False, None], delay=30))
                else:
                    main_group.add(Projectile((543, randint(9, 471)), (24, 64), 1, 24, "W", RED, target_type=Player, particles=[False, None], delay=30))
            
                if randint(1, 2) == 1:
                    main_group.add(Projectile((randint(9, 551), 17), (24, 64), 1, 24, "S", RED, target_type=Player, particles=[False, None], delay=30))
                else:
                    main_group.add(Projectile((randint(9, 551), 463), (24, 64), 1, 24, "N", RED, target_type=Player, particles=[False, None], delay=30))
            
            self.super_time = pygame.time.get_ticks()
            self.super_cool = self.health * 40 + 800

        if self.health <= 0:
            self.kill()
        
        if self.health > self.max_health:
            self.health = self.max_health

    def take_damage(self, damage):
        now = pygame.time.get_ticks()
        burst_active = now - self.burst_time < self.burst_duration
        if burst_active:
            self.health = min(self.max_health, self.health + 1)
        else:
            self.health -= damage

class Twister(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(L_RED)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Twister"
        self.colour = RED
        self.alt_colour = D_RED
        
        self.speed = 1
        self.max_health = self.health = 40
        self.direction = "N"
        self.shot_cool = 100
        self.shot_time = 0
        self.super_cool = 10000
        self.super_time = 0

        self.dir_index = 0
        self.directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 64:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 64:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (8, 8), 1, 12, self.directions[int(self.dir_index)], WHITE, target_type=Player, particles=[False, None]))
            if self.health <= 20:
                main_group.add(Projectile(self.rect.center, (8, 8), 1, 12, inverse_direction(self.directions[int(self.dir_index)]), WHITE, target_type=Player, particles=[False, None]))
            self.dir_index += 0.2
            if self.dir_index >= 8:
                self.dir_index = 0
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            for i in range(9):
                main_group.add(Projectile((-i * 32 + 543, 463), (16, 16), 1, 8, "NW", ORANGE, target_type=Player, particles=[False, None], delay=i * 45 + 30))
                main_group.add(Projectile((i * 32 + 17, 463), (16, 16), 1, 8, "NE", ORANGE, target_type=Player, particles=[False, None], delay=(9 - i) * 45 + 150))
                main_group.add(Projectile((-i * 32 + 543, 463), (16, 16), 1, 8, "NW", ORANGE, target_type=Player, particles=[False, None], delay=(9 - i) * 45 + 30))
                main_group.add(Projectile((i * 32 + 17, 463), (16, 16), 1, 8, "NE", ORANGE, target_type=Player, particles=[False, None], delay=i * 45 + 150))
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Vampire(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(D_RED)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "Count Necros"
        self.colour = D_RED
        self.alt_colour = D_GREY
        
        self.speed = 3
        self.max_health = self.health = 10
        self.direction = "N"
        self.shot_cool = 1500
        self.shot_time = 0
        self.super_cool = 3000
        self.super_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 40:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 40:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (10, 10), 2, 2, "N", RED, target_type=Player, particles=[True, L_RED], drain=1))
            main_group.add(Projectile(self.rect.center, (10, 10), 1, 2, "NE", D_RED, target_type=Player, particles=[True, L_RED], drain=2))
            main_group.add(Projectile(self.rect.center, (10, 10), 2, 2, "E", RED, target_type=Player, particles=[True, L_RED], drain=1))
            main_group.add(Projectile(self.rect.center, (10, 10), 1, 2, "SE", D_RED, target_type=Player, particles=[True, L_RED], drain=2))
            main_group.add(Projectile(self.rect.center, (10, 10), 2, 2, "S", RED, target_type=Player, particles=[True, L_RED], drain=1))
            main_group.add(Projectile(self.rect.center, (10, 10), 1, 2, "SW", D_RED, target_type=Player, particles=[True, L_RED], drain=2))
            main_group.add(Projectile(self.rect.center, (10, 10), 2, 2, "W", RED, target_type=Player, particles=[True, L_RED], drain=1))
            main_group.add(Projectile(self.rect.center, (10, 10), 1, 2, "NW", D_RED, target_type=Player, particles=[True, L_RED], drain=2))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            for i in range(randint(1, 3)):
                if randint(1, 2) == 1:
                    main_group.add(Projectile((17, randint(9, 471)), (24, 64), 1, 24, "E", RED, target_type=Player, particles=[False, None], delay=10))
                else:
                    main_group.add(Projectile((543, randint(9, 471)), (24, 64), 1, 24, "W", RED, target_type=Player, particles=[False, None], delay=10))
            
                if randint(1, 2) == 1:
                    main_group.add(Projectile((randint(9, 551), 17), (24, 64), 1, 24, "S", RED, target_type=Player, particles=[False, None], delay=10))
                else:
                    main_group.add(Projectile((randint(9, 551), 463), (24, 64), 1, 24, "N", RED, target_type=Player, particles=[False, None], delay=10))
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Summoned(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((24, 24))
        self.image.fill(D_BLUE)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "Summoned"
        self.colour = D_BLUE
        self.alt_colour = D_PURPLE
        
        self.speed = 2
        self.max_health = self.health = 5
        self.direction = "N"
        self.shot_cool = 1000
        self.shot_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 24:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 24:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0: 
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (5, 10), 1, 8, self.direction, D_GREEN, target_type=Player, particles=[True, GREEN]))
                
            self.shot_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()

class Summoner(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(D_GREEN)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Summoner"
        self.colour = D_GREEN
        self.alt_colour = GREEN
        
        self.speed = 1
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 2000
        self.shot_time = 0
        self.super_cool = 10000
        self.super_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 64:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 64:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (10, 20), 2, 16, self.direction, D_ORANGE, target_type=Player, particles=[True, L_GREEN]))
            main_group.add(Projectile(self.rect.center, (10, 20), 2, 16, self.direction, D_ORANGE, target_type=Player, particles=[True, L_GREEN], delay=30))
            main_group.add(Projectile(self.rect.center, (10, 20), 2, 16, self.direction, D_ORANGE, target_type=Player, particles=[True, L_GREEN], delay=45))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Summoned(self.rect.center))
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Artificer(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((48, 48))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Artificer"
        self.colour = YELLOW
        self.alt_colour = L_ORANGE
        
        self.speed = 1
        self.max_health = self.health = 25
        self.direction = "N"
        self.shot_cool = 1750
        self.shot_time = 0
        self.super_cool = 5000
        self.super_time = 0
        self.ability_cool = 3500
        self.ability_time = 0
        
        self.charges = 0
        self.bullets = 1

    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 48:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 48:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            for i in range(self.bullets):
                main_group.add(HomingProjectile(self.rect.center, (20, 20), 1, 2, self.direction, D_GREY, target_type=Player, particles=[False, None], delay=30*i))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            for i in range(50):
                main_group.add(Particle(self.rect.center, (8, 8), ORANGE, choice([1, 4]), 3))
            self.charges += 1
            if self.super_cool > 1500:
                self.super_cool -= 100
            self.super_time = pygame.time.get_ticks()
        
        if self.ability_cool + self.ability_time < pygame.time.get_ticks():
            for i in range(50):
                main_group.add(Particle(self.rect.center, (4, 4), WHITE, choice([1, 4]), 3))
            for i in range(self.charges):
                if not randint(0, 9):
                    self.bullets += 1
            self.ability_time = pygame.time.get_ticks()

        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Sorcerer(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(L_PURPLE)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Sorcerer"
        self.colour = PURPLE
        self.alt_colour = PINK
        
        self.speed = 2
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 2000
        self.shot_time = 0
        self.super_cool = 5000
        self.super_time = 0
        self.metamagic_text = font.render("Fast", True, WHITE)

        self.metamagic_options = ["Large", "Fast", "Powerful", "Drain", "Split", "Homing", "Shadow", "Double"]
        self.active_metamagic = ["Fast"]
        
    def update(self):
        size = [16, 16]
        speed = 12
        damage = 1
        drain = 0
        split = False
        homing = False
        opacity = 255
        doubles = 1
        proj_colour = L_BLUE

        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - 64:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - 64:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 0:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            for meta in self.active_metamagic:
                if meta == "Large":
                    size[0] += 10
                    size[1] += 10
                if meta == "Fast": speed += 4
                if meta == "Powerful": damage += 1
                if meta == "Drain": drain += 1
                if meta == "Split": split = True
                if meta == "Homing": homing = True
                if meta == "Shadow":
                    opacity -= 50
                    if opacity < 5: opacity = 5
                    proj_colour = BLACK
                if meta == "Double":
                    doubles += 1

            for i in range(doubles):
                if homing:
                    main_group.add(HomingProjectile(self.rect.center, size, damage, speed//4, self.direction, proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity))
                    if split:
                        main_group.add(HomingProjectile(self.rect.center, size, damage, speed//4, adjacent_direction(self.direction)[0], proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity))
                        main_group.add(HomingProjectile(self.rect.center, size, damage, speed//4, adjacent_direction(self.direction)[1], proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity))
                else:
                    main_group.add(Projectile(self.rect.center, size, damage, speed, self.direction, proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity))
                    if split:
                        main_group.add(Projectile(self.rect.center, size, damage, speed, adjacent_direction(self.direction)[0], proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity))
                        main_group.add(Projectile(self.rect.center, size, damage, speed, adjacent_direction(self.direction)[1], proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity))
                
            self.shot_cool = self.health * 50 + 500
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            random_metamagic = choice(self.metamagic_options)
            if self.health > 15:
                self.metamagic_text = font.render(f"{self.active_metamagic[0]} -> {random_metamagic}", True, WHITE)
                self.active_metamagic = [random_metamagic]
            else:
                self.metamagic_text = font.render(f"+ {random_metamagic}", True, WHITE)
                self.active_metamagic.append(random_metamagic)
            
            self.super_time = pygame.time.get_ticks()
        
        screen.blit(self.metamagic_text, (self.rect.x, self.rect.y - 32))

        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

# Weapon Classes
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, size, damage, speed, direction, colour, target_type=Enemy, particles=[True, WHITE], seeking=False, delay=0, drain=0, alpha=255): # Particles list is 'particles enabled' then 'particle colour'
        super().__init__()
        self.image = pygame.Surface(size)
        if direction in ["W", "E"]:
            self.image = pygame.transform.rotate(self.image, 90)
        if direction in ["NE", "SW"]:
            self.image = pygame.transform.rotate(self.image, 45)
        if direction in ["NW", "SE"]:
            self.image = pygame.transform.rotate(self.image, 135)
        self.image.fill(colour)
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect(center=pos)
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.target_type = target_type
        self.particles = particles[0]
        self.part_colour = particles[1]
        self.seeking = seeking
        self.delay = delay
        self.drain = drain
        
        if seeking:
            if self.target_type == Player:
                self.target = player.rect.center
            elif self.target_type == Enemy:
                self.target = boss.rect.center
            self.attack_time = pygame.time.get_ticks() + 2000
            self.attacked = False
            main_group.add(ParticleEmitter(self.target, (4, 4), L_RED, 4, 1000, 3))
        
    def update(self):
        if self.delay <= 0:
            if self.direction == "N":
                self.rect.y -= self.speed
                if self.particles:
                    if randint(1, 2) == 1:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                    else:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
            if self.direction == "E":
                self.rect.x += self.speed
                if self.particles:
                    if randint(1, 2) == 1:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                    else:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
            if self.direction == "S":
                self.rect.y += self.speed
                if self.particles:
                    if randint(1, 2) == 1:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                    else:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
            if self.direction == "W":
                self.rect.x -= self.speed
                if self.particles:
                    if randint(1, 2) == 1:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                    else:
                        main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
            if self.direction == "NE":
                self.rect.x += self.speed // 2
                self.rect.y -= self.speed // 2
                if self.particles:
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed//0.75))
            if self.direction == "SE":
                self.rect.x += self.speed // 2
                self.rect.y += self.speed // 2
                if self.particles:
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed//0.75))
            if self.direction == "SW":
                self.rect.x -= self.speed // 2
                self.rect.y += self.speed // 2
                if self.particles:
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed//0.75))
            if self.direction == "NW":
                self.rect.x -= self.speed // 2
                self.rect.y -= self.speed // 2
                if self.particles:
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed//0.75))
        
            for sprite in main_group:
                if isinstance(sprite, self.target_type) and self.rect.colliderect(sprite.rect):
                    if isinstance(sprite, Enemy):
                        sprite.take_damage(self.damage)
                        player.health += self.drain
                    else:
                        sprite.health -= self.damage
                        boss.health += self.drain
                    self.kill()
                    break
        
            if self.seeking:
                if self.attack_time < pygame.time.get_ticks() and not self.attacked:
                    self.image = pygame.transform.scale(self.image, (8, 8))
                    self.image.fill(D_RED)
                    self.rect = self.image.get_rect(center=self.target)
                    self.attacked = True
                    self.part_colour = ORANGE
                if self.attack_time < pygame.time.get_ticks():
                    self.image = pygame.transform.scale(self.image, (self.rect.width + 2, self.rect.height + 2))
                    self.rect = self.image.get_rect(center=self.target)
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                if self.attack_time + 500 < pygame.time.get_ticks():
                    self.kill()
        
            if not self.rect.colliderect(screen.get_rect()) and not self.seeking:
                self.kill()
        
        if self.delay > 0:
            self.delay -= 1

class HomingProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, size, damage, speed, direction, colour, target_type=Enemy, particles=[True, WHITE], seeking=False, delay=0, drain=0, alpha=255): # Particles list is 'particles enabled' then 'particle colour'
        super().__init__()
        self.image = pygame.Surface(size)
        if direction in ["W", "E"]:
            self.image = pygame.transform.rotate(self.image, 90)
        if direction in ["NE", "SW"]:
            self.image = pygame.transform.rotate(self.image, 45)
        if direction in ["NW", "SE"]:
            self.image = pygame.transform.rotate(self.image, 135)
        self.image.fill(colour)
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect(center=pos)
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.target_type = target_type
        self.particles = particles[0]
        self.part_colour = particles[1]
        self.seeking = seeking
        self.delay = delay
        self.drain = drain

        self.vx = 0
        self.vy = 0
        self.terminal_velocity = (self.speed * 1.8) ** 2
        
        if seeking:
            if self.target_type == Player:
                self.target = player.rect.center
            elif self.target_type == Enemy:
                self.target = boss.rect.center
            self.attack_time = pygame.time.get_ticks() + 2000
            self.attacked = False
            main_group.add(ParticleEmitter(self.target, (4, 4), L_RED, 4, 1000, 3))
        
    def update(self):
        if self.delay <= 0:
            if self.target_type == Player:
                if player.rect.y < self.rect.y:
                    self.vy -= self.speed / 3
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                if player.rect.x > self.rect.x:
                    self.vx += self.speed / 3
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                if player.rect.y > self.rect.y:
                    self.vy += self.speed / 3
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                if player.rect.x < self.rect.x:
                    self.vx -= self.speed / 3
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
            
            if self.vx > self.terminal_velocity:
                self.vx = self.terminal_velocity
            if self.vx < -self.terminal_velocity:
                self.vx = -self.terminal_velocity
            if self.vy > self.terminal_velocity:
                self.vy = self.terminal_velocity
            if self.vy < -self.terminal_velocity:
                self.vy = -self.terminal_velocity

            self.rect.x += self.vx
            self.rect.y += self.vy
        
            for sprite in main_group:
                if isinstance(sprite, self.target_type) and self.rect.colliderect(sprite.rect):
                    if isinstance(sprite, Enemy):
                        sprite.take_damage(self.damage)
                        player.health += self.drain
                    else:
                        sprite.health -= self.damage
                        boss.health += self.drain
                    self.kill()
                    break
        
            if self.seeking:
                if self.attack_time < pygame.time.get_ticks() and not self.attacked:
                    self.image = pygame.transform.scale(self.image, (8, 8))
                    self.image.fill(D_RED)
                    self.rect = self.image.get_rect(center=self.target)
                    self.attacked = True
                    self.part_colour = ORANGE
                if self.attack_time < pygame.time.get_ticks():
                    self.image = pygame.transform.scale(self.image, (self.rect.width + 2, self.rect.height + 2))
                    self.rect = self.image.get_rect(center=self.target)
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                    main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                if self.attack_time + 500 < pygame.time.get_ticks():
                    self.kill()
        
            if not self.rect.colliderect(screen.get_rect()) and not self.seeking:
                self.kill()
        
        if self.delay > 0:
            self.delay -= 1

# Visual Classes
class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, size, colour, quadrant, speed, strict_move=False):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(colour)
        self.rect = self.image.get_rect(center=pos)
        
        self.quadrant = quadrant
        self.speed = speed
        self.strict_move = strict_move
    
    def update(self):
        if self.quadrant == 1:
            if self.strict_move:
                self.rect.x += self.speed
            else:
                if randint(1, 2) == 1:
                    self.rect.x += self.speed
                else:
                    self.rect.y -= self.speed
        if self.quadrant == 2:
            if self.strict_move:
                self.rect.y += self.speed
            else:
                if randint(1, 2) == 1:
                    self.rect.y += self.speed
                else:
                    self.rect.x += self.speed
        if self.quadrant == 3:
            if self.strict_move:
                self.rect.x -= self.speed
            else:
                if randint(1, 2) == 1:
                    self.rect.x -= self.speed
                else:
                    self.rect.y += self.speed
        if self.quadrant == 4:
            if self.strict_move:
                self.rect.y -= self.speed
            else:
                if randint(1, 2) == 1:
                    self.rect.y -= self.speed
                else:
                    self.rect.x -= self.speed
        
        if not self.rect.colliderect(screen.get_rect()):
            self.kill()
        
        if random() < 0.1:
            self.kill()

class ParticleEmitter(pygame.sprite.Sprite):
    def __init__(self, pos, size, colour, speed, duration, emissionRate=1):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        
        self.size = size
        self.colour = colour
        self.speed = speed
        self.duration = pygame.time.get_ticks() + duration
        self.emission_rate = emissionRate
        
    def update(self):
        for rate in range(self.emission_rate):
            main_group.add(Particle(self.rect.center, self.size, self.colour, 1, self.speed))
            main_group.add(Particle(self.rect.center, self.size, self.colour, 2, self.speed))
            main_group.add(Particle(self.rect.center, self.size, self.colour, 3, self.speed))
            main_group.add(Particle(self.rect.center, self.size, self.colour, 4, self.speed))
        
        if self.duration < pygame.time.get_ticks():
            self.kill()

# Upgrades
class Upgrade(pygame.sprite.Sprite):
    def __init__(self, name, rarity, tier, effect1, effect2=None):
        super().__init__()
        self.image = pygame.Surface((160, 240))
        self.image.fill(M_GREY)
        self.rect = self.image.get_rect(center=(0, 0))
        
        self.name = name
        self.rarity = rarity   # 1 - Common, 2 - Uncommon, 3 - Rare, 4 - Epic, 5 - Legendary
        self.tier = tier       # 1 - Basic, 2/3 - Decent, 4/5 - Good, 6/7 - Great, 8/9 - Fantastic, 10 - Perfect
        self.weight = (16 - (rarity * 3)) * (21 - (tier * 2))
        self.activated = False
        
        if rarity == 1:
            self.rarity_name = "Common"
            self.rarity_colour = BLACK
        elif rarity == 2:
            self.rarity_name = "Uncommon"
            self.rarity_colour = D_BLUE
        elif rarity == 3:
            self.rarity_name = "Rare"
            self.rarity_colour = RED
        elif rarity == 4:
            self.rarity_name = "Epic"
            self.rarity_colour = PURPLE
        elif rarity == 5:
            self.rarity_name = "Legendary"
            self.rarity_colour = L_ORANGE
        else:
            self.rarity_name = "Unknown"
            self.rarity_colour = White
        
        if tier == 1:
            self.tier_name = "Basic"
        elif tier in [2, 3]:
            self.tier_name = "Decent"
        elif tier in [4, 5]:
            self.tier_name = "Good"
        elif tier in [6, 7]:
            self.tier_name = "Great"
        elif tier in [8, 9]:
            self.tier_name = "Fantastic"
        elif tier == 10:
            self.tier_name = "Perfect"
        else:
            self.tier_name = "Unknown"
        
        self.effect1 = effect1  # Effects are: [Name, Description, Severity]
        self.eff1_desc = f"{effect1[0]}: {effect1[1].replace('$$', f'{effect1[2]}')}"
        if effect2:
            self.effect2 = effect2
            self.eff2_desc = f"{effect2[0]}: {effect2[1].replace('$$', f'{effect2[2]}')}"
        else: self.eff2_desc = ""
    
    def update(self):
        name_text = card_font.render(self.name, True, WHITE)
        self.image.blit(name_text, (4, 0))
        rarity_text = small_card_font.render(f"{self.rarity_name} | {self.tier_name} ({self.tier})", True, self.rarity_colour)
        self.image.blit(rarity_text, (4, 24))
        
        for text, y in ((self.eff1_desc, 160), (self.eff2_desc, 200)):
            for line in wrap_text(text, small_card_font, self.image.get_width() - 8):
                self.image.blit(small_card_font.render(line, True, WHITE), (4, y))
                y += small_card_font.get_linesize()
        
        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and mouse[0]:
            global game_state, item_chosen
            player.upgrades.append(self)
            game_state = "Fight"
            item_chosen = True

upgrade_list = [
    Upgrade("Rapid Fire", 1, 1, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 5]),
    Upgrade("Rapid Fire", 1, 2, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 10]),
    Upgrade("Rapid Fire", 1, 3, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 15]),
    Upgrade("Rapid Fire", 1, 4, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 20]),
    Upgrade("Rapid Fire", 1, 5, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 25]),
    Upgrade("Rapid Fire", 1, 6, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 30]),
    Upgrade("Rapid Fire", 1, 7, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 35]),
    Upgrade("Rapid Fire", 1, 8, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 40]),
    Upgrade("Rapid Fire", 1, 9, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 45]),
    Upgrade("Rapid Fire", 1, 10, ["Increased Attack Speed", "Your attack speed is increased by $$%.", 50])
]

upgrade_pool = []
for upgrade in upgrade_list:
    for i in range(upgrade.weight):
        upgrade_pool.append(upgrade)

# Groups
player = Player((16, 464))
boss_list = [Bomber((280, 240)), Warper((280, 240)), Cleric((280, 240)), Defender((280, 240)), Twister((280, 240)), Summoner((280, 240)), Artificer((280, 240)), Sorcerer((280, 240)), Vampire((280, 240))]
boss = Mage((280, 240))
main_group = pygame.sprite.Group()
main_group.add(player, boss)
upgrade_group = pygame.sprite.Group()
selected = False

# Mainloop
running = True
while running:
    if game_state == "Menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = "Fight"
        
        screen.fill(BLACK)

        screen.blit(title_font.render("The Dungeon Lurks", True, WHITE), (0, 0))
        screen.blit(subtitle_font.render(f"v{game_version}: {update_name}", True, WHITE), (0, 48))
        screen.blit(subtitle_font.render("Press SPACE to Begin!", True, WHITE), (88, 256))

        pygame.display.flip()
        clock.tick(FPS)
    
    if game_state == "Fight":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if boss.health <= 0 and len(boss_list) > 0:
            player.health = player.max_health
            player.ult_used = False
            boss = boss_list.pop(0)
            if isinstance(boss, Defender):
                boss.burst_time = pygame.time.get_ticks() + 5000
            boss.add(main_group)
        
        if len(boss_list) == 0:
            running = False
            
        screen.fill(BLACK)
        
        main_group.update()
        main_group.draw(screen)
    
        if player not in main_group:
            running = False
    
        screen.blit(font.render(f"HP: {player.health}/{player.max_health}", True, WHITE), (0, 0))
    
        bossbar_base = pygame.Surface((320, 16))
        bossbar_base.fill(D_GREY)
        screen.blit(bossbar_base, (120, 16))
    
        bossbar_val = pygame.Surface((abs(int(300/boss.max_health * boss.health)), 12))
        bossbar_val.fill(L_GREY)
        screen.blit(bossbar_val, (130, 18))
    
        bossbar_name_outline = boss_outline_font.render(boss.name, True, boss.alt_colour)
        screen.blit(bossbar_name_outline, (280 - (bossbar_name_outline.get_width()//2), -2))
    
        bossbar_name = boss_font.render(boss.name, True, boss.colour)
        screen.blit(bossbar_name, (280 - (bossbar_name.get_width()//2), 0))

        if hasattr(boss, "bullets"):
            bullet_text = font.render(f"Bullets: {boss.bullets}", True, WHITE)
            screen.blit(bullet_text, (boss.rect.x, boss.rect.y - 32))
    
        pygame.display.flip()
        clock.tick(FPS)

    if game_state == "Upgrade":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # TODO: Upgrade Game State + Upgrade Functionality
        
        if not selected:
            selected = True
            cards = choices(upgrade_pool, k=3)
            card1, card2, card3 = cards[:3]
            card1.rect.center = (90, 240)
            card2.rect.center = (280, 240)
            card3.rect.center = (470, 240)
            upgrade_group.add(card1, card2, card3)
        
        upgrade_group.draw(screen)
        upgrade_group.update()

        pygame.display.flip()
        clock.tick(FPS)

pygame.time.delay(500)
pygame.quit()