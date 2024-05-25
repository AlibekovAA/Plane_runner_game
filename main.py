import random
import pygame
import pygame.freetype
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLANE_START_POS, PLANE_SPEEDS, GROUND_START_POSITIONS, GROUND_SPEEDS, GROUND_INTERVALS, NEW_TOWERS_INTERVALS, NEW_ENEMY_PLANE_INTERVALS, FONT_SIZE, FPS, WHITE, BLACK

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('music_bac.mp3')
collision_sound = pygame.mixer.Sound('bombs.mp3')

pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('11 September Game')
clock = pygame.time.Clock()
font = pygame.freetype.Font(None, FONT_SIZE)

towers_image = pygame.image.load('images/towers.png')
towers_image = pygame.transform.scale(towers_image, (250, 200))
plane_image = pygame.image.load('images/plane.png')
plane_image = pygame.transform.scale(plane_image, (150, 100))
ground_image = pygame.image.load('images/ground.png')
ground_image = pygame.transform.scale(ground_image, (800, 142))
enemy_plane_image = pygame.image.load('images/plane_2.png')
enemy_plane_image = pygame.transform.scale(enemy_plane_image, (150, 100))

GROUND_EVENT = pygame.USEREVENT
TOWERS_EVENT = pygame.USEREVENT + 1
ENEMY_PLANE_EVENT = pygame.USEREVENT + 2

pygame.time.set_timer(GROUND_EVENT, GROUND_INTERVALS[0])
pygame.time.set_timer(TOWERS_EVENT, random.randint(*NEW_TOWERS_INTERVALS[0]))
pygame.time.set_timer(
    ENEMY_PLANE_EVENT, random.randint(*NEW_ENEMY_PLANE_INTERVALS[0]))

ground_group = pygame.sprite.Group()
towers_group = pygame.sprite.Group()
enemy_plane_group = pygame.sprite.Group()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'images/exp{num}.png')
            img = pygame.transform.scale(img, (100, 100))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 4

        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


class Ground(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= GROUND_SPEED
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH


class Towers(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= GROUND_SPEED
        if self.rect.right < 0:
            self.kill()
            plane.score += 1


class EnemyPlane(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= GROUND_SPEED * 2
        if self.rect.right < 0:
            self.kill()
            plane.score += 1


class Plane(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.mask = pygame.mask.from_surface(self.image)
        self.score = 0
        self.game_status = 'Game'
        self.speed = PLANE_SPEED
        self.moving_up = False
        self.moving_down = False

    def update_position(self):
        if self.moving_up:
            self.rect.y -= self.speed
        if self.moving_down:
            self.rect.y += self.speed

        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT - ground_image.get_height():
            self.rect.bottom = SCREEN_HEIGHT - ground_image.get_height()
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self):
        screen.blit(self.image, self.rect)


def add_ground():
    for position in GROUND_START_POSITIONS:
        g = Ground(ground_image, position)
        ground_group.add(g)


def add_tower():
    t = Towers(towers_image, (SCREEN_WIDTH + 10, 400))
    towers_group.add(t)


def add_enemy_plane():
    y_position = random.randint(50, 250)
    e = EnemyPlane(enemy_plane_image, (SCREEN_WIDTH + 10, y_position))
    enemy_plane_group.add(e)


def reset_game():
    global plane, ground_group, towers_group, enemy_plane_group, paused
    plane = Plane(plane_image, PLANE_START_POS)
    ground_group.empty()
    towers_group.empty()
    enemy_plane_group.empty()
    add_ground()
    pygame.mixer.music.play(-1)
    paused = False


def select_difficulty():
    global running
    screen.fill(WHITE)
    font.render_to(screen, (100, 100), "Select Difficulty:", BLACK)
    font.render_to(screen, (110, 150), "1 - Easy", BLACK)
    font.render_to(screen, (110, 190), "2 - Medium", BLACK)
    font.render_to(screen, (110, 230), "3 - Hard", BLACK)
    font.render_to(screen, (100, 280), "Press Q to Quit", BLACK)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    change_difficulty(EASY)
                    running = True
                    return
                elif event.key == pygame.K_2:
                    change_difficulty(MEDIUM)
                    running = True
                    return
                elif event.key == pygame.K_3:
                    change_difficulty(HARD)
                    running = True
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()


def change_difficulty(difficulty):
    global GROUND_SPEED, GROUND_INTERVAL, NEW_TOWERS_INTERVAL, NEW_ENEMY_PLANE_INTERVAL, PLANE_SPEED
    if difficulty == EASY:
        PLANE_SPEED = PLANE_SPEEDS[0]
        GROUND_SPEED = GROUND_SPEEDS[0]
        GROUND_INTERVAL = GROUND_INTERVALS[0]
        NEW_TOWERS_INTERVAL = NEW_TOWERS_INTERVALS[0]
        NEW_ENEMY_PLANE_INTERVAL = NEW_ENEMY_PLANE_INTERVALS[0]
    elif difficulty == MEDIUM:
        PLANE_SPEED = PLANE_SPEEDS[1]
        GROUND_SPEED = GROUND_SPEEDS[1]
        GROUND_INTERVAL = GROUND_INTERVALS[1]
        NEW_TOWERS_INTERVAL = NEW_TOWERS_INTERVALS[1]
        NEW_ENEMY_PLANE_INTERVAL = NEW_ENEMY_PLANE_INTERVALS[1]
    elif difficulty == HARD:
        PLANE_SPEED = PLANE_SPEEDS[2]
        GROUND_SPEED = GROUND_SPEEDS[2]
        GROUND_INTERVAL = GROUND_INTERVALS[2]
        NEW_TOWERS_INTERVAL = NEW_TOWERS_INTERVALS[2]
        NEW_ENEMY_PLANE_INTERVAL = NEW_ENEMY_PLANE_INTERVALS[2]


EASY = 1
MEDIUM = 2
HARD = 3

select_difficulty()

plane = Plane(plane_image, PLANE_START_POS)
add_ground()
running = True
paused = False
explosion_group = pygame.sprite.Group()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if plane.game_status == 'Game' and not paused:
                if event.key == pygame.K_w:
                    plane.moving_up = True
                if event.key == pygame.K_s:
                    plane.moving_down = True
            if plane.game_status == 'Menu':
                if event.key == pygame.K_r:
                    select_difficulty()
                    reset_game()
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                plane.moving_up = False
            if event.key == pygame.K_s:
                plane.moving_down = False
        if not paused:
            if event.type == GROUND_EVENT:
                add_ground()
            if event.type == TOWERS_EVENT:
                pygame.time.set_timer(
                    TOWERS_EVENT, random.randint(*NEW_TOWERS_INTERVAL))
                add_tower()
            if event.type == ENEMY_PLANE_EVENT:
                pygame.time.set_timer(
                    ENEMY_PLANE_EVENT, random.randint(*NEW_ENEMY_PLANE_INTERVAL))
                add_enemy_plane()

    screen.fill(WHITE)
    if not paused:
        if plane.game_status == 'Game':
            ground_group.update()
            ground_group.draw(screen)
            towers_group.update()
            towers_group.draw(screen)
            enemy_plane_group.update()
            enemy_plane_group.draw(screen)
            plane.update_position()
            plane.draw()
            font.render_to(screen, (850, 50), str(plane.score), BLACK)
            if pygame.sprite.spritecollide(plane, towers_group, False, pygame.sprite.collide_mask):
                explosion = Explosion(plane.rect.centerx, plane.rect.centery)
                explosion_group.add(explosion)
                plane.game_status = 'Menu'
                collision_sound.play()
                pygame.mixer.music.stop()

            for enemy_plane in enemy_plane_group:
                if pygame.sprite.spritecollide(plane, enemy_plane_group, False, pygame.sprite.collide_mask):
                    explosion = Explosion(
                        plane.rect.centerx, plane.rect.centery)
                    explosion_group.add(explosion)
                    plane.game_status = 'Menu'
                    collision_sound.play()
                    pygame.mixer.music.stop()
                    break

        else:
            game_over_text, rect = font.render('Game over', BLACK)
            screen.blit(game_over_text, ((SCREEN_WIDTH - rect.width) //
                        2, (SCREEN_HEIGHT - rect.height) // 3))
            restart_text, rect = font.render('Press R to Restart', BLACK)
            screen.blit(restart_text, ((SCREEN_WIDTH - rect.width) //
                        2, (SCREEN_HEIGHT - rect.height) // 3 + 50))
            exit_text, rect = font.render('Press Q to exit', BLACK)
            screen.blit(exit_text, ((SCREEN_WIDTH - rect.width) //
                        2, (SCREEN_HEIGHT - rect.height) // 3 + 100))
    else:
        paused_text, rect = font.render('Paused', BLACK)
        screen.blit(paused_text, ((SCREEN_WIDTH - rect.width) //
                    2, (SCREEN_HEIGHT - rect.height) // 3))

    explosion_group.update()
    explosion_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
