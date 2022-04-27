import pygame
import os
import time
import random
pygame.font.init()
pygame.init()

WIDTH, HEIGHT= 1200, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# inamici
Inamic = pygame.image.load(os.path.join("D:\codes\pygame","inamic.jpg"))
# player
Racheta = pygame.image.load(os.path.join("D:\codes\pygame", "naveta.jpg"))
#laser
LaserBun = pygame.image.load(os.path.join("D:\codes\pygame", "laser.png"))
LaserRau = pygame.image.load(os.path.join("D:\codes\pygame", "LaserRau.png"))

#background
Fundal= pygame.transform.scale(pygame.image.load(os.path.join("D:\codes\pygame", "black.jpg")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.player_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel ,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                if laser.collision(obj):
                    obj.health -= 10
                    self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        else:
            self.cool_down_counter += 1
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 66, self.y + 36 , self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.player_img = Racheta
        self.laser_img = LaserBun
        self.mask = pygame.mask.from_surface(self.player_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y+self.player_img.get_height() + 10, self.player_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y+self.player_img.get_height() + 10, self.player_img.get_width() * ((self.health) / self.max_health), 10))

class Enemy(Ship):
    def __init__(self, x, y , health = 100):
        super().__init__(x, y, health)
        self.player_img = Inamic
        self.laser_img = LaserRau
        self.mask= pygame.mask.from_surface(self.player_img)

    def move(self, vel):
        self.y += vel

def collide(x1, x2):
     offset_x = x2.x - x1.x
     offset_y = x2.y - x1.y
     return x1.mask.overlap(x2.mask,(offset_x, offset_y)) != None

def main():
    run = True
    FPS = 61
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1


    player_vel = 6
    laser_vel = -4

    player = Player(576, 650)

    clock= pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(Fundal, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("AI PIERDUT!", 1, (255, 255, 255))
            time.sleep(5)
            WIN.blit(lost_label, (435, 265))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        if lives <= 0 or player.health <=0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > 3 * FPS:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(100, WIDTH - 100), random.randrange(-1500, - 100))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + 50 < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + 130 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(-laser_vel, player)

            if random.randrange(0, 3)==1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            else:
                if enemy.y > HEIGHT:
                 lives -= 1
                 enemies.remove(enemy)

        player.move_lasers(laser_vel,enemies)

        redraw_window()

main()
