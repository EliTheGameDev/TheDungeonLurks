from random import *
import json
import tkinter as tk
from tkinter import messagebox
import pygame
pygame.init()

# Game Setup
game_version = 0.4
update_name = "Conquer Continually"

screen = pygame.display.set_mode((560, 480))
pygame.display.set_caption(f"The Dungeon Lurks - v{game_version} - {update_name}")
clock = pygame.time.Clock()
FPS = 60
game_states = ["Menu", "Fight", "Meta"]
game_state = game_states[0]
random_bosses = False

root = tk.Tk()
root.withdraw()

with open("save.json", "r") as f:
    save_data = json.load(f)

money = save_data["copper"] + int(save_data["silver"] * 10) + int(save_data["gold"] * 100) + int(save_data["platinum"] * 1000)

def recalc_money():
    md = str(money)
    tmd = ""
    plat = False
    while len(md) < 4:
        md = "0" + md
    if int(list(md)[-1]) > 0: tmd += f"{int(list(md)[-1])} CP "
    if int(list(md)[-2]) > 0: tmd += f"{int(list(md)[-2])} SP "
    if int(list(md)[-3]) > 0: tmd += f"{int(list(md)[-3])} GP "
    for x in list(md)[:-3]:
        if int(x) > 0:
            plat = True
    if plat: 
        for p in list(md)[:-3]: 
            tmd += p
        tmd += " PP"

    if len(tmd) > 0:
        return tmd
    else:
        return "Nothing"

money_display = recalc_money()

gamescreen = pygame.Surface((560, 432))
gamescreen_rect = gamescreen.get_rect(topleft=(0, 48))

# Fonts
font = pygame.font.SysFont("Forte", 16)
boss_font = pygame.font.SysFont("Impact", 24)
boss_outline_font = pygame.font.SysFont("Impact", 26, bold=True)
title_font = pygame.font.SysFont("Copperplate Gothic", 48)
subtitle_font = pygame.font.SysFont("Copperplate Gothic", 32)
note_font = pygame.font.SysFont("Copperplate Gothic", 16)

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
D_CYAN = (0, 191, 191)
CYAN = (0, 255, 255)
L_CYAN = (63, 255, 255)
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

D_UI = (15, 7, 0)
UI = (31, 23, 0)
L_UI = (63, 55, 31)
BG = (15, 11, 0)
BLENDED = (11, 7, 0)

redness = 0

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
    elif direction == "E":
        return ["NE", "SE"]
    elif direction == "S":
        return ["SE", "SW"]
    elif direction == "W":
        return["SW", "NW"]
    elif direction == "NE":
        return ["N", "E"]
    elif direction == "SE":
        return ["E", "S"]
    elif direction == "SW":
        return ["S", "W"]
    elif direction == "NW":
        return ["W", "N"]
    else:
        return ["N", "S"]

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

        # Upgradable Attributes
        self.shot_speed = 16
        self.shot_damage = 1
        self.shot_shape = (8, 16)
        self.shot_colour = GREEN
        self.shot_particles = (True, D_GREEN)
        self.shot_homing = False
        self.shot_bouncy = 0
        self.shot_seeking = False

        self.super_speed = 2
        self.super_damage = 2
        self.super_shape = (108, 24)
        self.super_colour = YELLOW
        self.super_particles = (False, YELLOW)
        self.super_homing = False
        self.super_bouncy = 0
        self.super_seeking = False

        self.ult_secondary = None
        self.evasion = 0
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.rect.y > 48:
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
            main_group.add(Projectile(self.rect.center, self.shot_shape, self.shot_damage, self.shot_speed, self.direction, self.shot_colour, particles=self.shot_particles, seeking=self.shot_seeking, destructive=True))
            self.shot_time = pygame.time.get_ticks()
        if keys[pygame.K_e] and self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, self.super_shape, self.super_damage, self.super_speed, self.direction, self.super_colour, particles=self.super_particles, seeking=self.super_seeking, destructive=True))
            self.super_time = pygame.time.get_ticks()
        if keys[pygame.K_q] and self.health <= 5 and not self.ult_used:
            self.health = self.max_health
            self.ult_time = pygame.time.get_ticks()
            self.ult_used = True
        
        if self.ult_time + self.ult_duration >= pygame.time.get_ticks() and self.ult_used:
            main_group.add(Particle(self.rect.center, (4, 4), WHITE, 1, 3), Particle(self.rect.center, (4, 4), WHITE, 2, 3), Particle(self.rect.center, (4, 4), WHITE, 3, 3), Particle(self.rect.center, (4, 4), WHITE, 4, 3))
        
        if self.health <= 0:
            self.kill()
            print("GAME OVER")
    
    def take_damage(self, damage, evasion_mod=0):
        if uniform(0, 1) > self.evasion + evasion_mod:
            if not (self.ult_time + self.ult_duration >= pygame.time.get_ticks() and self.ult_used):
                self.health -= damage
                for i in range(20*damage):
                    main_group.add(Particle(self.rect.center, (6, 6), RED, randint(1, 4), 3))
                global redness
                redness += damage * 4
            else:
                self.health = self.max_health
    
    def abort(self):
        pass

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def take_damage(self, damage):
        self.health -= damage
    
    def abort(self):
        self.kill()

class Scaffold(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(D_GREY)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = ""
        self.colour = WHITE
        self.alt_colour = M_GREY
        
        self.speed = 2
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 800
        self.shot_time = 0
        self.super_cool = 3000
        self.super_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - self.rect.w:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - self.rect.h:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (8, 16), 1, 8, self.direction, WHITE, target_type=Player, particles=[True, WHITE]))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (48, 8), 1, 2, self.direction, WHITE, target_type=Player, particles=[True, WHITE]))
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(1, 10)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

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
                if self.rect.y > 48: 
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            if self.health > 5:
                main_group.add(Projectile(self.rect.center, (32, 32), 3, 4, self.direction, RED, target_type=Player, particles=[True, ORANGE], destructive=True))
                if self.health < 10:
                    main_group.add(Projectile(self.rect.center, (32, 32), 3, 4, inverse_direction(self.direction), RED, target_type=Player, particles=[True, ORANGE], destructive=True))
            else:
                self.shot_cool = self.health * 300
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "N", RED, target_type=Player, particles=[True, ORANGE], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "E", RED, target_type=Player, particles=[True, ORANGE], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "S", RED, target_type=Player, particles=[True, ORANGE], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 24), 2, 8, "W", RED, target_type=Player, particles=[True, ORANGE], destructive=True))
                
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (16, 16), 2, 3, self.direction, PINK, target_type=Player, particles=[True, D_PINK], seeking=True))
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(3, 10)
            money_display = recalc_money()
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
                if self.rect.y > 48:
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
            global money, money_display
            money += randint(3, 10)
            money_display = recalc_money()
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
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (16, 32), 1, 7, self.pointing, L_YELLOW, target_type=Player, seeking=self.seek, destructive=True))
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
            global money, money_display
            money += randint(3, 10)
            money_display = recalc_money()
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
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (16, 16), 3, 1, self.direction, L_PURPLE, target_type=Player, particles=[True, D_PURPLE], seeking=True))
            
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            global gamescreen, gamescreen_rect
            screen_size = choice(self.screen_presets)
            screen = pygame.display.set_mode(screen_size)
            gamescreen = pygame.Surface((screen_size[0], screen_size[1] - 48))
            gamescreen_rect = gamescreen.get_rect(topleft=(0, 48))
            self.rect.center = (24, 72)
            player.rect.center = (screen.get_width(), screen.get_height())
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(3, 10)
            money_display = recalc_money()
            screen = pygame.display.set_mode((560, 480))
            gamescreen = pygame.Surface((560, 432))
            gamescreen_rect = gamescreen.get_rect(topleft=(0, 48))
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
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if burst_active and self.shot_cool + self.shot_time < now:
            if self.burst_dir == 0:
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "N", WHITE, target_type=Player, particles=[False, None], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "E", WHITE, target_type=Player, particles=[False, None], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "S", WHITE, target_type=Player, particles=[False, None], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 64), 1, 16, "W", WHITE, target_type=Player, particles=[False, None], destructive=True))
            else:
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "NE", WHITE, target_type=Player, particles=[False, None], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "NW", WHITE, target_type=Player, particles=[False, None], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "SE", WHITE, target_type=Player, particles=[False, None], destructive=True))
                main_group.add(Projectile(self.rect.center, (24, 24), 1, 16, "SW", WHITE, target_type=Player, particles=[False, None], destructive=True))

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
                    main_group.add(Projectile((17, randint(57, 471)), (24, 64), 1, 24, "E", RED, target_type=Player, particles=[False, None], delay=30, destructive=True))
                else:
                    main_group.add(Projectile((543, randint(57, 471)), (24, 64), 1, 24, "W", RED, target_type=Player, particles=[False, None], delay=30, destructive=True))
            
                if randint(1, 2) == 1:
                    main_group.add(Projectile((randint(9, 551), 65), (24, 64), 1, 24, "S", RED, target_type=Player, particles=[False, None], delay=30, destructive=True))
                else:
                    main_group.add(Projectile((randint(9, 551), 463), (24, 64), 1, 24, "N", RED, target_type=Player, particles=[False, None], delay=30, destructive=True))
            
            self.super_time = pygame.time.get_ticks()
            self.super_cool = self.health * 40 + 800

        if self.health <= 0:
            global money, money_display
            money += randint(10, 20)
            money_display = recalc_money()
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
        self.super_cool = 15000
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
                if self.rect.y > 48:
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
                main_group.add(Projectile((-i * 32 + 543, 463), (16, 16), 1, 8, "NW", ORANGE, target_type=Player, particles=[False, None], delay=i * 45 + 30, destructive=True))
                main_group.add(Projectile((i * 32 + 17, 463), (16, 16), 1, 8, "NE", ORANGE, target_type=Player, particles=[False, None], delay=(9 - i) * 45 + 150, destructive=True))
                main_group.add(Projectile((-i * 32 + 543, 463), (16, 16), 1, 8, "NW", ORANGE, target_type=Player, particles=[False, None], delay=(9 - i) * 45 + 30, destructive=True))
                main_group.add(Projectile((i * 32 + 17, 463), (16, 16), 1, 8, "NE", ORANGE, target_type=Player, particles=[False, None], delay=i * 45 + 150, destructive=True))
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(5, 12)
            money_display = recalc_money()
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
                if self.rect.y > 48:
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
                    main_group.add(Projectile((17, randint(57, 471)), (24, 64), 1, 24, "E", RED, target_type=Player, particles=[False, None], delay=10, destructive=True))
                else:
                    main_group.add(Projectile((543, randint(57, 471)), (24, 64), 1, 24, "W", RED, target_type=Player, particles=[False, None], delay=10, destructive=True))
            
                if randint(1, 2) == 1:
                    main_group.add(Projectile((randint(9, 551), 65), (24, 64), 1, 24, "S", RED, target_type=Player, particles=[False, None], delay=10, destructive=True))
                else:
                    main_group.add(Projectile((randint(9, 551), 463), (24, 64), 1, 24, "N", RED, target_type=Player, particles=[False, None], delay=10, destructive=True))
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(15, 25)
            money_display = recalc_money()
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
        self.shot_cool = 1500
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
                if self.rect.y > 48: 
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
        self.max_health = self.health = 25
        self.direction = "N"
        self.shot_cool = 2000
        self.shot_time = 0
        self.super_cool = 20000
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
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (10, 20), 1, 16, self.direction, D_ORANGE, target_type=Player, particles=[True, L_GREEN]))
            main_group.add(Projectile(self.rect.center, (10, 20), 1, 16, self.direction, D_ORANGE, target_type=Player, particles=[True, L_GREEN], delay=30))
            main_group.add(Projectile(self.rect.center, (10, 20), 1, 16, self.direction, D_ORANGE, target_type=Player, particles=[True, L_GREEN], delay=45))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Summoned(self.rect.center))
            
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(5, 12)
            money_display = recalc_money()
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
                if self.rect.y > 48:
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
            global money, money_display
            money += randint(5, 12)
            money_display = recalc_money()
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
        destructive = False

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
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            for meta in self.active_metamagic:
                if meta == "Large":
                    size[0] += 10
                    size[1] += 10
                    destructive = True
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
                    main_group.add(Projectile(self.rect.center, size, damage, speed, self.direction, proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity, destructive=destructive))
                    if split:
                        main_group.add(Projectile(self.rect.center, size, damage, speed, adjacent_direction(self.direction)[0], proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity, destructive=destructive))
                        main_group.add(Projectile(self.rect.center, size, damage, speed, adjacent_direction(self.direction)[1], proj_colour, target_type=Player, particles=[True, D_BLUE], delay=i*20, drain=drain, alpha=opacity, destructive=destructive))
                
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
            global money, money_display
            money += randint(5, 12)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Shadow(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(BLENDED)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Shadow"
        self.colour = D_GREY
        self.alt_colour = BLACK
        
        self.speed = 0
        self.max_health = self.health = 20
        self.direction = "N"
        self.shot_cool = 800
        self.shot_time = 0
        self.super_cool = 8000
        self.super_time = 0

        self.positions = [(16, 64), (544, 64), (280, 264), (16, 464), (544, 464)]
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                self.direction = "E"
            else:
                self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                self.direction = "S"
            else:
                self.direction = "N"
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            self.image.fill(BG) 
            main_group.add(Particle(self.rect.center, (randint(4, 12), randint(4, 12)), D_GREY, randint(1, 4), 1))
            main_group.add(Particle(self.rect.center, (randint(4, 12), randint(4, 12)), D_GREY, randint(1, 4), 1))
            main_group.add(Particle(self.rect.center, (randint(4, 12), randint(4, 12)), D_GREY, randint(1, 4), 1))
        elif self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(HomingProjectile(self.rect.center, (8, 16), 1, 2, self.direction, BG, target_type=Player, particles=[True, D_ORANGE]))
            if self.health < 10:
                main_group.add(HomingProjectile(self.rect.center, (8, 16), 1, 2, self.direction, BG, target_type=Player, particles=[True, D_ORANGE], delay=10))
            
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time + 2000 < pygame.time.get_ticks():
            self.image.fill(BLENDED)
            self.rect.center = choice(self.positions)
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(8, 15)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health
    
    def take_damage(self, damage):
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            pass
        else:
            self.health -= damage

class Ranger(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(D_GREEN)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Ranger"
        self.colour = GREEN
        self.alt_colour = D_CYAN
        
        self.speed = 1
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 600
        self.shot_time = 0
        self.super_cool = 2500
        self.super_time = 0
        self.burst_cool = 4000
        self.burst_time = 0

        self.point = (0, 0)
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - self.rect.w:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - self.rect.h:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            if self.health > 20:
                main_group.add(HomingProjectile(self.rect.center, (10, 10), 2, 2, self.direction, CYAN, target_type=self.point, particles=[True, L_CYAN], seeking=True, donthit=(Enemy), speed_mult=3))
            elif self.health > 10:
                main_group.add(HomingProjectile(self.rect.center, (10, 10), 2, 2, self.direction, CYAN, target_type=self.point, particles=[True, L_CYAN], seeking=True, donthit=(Enemy), speed_mult=3))
                main_group.add(HomingProjectile(self.rect.center, (10, 10), 2, 2, self.direction, CYAN, target_type=self.point, particles=[True, L_CYAN], seeking=True, delay=10, donthit=(Enemy), speed_mult=3))
            else:
                main_group.add(HomingProjectile(self.rect.center, (10, 10), 2, 2, self.direction, CYAN, target_type=self.point, particles=[True, L_CYAN], seeking=True, donthit=(Enemy), speed_mult=3))
                main_group.add(HomingProjectile(self.rect.center, (10, 10), 2, 2, self.direction, CYAN, target_type=self.point, particles=[True, L_CYAN], seeking=True, delay=10, donthit=(Enemy), speed_mult=3))
                main_group.add(HomingProjectile(self.rect.center, (10, 10), 2, 2, self.direction, CYAN, target_type=self.point, particles=[True, L_CYAN], seeking=True, delay=20, donthit=(Enemy), speed_mult=3))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            self.point = player.rect.center
            self.super_time = pygame.time.get_ticks()
        
        if self.burst_cool + self.burst_time < pygame.time.get_ticks():
            main_group.add(HomingProjectile(self.rect.center, (10, 10), 1, 1, self.direction, CYAN, target_type=Player, particles=[True, L_CYAN], speed_mult=5))
            main_group.add(HomingProjectile(self.rect.center, (10, 10), 1, 1, self.direction, CYAN, target_type=Player, delay=10, particles=[True, L_CYAN], speed_mult=5))
            main_group.add(HomingProjectile(self.rect.center, (10, 10), 1, 1, self.direction, CYAN, target_type=Player, delay=20, particles=[True, L_CYAN], speed_mult=5))
            main_group.add(HomingProjectile(self.rect.center, (10, 10), 1, 1, self.direction, CYAN, target_type=Player, delay=30, particles=[True, L_CYAN], speed_mult=5))
            self.burst_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(8, 15)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Magnet(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Magnet"
        self.colour = RED
        self.alt_colour = CYAN
        
        self.speed = 2
        self.max_health = self.health = 20
        self.direction = "N"
        self.shot_cool = 800
        self.shot_time = 0
        self.super_cool = 10000
        self.super_time = 0

        self.polarisation = 1 # 1 is Red (+), -1 is Blue (-)
        
    def update(self):
        if self.polarisation == 1:
            if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
                if player.rect.x > self.rect.x:
                    if self.rect.x < screen.get_width() - self.rect.w:
                        self.rect.x += self.speed
                        self.direction = "E"
                else:
                    if self.rect.x > 0:
                        self.rect.x -= self.speed
                        self.direction = "W"
            else:
                if player.rect.y > self.rect.y:
                    if self.rect.y < screen.get_height() - self.rect.h:
                        self.rect.y += self.speed
                        self.direction = "S"
                else:
                    if self.rect.y > 48:
                        self.rect.y -= self.speed
                        self.direction = "N"
        else:
            if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
                if player.rect.x < self.rect.x:
                    if self.rect.x < screen.get_width() - self.rect.w:
                        self.rect.x += self.speed
                        self.direction = "E"
                else:
                    if self.rect.x > 0:
                        self.rect.x -= self.speed
                        self.direction = "W"
            else:
                if player.rect.y < self.rect.y:
                    if self.rect.y < screen.get_height() - self.rect.h:
                        self.rect.y += self.speed
                        self.direction = "S"
                else:
                    if self.rect.y > 48:
                        self.rect.y -= self.speed
                        self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            if self.polarisation == 1:
                main_group.add(Projectile(self.rect.center, (8, 8), 2, 6, self.direction, D_RED, target_type=Player, particles=[True, D_CYAN]))
                main_group.add(Projectile(self.rect.center, (8, 8), 2, 6, adjacent_direction(self.direction)[0], D_RED, target_type=Player, particles=[True, D_CYAN]))
                main_group.add(Projectile(self.rect.center, (8, 8), 2, 6, adjacent_direction(self.direction)[1], D_RED, target_type=Player, particles=[True, D_CYAN]))
            else:
                main_group.add(HomingProjectile((280, 264), (16, 16), 1, 1, self.direction, L_CYAN, target_type=Player, particles=[True, L_RED], drain=1))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            self.polarisation *= -1
            if self.polarisation == 1:
                self.image.fill(RED)
                self.colour = RED
                self.alt_colour = CYAN
            else:
                self.image.fill(CYAN)
                self.colour = CYAN
                self.alt_colour = RED
            
            self.super_cool = 10000 + randint(-5000, 5000)
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(8, 15)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health
    
    def take_damage(self, damage):
        if self.polarisation == -1:
            pass
        else:
            self.health -= damage

class Decayed(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((24, 24))
        self.image.fill(D_GREEN)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Decayed"
        self.colour = D_PURPLE
        self.alt_colour = D_GREEN
        
        self.speed = 1
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 1500
        self.shot_time = 0
        self.super_cool = 2000
        self.super_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - self.rect.w:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - self.rect.h:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(HomingProjectile((8, 56), (8, 8), 2, 2, "SE", PURPLE, target_type=(Player, Enemy), particles=[True, D_PURPLE], speed_mult=1.5))
            if self.health <= 15: main_group.add(HomingProjectile((552, 472), (8, 8), 2, 2, "NW", PURPLE, target_type=(Player, Enemy), particles=[True, D_PURPLE], speed_mult=1.5))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            self.health -= 1
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(8, 15)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health
        
    def take_damage(self, damage):
        player.take_damage(damage)

class Zombie(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(D_GREEN)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "Zombie Adventurer"
        self.colour = D_GREEN
        self.alt_colour = GREEN
        
        self.speed = 1
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 300
        self.shot_time = 0
        self.super_cool = 2000
        self.super_time = 0
        self.ult_used = False
        self.ult_time = 0
        self.ult_duration = 5000
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - self.rect.w:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - self.rect.h:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (8, 16), 1, 16, self.direction, GREEN, target_type=Player, particles=[True, D_GREEN], destructive=True))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (108, 24), 2, 2, self.direction, YELLOW, target_type=Player, particles=[False, YELLOW], destructive=True))
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 8 and not self.ult_used:
            self.health = self.max_health
            self.ult_time = pygame.time.get_ticks()
            self.ult_used = True
        
        if self.ult_time + self.ult_duration >= pygame.time.get_ticks() and self.ult_used:
            self.health = self.max_health
            main_group.add(Particle(self.rect.center, (4, 4), WHITE, 1, 3), Particle(self.rect.center, (4, 4), WHITE, 2, 3), Particle(self.rect.center, (4, 4), WHITE, 3, 3), Particle(self.rect.center, (4, 4), WHITE, 4, 3))
        
        if self.health <= 0:
            global money, money_display
            money += randint(20, 30)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Jester(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Jester"
        self.colour = RED
        self.alt_colour = WHITE
        
        self.speed = 3
        self.max_health = self.health = 30
        self.direction = "N"
        self.shot_cool = 2000
        self.shot_time = 0
        self.super_cool = 12000
        self.super_time = 0
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - self.rect.w:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - self.rect.h:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(BouncingProjectile(self.rect.center, (32, 32), 1, 12, self.direction, RED, target_type=Player, bounces=10, particles=[True, WHITE]))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            rand_num = randint(0, 30)
            rand_range = list(range(rand_num * 16 + 8, rand_num * 16 + 88))
            for i in range(8,560,16):
                if not i in rand_range: main_group.add(Projectile((i, 456), (12, 48), 1, 32, "N", YELLOW, target_type=Player, particles=[True, WHITE], delay=i))
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(10, 18)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Illusionist(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((24, 24))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Illusionist"
        self.colour = WHITE
        self.alt_colour = L_GREY
        
        self.speed = 2
        self.max_health = self.health = 25
        self.direction = "N"
        self.shot_cool = 1200
        self.shot_time = 0
        self.super_cool = 10000
        self.super_time = 0
        self.tp_time = 5000
        self.tp_used = True

        self.illusion_pos = [(0, 0), (0, 0), (0, 0)]
        
    def update(self):
        if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
            if player.rect.x > self.rect.x:
                if self.rect.x < screen.get_width() - self.rect.w:
                    self.rect.x += self.speed
                    self.direction = "E"
            else:
                if self.rect.x > 0:
                    self.rect.x -= self.speed
                    self.direction = "W"
        else:
            if player.rect.y > self.rect.y:
                if self.rect.y < screen.get_height() - self.rect.h:
                    self.rect.y += self.speed
                    self.direction = "S"
            else:
                if self.rect.y > 48:
                    self.rect.y -= self.speed
                    self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(BouncingProjectile(self.rect.center, (8, 8), 2, 8, self.direction, WHITE, target_type=Player, bounces=0, particles=[False, WHITE]))
            main_group.add(BouncingProjectile(self.rect.center, (8, 8), 2, 8, inverse_direction(self.direction), WHITE, target_type=Player, bounces=0, particles=[False, WHITE]))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            self.tp_used = False
            for n in range(3): main_group.add(Illusion((randint(0, screen.get_width() - 24), randint(48, screen.get_height() - 24)), n, (self.max_health - self.health) // 5))
            self.super_time = pygame.time.get_ticks()
        
        if self.super_cool + self.tp_time < pygame.time.get_ticks() and not self.tp_used:
            self.rect.center = choice(self.illusion_pos)
            self.tp_used = True
            self.tp_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(10, 18)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

    def take_damage(self, damage):
        if self.tp_used: self.health -= damage
        else: pass

class Illusion(Enemy):
    def __init__(self, pos, number, tier):
        super().__init__()
        self.image = pygame.Surface((24, 24))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=pos)
        
        self.number = number
        self.colour = WHITE
        self.alt_colour = L_GREY
        
        self.speed = 2
        self.max_health = self.health = 999
        self.direction = "N"
        self.shot_cool = 1200
        self.shot_time = 0

        self.tier = tier
        
    def update(self):
        if randint(0, self.tier):
            if abs(player.rect.x - self.rect.x) > abs(player.rect.y - self.rect.y):
                if player.rect.x > self.rect.x:
                    if self.rect.x < screen.get_width() - self.rect.w:
                        self.rect.x += self.speed
                        self.direction = "E"
                else:
                    if self.rect.x > 0:
                        self.rect.x -= self.speed
                        self.direction = "W"
            else:
                if player.rect.y > self.rect.y:
                    if self.rect.y < screen.get_height() - self.rect.h:
                        self.rect.y += self.speed
                        self.direction = "S"
                else:
                    if self.rect.y > 48:
                        self.rect.y -= self.speed
                        self.direction = "N"

        else: 
            if boss.name == "The Illusionist":
                if not boss.tp_used:
                    boss.illusion_pos[self.number] = self.rect.center
                else:
                    self.kill()
            else:
                self.kill()
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(BouncingProjectile(self.rect.center, (8, 8), 0, 8, self.direction, WHITE, target_type=Player, bounces=0, particles=[False, WHITE]))
            main_group.add(BouncingProjectile(self.rect.center, (8, 8), 0, 8, inverse_direction(self.direction), WHITE, target_type=Player, bounces=0, particles=[False, WHITE]))
            self.shot_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

class Ship(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((24, 128))
        self.image.fill(D_GREY)
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "The Ship"
        self.colour = D_GREY
        self.alt_colour = BLACK
        
        self.speed = 1
        self.max_health = self.health = 50
        self.direction = "N"
        self.shot_cool = 800
        self.shot_time = 0
        self.super_cool = 3000
        self.super_time = 0
        
    def update(self):
        if player.rect.y > self.rect.y:
            if self.rect.y < screen.get_height() - self.rect.h:
                self.rect.y += self.speed
                self.direction = "S"
        else:
            if self.rect.y > 48:
                self.rect.y -= self.speed
                self.direction = "N"
        
        if self.shot_cool + self.shot_time < pygame.time.get_ticks():
            main_group.add(Projectile(self.rect.center, (20, 32), 3, 20, "W", RED, target_type=Player, particles=[True, D_RED], seeking=True))
            self.shot_time = pygame.time.get_ticks()
        
        if self.super_cool + self.super_time < pygame.time.get_ticks():
            main_group.add(BouncingProjectile((self.rect.centerx - 20, self.rect.centery - 64), (12, 12), 1, 12, "NW", PINK, target_type=Player, bounces=3, particles=[True, D_PINK]))
            main_group.add(BouncingProjectile((self.rect.centerx - 20, self.rect.centery), (12, 12), 1, 12, "W", PINK, target_type=Player, bounces=3, particles=[True, D_PINK]))
            main_group.add(BouncingProjectile((self.rect.centerx - 20, self.rect.centery + 64), (12, 12), 1, 12, "SW", PINK, target_type=Player, bounces=3, particles=[True, D_PINK]))
            self.super_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            global money, money_display
            money += randint(10, 18)
            money_display = recalc_money()
            self.kill()
        elif self.health > self.max_health:
            self.health = self.max_health

# Weapon Classes
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, size, damage, speed, direction, colour, target_type=Enemy, particles=[True, WHITE], seeking=False, delay=0, drain=0, alpha=255, destructive=False, evasion_resist=0): # Particles list is 'particles enabled' then 'particle colour'
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
        self.destructive = destructive
        self.evasion_resist = evasion_resist
        
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
                if isinstance(sprite, Projectile) and sprite.destructive and not self.destructive and self.rect.colliderect(sprite.rect):
                    self.kill()
                    break
                if isinstance(sprite, self.target_type) and self.rect.colliderect(sprite.rect):
                    if isinstance(sprite, Enemy):
                        sprite.take_damage(self.damage)
                        player.health += self.drain
                    else:
                        sprite.take_damage(self.damage, evasion_mod=-self.evasion_resist)
                        boss.health += self.drain
                    self.kill()
                    break
        
            if self.seeking:
                if self.attack_time < pygame.time.get_ticks() and not self.attacked:
                    self.destructive = True
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
        
            if not self.rect.colliderect(gamescreen_rect) and not self.seeking:
                self.kill()
        
        if self.delay > 0:
            self.delay -= 1
    
    def abort(self):
        self.kill()

class HomingProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, size, damage, speed, direction, colour, target_type=Enemy, particles=[True, WHITE], seeking=False, delay=0, drain=0, alpha=255, donthit=(), speed_mult=1, resist_evasion=0.2): # Particles list is 'particles enabled' then 'particle colour'
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
        self.dont_hit = donthit
        self.speed_mult = speed_mult
        self.resist_evasion = resist_evasion

        self.vx = 0
        self.vy = 0
        self.terminal_velocity = (self.speed * 1.8) ** 2 * speed_mult
        
        if seeking:
            if self.target_type == Player:
                self.target = player.rect.center
            elif self.target_type == Enemy:
                self.target = boss.rect.center
            else:
                self.target = player.rect.center
            self.attack_time = pygame.time.get_ticks() + 2000
            self.attacked = False
            main_group.add(ParticleEmitter(self.target, (4, 4), L_RED, 4, 1000, 3))
        
    def update(self):
        if self.delay <= 0:
            if self.target_type == Player:
                if player.rect.y < self.rect.y:
                    self.vy -= self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                if player.rect.x > self.rect.x:
                    self.vx += self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                if player.rect.y > self.rect.y:
                    self.vy += self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                if player.rect.x < self.rect.x:
                    self.vx -= self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                            
            elif self.target_type == Enemy:
                if boss.rect.y < self.rect.y:
                    self.vy -= self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                if boss.rect.x > self.rect.x:
                    self.vx += self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                if boss.rect.y > self.rect.y:
                    self.vy += self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                if boss.rect.x < self.rect.x:
                    self.vx -= self.speed / 3 * self.speed_mult
                    if self.particles:
                        if randint(1, 2) == 1:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                        else:
                            main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
            
            elif isinstance(self.target_type, (tuple, list)):
                try:
                    if self.target_type[1] < self.rect.y:
                        self.vy -= self.speed / 3 * self.speed_mult
                        if self.particles:
                            if randint(1, 2) == 1:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                            else:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                    if self.target_type[0] > self.rect.x:
                        self.vx += self.speed / 3 * self.speed_mult
                        if self.particles:
                            if randint(1, 2) == 1:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                            else:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                    if self.target_type[1] > self.rect.y:
                        self.vy += self.speed / 3 * self.speed_mult
                        if self.particles:
                            if randint(1, 2) == 1:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                            else:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                    if self.target_type[0] < self.rect.x:
                        self.vx -= self.speed / 3 * self.speed_mult
                        if self.particles:
                            if randint(1, 2) == 1:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                            else:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                except TypeError:
                    if player.rect.y < self.rect.y:
                        self.vy -= self.speed / 3 * self.speed_mult
                        if self.particles:
                            if randint(1, 2) == 1:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                            else:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 2, self.speed // 0.75))
                    if player.rect.x > self.rect.x:
                        self.vx += self.speed / 3 * self.speed_mult
                        if self.particles:
                            if randint(1, 2) == 1:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                            else:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 3, self.speed // 0.75))
                    if player.rect.y > self.rect.y:
                        self.vy += self.speed / 3 * self.speed_mult
                        if self.particles:
                            if randint(1, 2) == 1:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 1, self.speed // 0.75))
                            else:
                                main_group.add(Particle(self.rect.center, (4, 4), self.part_colour, 4, self.speed // 0.75))
                    if player.rect.x < self.rect.x:
                        self.vx -= self.speed / 3 * self.speed_mult
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

            if isinstance(self.target_type, (tuple, list)):
                try:
                    if self.rect.colliderect(pygame.Rect(self.target_type[0]-8, self.target_type[1]-8, 16, 16)):
                        self.kill()
                except TypeError:
                    pass
        
            for sprite in main_group:
                if isinstance(sprite, Projectile) and sprite.destructive and self.rect.colliderect(sprite.rect):
                    self.kill()
                    break
                if not isinstance(sprite, self.dont_hit):
                    try:
                        if isinstance(sprite, self.target_type) and self.rect.colliderect(sprite.rect):
                            if isinstance(sprite, Enemy):
                                sprite.take_damage(self.damage)
                                player.health += self.drain
                            else:
                                sprite.health -= self.damage
                                boss.health += self.drain
                            self.kill()
                            break
                    except TypeError:
                        if self.rect.colliderect(sprite.rect) and not isinstance(sprite, (Projectile, HomingProjectile, Particle, ParticleEmitter)):
                            if isinstance(sprite, Enemy):
                                sprite.take_damage(self.damage)
                                player.health += self.drain
                            elif isinstance(sprite, Player):
                                sprite.take_damage(self.damage, evasion_mod=-self.resist_evasion)
                                boss.health += self.drain
                            else:
                                sprite.health -= self.damage
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
        
            if not self.rect.colliderect(gamescreen_rect) and not self.seeking:
                self.kill()
        
        if self.delay > 0:
            self.delay -= 1
        
        def abort(self):
            self.kill()

class BouncingProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, size, damage, speed, direction, colour, target_type=Enemy, particles=[True, WHITE], bounces=1, seeking=False, delay=0, drain=0, destructive=False, evasion_resist=0): # Particles list is 'particles enabled' then 'particle colour'
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(self.image, colour, (size[0] // 2, size[1] // 2), size[0] // 2)
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
        self.destructive = destructive
        self.bounces = bounces
        self.evasion_resist = evasion_resist
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
                if isinstance(sprite, Projectile) and sprite.destructive and not self.destructive and self.rect.colliderect(sprite.rect):
                    self.kill()
                    break
                if isinstance(sprite, self.target_type) and self.rect.colliderect(sprite.rect):
                    if isinstance(sprite, Enemy):
                        sprite.take_damage(self.damage)
                        player.health += self.drain
                    else:
                        sprite.take_damage(self.damage, evasion_mod=-self.evasion_resist)
                        boss.health += self.drain
                    self.kill()
                    break
        
            if self.seeking:
                if self.attack_time < pygame.time.get_ticks() and not self.attacked:
                    self.destructive = True
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
        
            if not self.rect.colliderect(gamescreen_rect) and not self.seeking:
                random_dir = randint(1, 3)
                if random_dir == 1: self.direction = inverse_direction(self.direction)
                elif random_dir == 2: self.direction = adjacent_direction(inverse_direction(self.direction))[0]
                elif random_dir == 3: self.direction = adjacent_direction(inverse_direction(self.direction))[1]
                self.bounces -= 1
                if self.bounces < 0:
                    self.kill()
                if self.rect.x <= gamescreen_rect.left: self.rect.x = gamescreen_rect.left + 16
                if self.rect.x >= gamescreen_rect.right - self.rect.width: self.rect.x = gamescreen_rect.right - 16
                if self.rect.y <= gamescreen_rect.top: self.rect.y = gamescreen_rect.top + 16
                if self.rect.y >= gamescreen_rect.bottom - self.rect.height: self.rect.y = gamescreen_rect.bottom - 16

        if self.delay > 0:
            self.delay -= 1
        
    def abort(self):
        self.kill()

# Visual Classes
class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, size, colour, quadrant, speed, strict_move=False):
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(self.image, colour, (size[0] // 2, size[1] // 2), size[0] // 2)
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
        
        if not self.rect.colliderect(gamescreen_rect):
            self.kill()
        
        if random() < 0.1:
            self.kill()
    
    def abort(self):
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
    
    def abort(self):
        self.kill()

# Groups
player = Player((16, 464))
boss_list = [
    Mage((280, 240)), Bomber((280, 240)), Warper((280, 240)), Cleric((280, 240)), Defender((280, 264)), 
    Twister((280, 240)), Summoner((280, 240)), Artificer((280, 240)), Sorcerer((280, 240)), Vampire((280, 240)), 
    Ranger((280, 240)), Shadow((280, 240)), Magnet((280, 240)), Decayed((280, 240)), Zombie((280, 240)),
    Illusionist((280, 240)), Jester((280, 240)), Ship((520, 240))
    ]

def reset_bosses():
    global boss_list
    boss_list = [
    Mage((280, 240)), Bomber((280, 240)), Warper((280, 240)), Cleric((280, 240)), Defender((280, 264)), 
    Twister((280, 240)), Summoner((280, 240)), Artificer((280, 240)), Sorcerer((280, 240)), Vampire((280, 240)), 
    Ranger((280, 240)), Shadow((280, 240)), Magnet((280, 240)), Decayed((280, 240)), Zombie((280, 240)),
    Illusionist((280, 240)), Jester((280, 240)), Ship((520, 240))
    ]

boss = None
main_group = pygame.sprite.Group()
main_group.add(player)
selected = False

upgrades = [
    {"name": "Health Boost", "cost": "0025", "level": 0, "max_level": 10, "effect": lambda: setattr(player, "max_health", player.max_health + 5)},
    {"name": "Rocketing Shots", "cost": "0020", "level": 0, "max_level": 10, "effect": lambda: setattr(player, "shot_speed", player.shot_speed + 2)},
    {"name": "Stronger Shots", "cost": "0080", "level": 0, "max_level": 3, "effect": lambda: setattr(player, "shot_damage", player.shot_damage + 1)},
    {"name": "Quicker Shots", "cost": "0030", "level": 0, "max_level": 5, "effect": lambda: setattr(player, "shot_cool", player.shot_cool - 100)},
    {"name": "Evasion", "cost": "0035", "level": 0, "max_level": 10, "effect": lambda: setattr(player, "evasion", player.evasion + 0.05)},
    {"name": "Swiftness", "cost": "0025", "level": 0, "max_level": 4, "effect": lambda: setattr(player, "speed", player.speed + 1)}
]

for u in save_data["upgrades"]:
    for i in range(len(upgrades)):
        if upgrades[i]["name"] == u:
            upgrades[i]["level"] = save_data["upgrades"][u]

visible_upgrades = [0, 1, 2, 3, 4]

for u in upgrades:
    for l in range(u["level"]):
        u["effect"]()

# Mainloop
reset = False
running = True
while running:
    if game_state == "Menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = "Fight"
                if event.key == pygame.K_r:
                    random_bosses = not random_bosses
                if event.key == pygame.K_m:
                    game_state = "Upgrades"
                if event.key == pygame.K_ESCAPE:
                    answer = messagebox.askyesno("Reset Save", "Are you sure you want to reset your save? \n\n This action cannot be undone. \n This action will close the game.")
                    if answer:
                        reset = True
                        running = False

        
        screen.fill(BG)

        screen.blit(title_font.render("The Dungeon Lurks", True, WHITE), (0, 0))
        screen.blit(subtitle_font.render(f"v{game_version}: {update_name}", True, WHITE), (0, 48))
        screen.blit(subtitle_font.render("Press SPACE to Begin!", True, WHITE), (88, 256))
        screen.blit(note_font.render(f"Randomised Bosses: {random_bosses} | Press R to Toggle.", True, WHITE), (0, 96))
        screen.blit(note_font.render("Press M to open Upgrades!", True, WHITE), (0, 120))

        pygame.display.flip()
        clock.tick(FPS)
    
    if game_state == "Fight":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if redness < max(0, 128 - int(255/player.max_health * player.health)) // 4: redness = max(0, 128 - int(255/player.max_health * player.health)) // 3
        if redness > max(0, 128 - int(255/player.max_health * player.health)) // 4: redness -= 1
        if redness < 0: redness = 0
        if redness > 255: redness = 255
        
        if boss == None or boss.health <= 0:
            player.health = min(int(player.health * 1.2), player.max_health)
            player.ult_used = False
            try:
                boss.update()
            except AttributeError:
                pass
            for x in main_group:
                x.abort()
            try:
                if random_bosses: boss = boss_list.pop(randint(0, len(boss_list) -1))
                else: boss = boss_list.pop(0)
                boss.add(main_group)
                boss.shot_time = pygame.time.get_ticks() + 500
                boss.super_time = pygame.time.get_ticks() + 500
                if hasattr(boss, "spec_time"): boss.spec_time = pygame.time.get_ticks() + 500
                if hasattr(boss, "burst_time"): boss.burst_time = pygame.time.get_ticks() + 500
                if hasattr(boss, "ability_time"): boss.ability_time = pygame.time.get_ticks() + 500
                if hasattr(boss, "tp_time"): boss.tp_time = pygame.time.get_ticks() + 500
            except IndexError:
                player.kill()
            
        screen.fill(BG)
        
        main_group.update()
        main_group.draw(screen)

        ui_rect = pygame.Surface((screen.get_width(), 48))
        ui_rect.fill(UI)
        screen.blit(ui_rect, (0, 0))

        ui_line = pygame.Surface((screen.get_width(), 4))
        ui_line.fill(L_UI)
        screen.blit(ui_line, (0, 44))
    
        screen.blit(font.render(f"HP: {player.health}/{player.max_health}", True, WHITE), (0, 0))
        screen.blit(font.render(f"Money: {money}", True, WHITE), (0, 16))
    
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
        
        damage_rect = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        damage_rect.fill((255, 0, 0, redness))
        screen.blit(damage_rect, (0, 0))

        if player not in main_group:
            game_state = "Menu"
            player.health = player.max_health
            for i in main_group:
                i.abort()
            main_group.add(player)
            boss = None
            reset_bosses()
            player.rect.center = (16, 464)
    
        pygame.display.flip()
        clock.tick(FPS)

    if game_state == "Upgrades":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "Menu"
                if event.key == pygame.K_UP:
                    for x in range(len(visible_upgrades)):
                        visible_upgrades[x] += 1
                        if visible_upgrades[x] >= len(upgrades):
                            visible_upgrades[x] = 0
                        if visible_upgrades[x] < 0:
                            visible_upgrades[x] = len(upgrades) - 1
                if event.key == pygame.K_DOWN:
                    for x in range(len(visible_upgrades)):
                        visible_upgrades[x] -= 1
                        if visible_upgrades[x] >= len(upgrades):
                            visible_upgrades[x] = 0
                        if visible_upgrades[x] < 0:
                            visible_upgrades[x] = len(upgrades) - 1
                if event.key == pygame.K_1:
                    if money >= int(upgrades[visible_upgrades[0]]["cost"]) * (1.5 ** upgrades[visible_upgrades[0]]["level"]) and upgrades[visible_upgrades[0]]["level"] < upgrades[visible_upgrades[0]]["max_level"]:
                        money -= int(int(upgrades[visible_upgrades[0]]["cost"]) * (1.5 ** upgrades[visible_upgrades[0]]["level"]))
                        upgrades[visible_upgrades[0]]["level"] += 1
                        money_display = recalc_money()
                        upgrades[visible_upgrades[0]]["effect"]()
                if event.key == pygame.K_2:
                    if money >= int(upgrades[visible_upgrades[1]]["cost"]) * (1.5 ** upgrades[visible_upgrades[1]]["level"]) and upgrades[visible_upgrades[1]]["level"] < upgrades[visible_upgrades[1]]["max_level"]:
                        money -= int(int(upgrades[visible_upgrades[1]]["cost"]) * (1.5 ** upgrades[visible_upgrades[1]]["level"]))
                        upgrades[visible_upgrades[1]]["level"] += 1
                        money_display = recalc_money()
                        upgrades[visible_upgrades[1]]["effect"]()
        
        screen.fill(BG)
    
        screen.blit(title_font.render("Upgrades", True, WHITE), (0, 0))
        screen.blit(subtitle_font.render(f"v{game_version}: {update_name}", True, WHITE), (0, 48))
        screen.blit(note_font.render("Press ESC to return to Menu!", True, WHITE), (0, 88))
        screen.blit(note_font.render(f"Money: {money_display}", True, WHITE), (0, 112))
        cost_statement = ""

        y = 144
        num = 1
        for u in visible_upgrades:
            cost = "000" + str(int(int(upgrades[u]["cost"]) * (1.5 ** upgrades[u]["level"])))
            cost_statement = ""
            if int(list(cost)[-1]) > 0: cost_statement += f"{int(list(cost)[-1])} CP "
            if int(list(cost)[-2]) > 0: cost_statement += f"{int(list(cost)[-2])} SP "
            if int(list(cost)[-3]) > 0: cost_statement += f"{int(list(cost)[-3])} GP "
            if int(list(cost)[-4]) > 0: cost_statement += f"{int(list(cost)[-4])} PP "
            screen.blit(note_font.render(f"{upgrades[u]["name"]} | Lv. {upgrades[u]["level"]}/{upgrades[u]["max_level"]} | {cost_statement}", True, WHITE), (24, y))
            screen.blit(note_font.render(f"Press {num} to Buy.", True, WHITE), (24, y + 24))
            y += 64
            num += 1
    
        pygame.display.flip()
        clock.tick(FPS)

save_data["copper"] = money % 10
save_data["silver"] = (money % 100) // 10
save_data["gold"] = (money % 1000) // 100
save_data["platinum"] = money // 1000

for u in upgrades:
    for i in save_data["upgrades"]:
        if i == u["name"]:
            save_data["upgrades"][u["name"]] = u["level"]

if reset:
    save_data = {"copper": 0, "silver": 0, "gold": 0, "platinum": 0, "upgrades": {"Health Boost": 0, "Rocketing Shots": 0, "Stronger Shots": 0, "Quicker Shots": 0, "Evasion": 0, "Swiftness": 0}}

with open("save.json", "w") as f:
    json.dump(save_data, f, indent=4)

pygame.time.delay(500)
pygame.quit()