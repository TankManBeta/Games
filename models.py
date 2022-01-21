# -*- coding: utf-8 -*-

"""
    @Author 坦克手贝塔
    @Date 2022/1/21 14:52
"""

import pygame
import time
import random

from pygame.sprite import Sprite

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
BG_COLOR = pygame.Color(0, 0, 0)
TEXT_COLOR = pygame.Color(255, 0, 0)


class BaseItem(Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class MainGame:
    window = None
    my_tank = None
    enemy_tank_count = 5
    enemy_tank_list = []
    my_bullet_list = []
    enemy_bullet_list = []
    explode_list = []
    wall_list = []

    def __init__(self):
        pass

    def start_game(self):
        pygame.display.init()
        MainGame.window = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.create_my_tank()
        self.create_enemy_tank()
        self.create_wall()
        pygame.display.set_caption("坦克大战")
        while True:
            time.sleep(0.02)
            MainGame.window.fill(BG_COLOR)
            self.get_event()
            MainGame.window.blit(self.get_text_surface(f"敌方坦克剩余数量{len(MainGame.enemy_tank_list)}"), (10, 10))
            if MainGame.my_tank and MainGame.my_tank.live:
                MainGame.my_tank.display_tank()
            else:
                del MainGame.my_tank
                MainGame.my_tank = None
            self.blit_enemy_tank()
            self.blit_my_bullet()
            self.blit_enemy_bullet()
            self.blit_explode()
            self.bilt_wall()
            if MainGame.my_tank and MainGame.my_tank.live:
                if not MainGame.my_tank.stop:
                    MainGame.my_tank.move()
                    MainGame.my_tank.hit_wall()
                    MainGame.my_tank.my_tank_hit_enemy_tank()
            pygame.display.update()

    def bilt_wall(self):
        for wall in MainGame.wall_list:
            if wall.live:
                wall.display_wall()
            else:
                MainGame.wall_list.remove(wall)

    def create_wall(self):
        for i in range(6):
            wall = Wall(i*130, 220)
            MainGame.wall_list.append(wall)

    def create_my_tank(self):
        MainGame.my_tank = MyTank(350, 300)
        music = Music("audio/start.wav")
        music.play_music()

    def create_enemy_tank(self):
        top = 100
        for i in range(self.enemy_tank_count):
            left = random.randint(0+130*i, 50+130*i)
            speed = random.randint(1, 4)
            enemy = EnemyTank(left, top, speed)
            MainGame.enemy_tank_list.append(enemy)

    def blit_enemy_tank(self):
        for enemy in MainGame.enemy_tank_list:
            if enemy.live:
                enemy.display_tank()
                enemy.random_move()
                enemy.hit_wall()
                if MainGame.my_tank and MainGame.my_tank.live:
                    enemy.enemy_tank_hit_my_tank()
                enemy.enemy_tank_hit_enemy_tank()
                enemy_bullet = enemy.shot()
                if enemy_bullet:
                    MainGame.enemy_bullet_list.append(enemy_bullet)
            else:
                MainGame.enemy_tank_list.remove(enemy)

    def blit_my_bullet(self):
        for my_bullet in MainGame.my_bullet_list:
            if my_bullet.live:
                my_bullet.display_bullet()
                my_bullet.move()
                my_bullet.my_bullet_hit_enemy_tank()
                my_bullet.hit_wall()
            else:
                MainGame.my_bullet_list.remove(my_bullet)

    def blit_enemy_bullet(self):
        for enemy_bullet in MainGame.enemy_bullet_list:
            if enemy_bullet.live:
                enemy_bullet.display_bullet()
                enemy_bullet.move()
                enemy_bullet.enemy_bullet_hit_my_tank()
                enemy_bullet.hit_wall()
            else:
                MainGame.enemy_bullet_list.remove(enemy_bullet)

    def blit_explode(self):
        for explode in MainGame.explode_list:
            if explode.live:
                explode.display_explode()
            else:
                MainGame.explode_list.remove(explode)

    def end_game(self):
        exit()

    def get_event(self):
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                self.end_game()
            if event.type == pygame.KEYDOWN:
                if not MainGame.my_tank:
                    if event.key == pygame.K_ESCAPE:
                        self.create_my_tank()
                if MainGame.my_tank and MainGame.my_tank.live:
                    if event.key == pygame.K_LEFT:
                        MainGame.my_tank.direction = "L"
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                    elif event.key == pygame.K_RIGHT:
                        MainGame.my_tank.direction = "R"
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                    elif event.key == pygame.K_UP:
                        MainGame.my_tank.direction = "U"
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                    elif event.key == pygame.K_DOWN:
                        MainGame.my_tank.direction = "D"
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                    elif event.key == pygame.K_SPACE:
                        if len(MainGame.my_bullet_list) < 3:
                            my_bullet = Bullet(MainGame.my_tank)
                            MainGame.my_bullet_list.append(my_bullet)
                            music = Music("audio/fire.wav")
                            music.play_music()
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    if MainGame.my_tank and MainGame.my_tank.live:
                        MainGame.my_tank.stop = True

    def get_text_surface(self, text):
        pygame.font.init()
        font = pygame.font.SysFont("kaiti", 18)
        text_surface = font.render(text, True, TEXT_COLOR)
        return text_surface


class Tank(BaseItem):
    def __init__(self, left, top):
        self.images = {
            'U': pygame.image.load("./img/p1tankU.gif"),
            'D': pygame.image.load("./img/p1tankD.gif"),
            'L': pygame.image.load("./img/p1tankL.gif"),
            'R': pygame.image.load("./img/p1tankR.gif")
        }
        self.direction = 'L'
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = 5
        self.stop = True
        self.live = True
        self.old_left = self.rect.left
        self.old_top = self.rect.top

    def move(self):
        self.old_left = self.rect.left
        self.old_top = self.rect.top
        if self.direction == "L":
            if self.rect.left - self.speed <= 0:
                self.rect.left = 0
            else:
                self.rect.left -= self.speed
        elif self.direction == "U":
            if self.rect.top - self.speed <= 0:
                self.rect.top = 0
            else:
                self.rect.top -= self.speed
        elif self.direction == "R":
            if self.rect.left + self.speed >= SCREEN_WIDTH-self.rect.width:
                self.rect.left = SCREEN_WIDTH-self.rect.width
            else:
                self.rect.left += self.speed
        elif self.direction == "D":
            if self.rect.top + self.speed >= SCREEN_HEIGHT-self.rect.height:
                self.rect.top = SCREEN_HEIGHT-self.rect.height
            else:
                self.rect.top += self.speed

    def shot(self):
        return Bullet(self)

    def stay(self):
        self.rect.left = self.old_left
        self.rect.top = self.old_top

    def hit_wall(self):
        for wall in MainGame.wall_list:
            if pygame.sprite.collide_rect(self, wall):
                self.stay()

    def display_tank(self):
        self.image = self.images[self.direction]
        MainGame.window.blit(self.image, self.rect)


class MyTank(Tank):
    def __init__(self, left, top):
        super(MyTank, self).__init__(left, top)

    def my_tank_hit_enemy_tank(self):
        for enemy in MainGame.enemy_tank_list:
            if pygame.sprite.collide_rect(self, enemy):
                self.stay()


class EnemyTank(Tank):
    def __init__(self, left, top, speed):
        super(EnemyTank, self).__init__(left, top)
        self.images = {
            'U': pygame.image.load("./img/enemy1U.gif"),
            'D': pygame.image.load("./img/enemy1D.gif"),
            'L': pygame.image.load("./img/enemy1L.gif"),
            'R': pygame.image.load("./img/enemy1R.gif")
        }
        self.direction = self.random_direction()
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = speed
        self.flag = True
        self.step = 60

    def enemy_tank_hit_my_tank(self):
        if pygame.sprite.collide_rect(self, MainGame.my_tank):
            self.stay()

    def enemy_tank_hit_enemy_tank(self):
        for enemy in MainGame.enemy_tank_list:
            if enemy != self:
                if pygame.sprite.collide_rect(self, enemy):
                    self.stay()

    def random_direction(self):
        directions = ['U', 'D', 'L', 'R']
        num = random.randint(0, 3)
        return directions[num]

    def random_move(self):
        if self.step <= 0:
            self.direction = self.random_direction()
            self.step = 60
        else:
            self.move()
            self.step -= 1

    def shot(self):
        num = random.randint(1, 500)
        if num < 10:
            return Bullet(self)


class Bullet(BaseItem):
    def __init__(self, tank):
        self.image = pygame.image.load("img/enemymissile.gif")
        self.direction = tank.direction
        self.rect = self.image.get_rect()
        if self.direction == 'U':
            self.rect.left = tank.rect.left + tank.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top - self.rect.height
        elif self.direction == 'D':
            self.rect.left = tank.rect.left + tank.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top + self.rect.height
        elif self.direction == 'L':
            self.rect.left = tank.rect.left - self.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top + tank.rect.width/2 - self.rect.width/2
        elif self.direction == 'R':
            self.rect.left = tank.rect.left + tank.rect.width
            self.rect.top = tank.rect.top + tank.rect.width/2 - self.rect.width/2
        self.speed = 5
        self.live = True

    def move(self):
        if self.direction == 'U':
            if self.rect.top > 0:
                self.rect.top -= self.speed
            else:
                self.live = False
        elif self.direction == 'R':
            if self.rect.left + self.rect.width < SCREEN_WIDTH:
                self.rect.left += self.speed
            else:
                self.live = False
        elif self.direction == 'D':
            if self.rect.top + self.rect.height < SCREEN_HEIGHT:
                self.rect.top += self.speed
            else:
                self.live = False
        elif self.direction == 'L':
            if self.rect.left > 0:
                self.rect.left -= self.speed
            else:
                self.live = False

    def hit_wall(self):
        for wall in MainGame.wall_list:
            if pygame.sprite.collide_rect(self, wall):
                self.live = False
                wall.hp -= 1
                if wall.hp <= 0:
                    wall.live = False

    def display_bullet(self):
        MainGame.window.blit(self.image, self.rect)

    def my_bullet_hit_enemy_tank(self):
        for enemy_tank in MainGame.enemy_tank_list:
            if pygame.sprite.collide_rect(enemy_tank, self):
                enemy_tank.live = False
                self.live = False
                explode = Explode(enemy_tank)
                MainGame.explode_list.append(explode)

    def enemy_bullet_hit_my_tank(self):
        if MainGame.my_tank and MainGame.my_tank.live:
            if pygame.sprite.collide_rect(MainGame.my_tank, self):

                explode = Explode(MainGame.my_tank)
                MainGame.explode_list.append(explode)
                self.live = False
                MainGame.my_tank.live = False


class Wall:
    def __init__(self, left, top):
        self.image = pygame.image.load("img/cement_wall.gif")
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.live = True
        self.hp = 3

    def display_wall(self):
        MainGame.window.blit(self.image, self.rect)


class Explode:
    def __init__(self, tank):
        self.rect = tank.rect
        self.images = [
            pygame.image.load("img/blast0.gif"),
            pygame.image.load("img/blast1.gif"),
            pygame.image.load("img/blast2.gif"),
            pygame.image.load("img/blast3.gif"),
            pygame.image.load("img/blast4.gif"),
            pygame.image.load("img/blast5.gif"),
            pygame.image.load("img/blast6.gif"),
            pygame.image.load("img/blast7.gif")
        ]
        self.step = 0
        self.image = self.images[self.step]
        self.live = True

    def display_explode(self):
        if self.step < len(self.images):
            self.image = self.images[self.step]
            self.step += 1
            MainGame.window.blit(self.image, self.rect)
        else:
            self.live = False
            self.step = 0


class Music:
    def __init__(self, filename):
        self.filename = filename
        pygame.mixer.init()
        pygame.mixer.music.load(self.filename)

    def play_music(self):
        pygame.mixer.music.play()


if __name__ == "__main__":
    MainGame().start_game()