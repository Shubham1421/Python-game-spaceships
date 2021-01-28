import pygame
from pygame.locals import *
import random


pygame.init()

# game settings
width, height = 1280, 700                       # Default 1280 700
screen = pygame.display.set_mode((width, height))
fps = 32
clock = pygame.time.Clock()
offsetx = pygame.display.get_surface().get_width()/10
offsety = pygame.display.get_surface().get_height()/10
restart = False
GAME_OVER = False

enemy_vel_max = 25
back_speed = 8
blast_time = 6
delaycount = 0                              # Keep it zero
delay = 70                                 # delay to blit game over

# load elements
back_image = pygame.image.load("data/background.jpg").convert_alpha()
player = pygame.image.load("data/spaceship.png").convert_alpha()
bullet_image = pygame.image.load("data/bullet1.png").convert_alpha()
enemy_spaceship_img = pygame.image.load("data/enemy_spaceship_img.png").convert_alpha()
blast_image = pygame.image.load("data/explosion.png")
score_img = [pygame.image.load("data/score/zero.png"),
             pygame.image.load("data/score/one.png"),
             pygame.image.load("data/score/two.png"),
             pygame.image.load("data/score/three.png"),
             pygame.image.load("data/score/four.png"),
             pygame.image.load("data/score/five.png"),
             pygame.image.load("data/score/six.png"),
             pygame.image.load("data/score/seven.png"),
             pygame.image.load("data/score/eight.png"),
             pygame.image.load("data/score/nine.png"),
             pygame.image.load("data/score/score.png"), ]
gameoverimg = pygame.image.load("data/gameover.png")
welcomeimg = pygame.image.load("data/final_welcome.png")


# Player settngs
playerpos = [(width - player.get_width())/2, height - player.get_height() - offsety]
playervel = 20
bullet_velocity = 13
player_blast_speed = 20
player_score = 0
enemy_width = enemy_spaceship_img.get_width()


# event track
keys = [False, False, False, False]     # Monitor W A S D keys
bullets = []                            # Track active bullets
enemy_bullets = []
enemies = []
back_image_pos1 = [0, 0]
back_image_pos2 = [0, -back_image.get_height()]
blasts = []

#Load and Play sounds
'''
sound = pygame.mixer.Sound("sounds/sound.wav")
sound.play()
'''
back_sound = pygame.mixer.Sound("sounds/rocket_thrust.wav")
fire_sound = pygame.mixer.Sound("sounds/fire.wav")
enemy_explosion = pygame.mixer.Sound("sounds/enemy_explosion.wav")
player_explosion = pygame.mixer.Sound("sounds/player_explosion.wav")
gameoversound = pygame.mixer.Sound("sounds/gameover.wav")
welcome_sound = pygame.mixer.Sound("sounds/welcome.wav")


pygame.mixer.init()


class Enemy:
    max_boundary_x = pygame.display.get_surface().get_width() - enemy_spaceship_img.get_width()
    health = 1
    enemyvelx = random.randrange(0, 2*enemy_vel_max, 3) - enemy_vel_max
    enemyvely = random.randrange(25, 100, 25)/10
    enemypos = []


class blast:
    pos = []
    value = 0


def welcome():
    welcome_sound.play(-1)
    while True:
        exit_status = 0
        screen.blit(welcomeimg, [0, 0])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # Exit event
                pygame.quit()
                exit(0)

            elif event.type == pygame.KEYDOWN:      # Track key values
                if event.key == K_KP_ENTER or event.key == K_RETURN:
                    exit_status = 1

        if exit_status:
            break
        pygame.display.update()
        clock.tick(fps)
    welcome_sound.fadeout(500)


def blit_everything():
    screen.blit(back_image, back_image_pos1)
    screen.blit(back_image, back_image_pos2)
    screen.blit(player, playerpos)
    for bullet in bullets:
        screen.blit(bullet_image, bullet)
    for enemy in enemies:
        screen.blit(enemy_spaceship_img, enemy.enemypos)
    for enemy_bullet in enemy_bullets:
        screen.blit(bullet_image, enemy_bullet)
    for blast in blasts:                                    # blasts
        if blast.value >= blast_time:                              # keep blasts on screen for a time
            blasts.remove(blast)
        else:
            if blast.value < blast_time / 3:                # to show animation of blasts
                screen.blit(blast_image, [blast.pos[0] + 60, blast.pos[1]])
                screen.blit(blast_image, [blast.pos[0] + 80, blast.pos[1]])
                screen.blit(blast_image, [blast.pos[0] + 100, blast.pos[1]])
            elif blast_time/3 < blast.value < blast_time/2:
                screen.blit(blast_image, [blast.pos[0]+60, blast.pos[1]])
                screen.blit(blast_image, [blast.pos[0]+100, blast.pos[1]])
                screen.blit(blast_image, [blast.pos[0]+120, blast.pos[1]])
            elif blast_time/2 < blast.value < blast_time:
                screen.blit(blast_image, [blast.pos[0]+80, blast.pos[1]])
                screen.blit(blast_image, [blast.pos[0]+110, blast.pos[1]])
                screen.blit(blast_image, [blast.pos[0]+130, blast.pos[1]])
            blast.pos[1] += back_speed  # blasts move with background to appear stationary
            blast.value += 1
    score()                 # Score
    pygame.display.update()


def back_move():
    back_image_pos1[1] += back_speed
    back_image_pos2[1] += back_speed
    if back_image_pos1[1] > back_image.get_height():
        back_image_pos1[1] = -back_image.get_height()
    if back_image_pos2[1] > back_image.get_height():
        back_image_pos2[1] = -back_image.get_height()


def move():
    if keys[0]:
        playerpos[1] -= playervel
    elif keys[2]:
        playerpos[1] += playervel
    if keys[1]:
        playerpos[0] -= playervel
    elif keys[3]:
        playerpos[0] += playervel
    # boundary conditions
    if playerpos[0] < 0:
        playerpos[0] = 0
    elif playerpos[0] > (pygame.display.get_surface().get_width() - player.get_width()):
        playerpos[0] = pygame.display.get_surface().get_width() - player.get_width()
    if playerpos[1] < 0:
        playerpos[1] = 0
    elif playerpos[1] > pygame.display.get_surface().get_height() - player.get_height():
        playerpos[1] = pygame.display.get_surface().get_height() - player.get_height()


def enemy_move():
    max_boundary_x = pygame.display.get_surface().get_width() - enemy_spaceship_img.get_width()
    for enemy in enemies:
        if enemy.enemypos[0] < 0:
            enemy.enemyvelx = random.randint(0, enemy_vel_max)
        elif enemy.enemypos[0] > max_boundary_x:
            enemy.enemyvelx = -random.randint(0, enemy_vel_max)
        # else:
        #    enemy.vel = random.randint(0, 2*enemy_vel_max) - enemy_vel_max
        enemy.enemypos[0] += enemy.enemyvelx
        enemy.enemypos[1] += enemy.enemyvely                                    # move enemy down
        if enemy.enemypos[1] > pygame.display.get_surface().get_height():
            enemies.remove(enemy)
            spawn_enemy()
        if enemy.enemypos[1] == 50 or enemy.enemypos[1] == 300:
            fire_bullet_enemy(enemy.enemypos)


def checkevent():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:           # Exit event
            pygame.quit()
            exit(0)

        elif event.type == pygame.KEYDOWN:      # Track key values
            if event.key == K_w:
                keys[0] = True
            elif event.key == K_a:
                keys[1] = True
            elif event.key == K_s:
                keys[2] = True
            elif event.key == K_d:
                keys[3] = True
            elif event.key == K_SPACE:
                fire_bullet("player")
            if event.key == pygame.K_p:
                global restart
                restart = True
                pause = True
                #paused()

        elif event.type == pygame.KEYUP:        # Keep plane within the boundaries
            if event.key == pygame.K_w:
                keys[0] = False
            elif event.key == pygame.K_a:
                keys[1] = False
            elif event.key == pygame.K_s:
                keys[2] = False
            elif event.key == pygame.K_d:
                keys[3] = False


def spawn_enemy():
    newenemy = Enemy()
    spawn_loc_x = random.randint(0, pygame.display.get_surface().get_width() - enemy_spaceship_img.get_width())# max area available to spawn
    tempx = random.randrange(1, spawn_loc_x, enemy_width/2)             # to reduce overlapping enemies
    tempy = -random.randrange(50, 500, 60)                                                  # y axis to spawn
    newenemy.enemyvely = random.randrange(25, 100, 25) / 10
    newenemy.enemypos = [tempx, tempy]                                                      # assign values
    enemies.append(newenemy)                                                                # add enemy to list


def fire_bullet(data):
    if data == "player":
        fire_sound.play()
        a = playerpos.copy()
        bullets.append(a)
        bullets[(len(bullets)-1)][0] += player.get_width()/2


def fire_bullet_enemy(b):
    a = b.copy()
    enemy_bullets.append(a)                                                     # b is position of enemy firing bullet


def bullet_move():
    for bullet in bullets:
        bullet[1] -= bullet_velocity
        if bullet[1] < 0:
            bullets.remove(bullet)
    for enemy_bullet in enemy_bullets:
        enemy_bullet[1] += bullet_velocity
        if enemy_bullet[1] > pygame.display.get_surface().get_height():
            enemy_bullets.remove(enemy_bullet)


def bullet_hit():
    for enemy_bullet in enemy_bullets:                                              # player is hit
        if playerpos[0] <= enemy_bullet[0] <= playerpos[0] + player.get_width():
            if playerpos[1] <= enemy_bullet[1] <= playerpos[1] + player.get_height() - 20:
                player_explosion.play()
                print("GAME OVER")
                global GAME_OVER
                GAME_OVER = True

    for enemy in enemies:                                                           # enemy is hit
        for bullet in bullets:
            if enemy.enemypos[0] < bullet[0] < enemy.enemypos[0] + enemy_spaceship_img.get_width():
                if enemy.enemypos[1] < bullet[1] < enemy.enemypos[1] + enemy_spaceship_img.get_height():
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    enemy_explosion.play()
                    create_blast(enemy.enemypos)
                    global player_score
                    player_score += 1
    print("Bullet_hit complete")


def create_blast(pos):
    newblast = blast()
    newblast.pos = pos.copy()
    newblast.value = 0
    blasts.append(newblast)


def level(number):
    if number == 1:
        if len(enemies) < 3:
            spawn_enemy()


def score():
    screen.blit(score_img[10], [width - 200, 10])
    score_blit = []
    positionx = width - 70
    if player_score/10 != 0:
        temp_score = player_score
        while temp_score != 0:
            temp_digit = temp_score % 10
            score_blit.append(temp_digit)
            temp_score = temp_score // 10
    for i in reversed(score_blit):
        screen.blit(score_img[i], [positionx, 14])
        positionx += 20


def gameover():
    player_blast_value = 0
    delaycount = 0
    while True:
        blit_everything()
        if delaycount > delay:
            gameoversound.play(fade_ms=750)
            while True:
                screen.blit(gameoverimg, [60, 5])
                checkevent()
                if checkrestart():
                    break
                pygame.display.update()
        delaycount += 1

        if player_blast_value == player_blast_speed:  # player blast animation
            player_blast_value = 0
        elif player_blast_value < player_blast_speed / 2:
            screen.blit(blast_image, [playerpos[0] + 20, playerpos[1]])
            screen.blit(blast_image, [playerpos[0] + 60, playerpos[1]])
            screen.blit(blast_image, [playerpos[0] + 20, playerpos[1] + 40])
            screen.blit(blast_image, [playerpos[0] + 60, playerpos[1] + 40])
        elif player_blast_value > player_blast_speed / 2:
            screen.blit(blast_image, [playerpos[0] + 40, playerpos[1]])
            screen.blit(blast_image, [playerpos[0] + 40, playerpos[1] + 30])
        player_blast_value += 1
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit event
                pygame.quit()
                exit(0)

        global restart
        if restart:
            break
        clock.tick(fps)


def paused():
    largeText = pygame.font.SysFont("comicsansms", 115)
    TextSurf, TextRect = text_objects("Paused", largeText)
    TextRect.center = ((display_width / 2), (display_height / 2))
    gameDisplay.blit(TextSurf, TextRect)

    while pause:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # gameDisplay.fill(white)

        button("Continue", 150, 450, 100, 50, green, bright_green, unpause)
        button("Quit", 550, 450, 100, 50, red, bright_red, quitgame)

        pygame.display.update()
        clock.tick(15)


def checkrestart():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:  # Track key values
            if event.key == K_RETURN:
                global restart
                restart = True
                return True


while True:
    welcome()
    back_sound.play(-1)
    while True:
        checkevent()
        move()
        bullet_move()
        enemy_move()
        back_move()
        bullet_hit()
        level(1)
        blit_everything()
        if GAME_OVER:
            gameover()
        if restart:
            break
        clock.tick(fps)

    print("exit")









