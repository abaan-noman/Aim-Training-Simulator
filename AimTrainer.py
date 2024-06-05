import math
import random
import time
import pygame
import pygame_gui

pygame.init()

WIDTH, HEIGHT = 800, 600

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 400
TARGET_EVENT = pygame.USEREVENT
POWERUP_EVENT = pygame.USEREVENT + 1

TARGET_PADDING = 30

BG_COLOR = (0, 25, 40)
LIVES = 3
TOP_BAR_HEIGHT = 50

LABEL_FONT = pygame.font.SysFont("comicsans", 24)

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

login_layout = {
    'email_label': {'type': 'label', 'text': 'Email:', 'rect': pygame.Rect((300, 200), (200, 50))},
    'email_input': {'type': 'input', 'rect': pygame.Rect((300, 250), (200, 50))},
    'year_label': {'type': 'label', 'text': 'Year of Birth:', 'rect': pygame.Rect((300, 300), (200, 50))},
    'year_input': {'type': 'input', 'rect': pygame.Rect((300, 350), (200, 50))},
    'login_button': {'type': 'button', 'text': 'Login', 'rect': pygame.Rect((350, 450), (100, 50))}
}

class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR,
                           (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR,
                           (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        dis = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return dis <= self.size

class MovingTarget(Target):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x_speed = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        self.y_speed = random.choice([-1, 1]) * random.uniform(0.5, 1.5)

    def update(self):
        super().update()
        self.x += self.x_speed
        self.y += self.y_speed

        if self.x - self.size < 0 or self.x + self.size > WIDTH:
            self.x_speed *= -1
        if self.y - self.size < TOP_BAR_HEIGHT or self.y + self.size > HEIGHT:
            self.y_speed *= -1

class FastShrinkingTarget(Target):
    GROWTH_RATE = 0.4

class PowerUp:
    SIZE = 20
    COLOR = "blue"
    TYPES = ["extra_life", "slow_motion", "larger_targets"]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(self.TYPES)

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.SIZE)

    def collide(self, x, y):
        dis = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return dis <= self.SIZE

def draw(win, targets, powerups):
    win.fill(BG_COLOR)

    for target in targets:
        target.draw(win)

    for powerup in powerups:
        powerup.draw(win)

def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)

    return f"{minutes:02d}:{seconds:02d}.{milli}"

def draw_top_bar(win, elapsed_time, targets_pressed, misses, lives):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "black")

    # Ensure we don't divide by zero
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")

    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")

    lives_label = LABEL_FONT.render(f"Lives: {lives - misses}", 1, "black")

    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))

def end_screen(win, elapsed_time, targets_pressed, clicks):
    win.fill(BG_COLOR)
    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "white")

    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")

    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")

    accuracy = round(targets_pressed / clicks * 100, 1) if clicks > 0 else 0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")

    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 200))
    win.blit(hits_label, (get_middle(hits_label), 300))
    win.blit(accuracy_label, (get_middle(accuracy_label), 400))

    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                quit()

def get_middle(surface):
    return WIDTH / 2 - surface.get_width()/2

def create_ui_elements():
    elements = {}
    for key, value in login_layout.items():
        if value['type'] == 'label':
            elements[key] = pygame_gui.elements.UILabel(relative_rect=value['rect'], text=value['text'], manager=manager)
        elif value['type'] == 'input':
            elements[key] = pygame_gui.elements.UITextEntryLine(relative_rect=value['rect'], manager=manager)
        elif value['type'] == 'button':
            elements[key] = pygame_gui.elements.UIButton(relative_rect=value['rect'], text=value['text'], manager=manager)
    return elements

def login_screen():
    clock = pygame.time.Clock()  # Create a clock object
    login_elements = create_ui_elements()
    run = True
    while run:
        time_delta = clock.tick(60) / 1000.0  # Use the clock object
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return False, None, None
            manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == login_elements['login_button']:
                    email = login_elements['email_input'].get_text()
                    year_of_birth = login_elements['year_input'].get_text()
                    return True, email, year_of_birth

        manager.update(time_delta)
        WIN.fill(BG_COLOR)
        manager.draw_ui(WIN)
        pygame.display.update()

    return False, None, None

def main():
    run = True
    targets = []
    powerups = []
    clock = pygame.time.Clock()

    logged_in, email, year_of_birth = login_screen()
    if not logged_in:
        pygame.quit()
        return

    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()
    lives = LIVES
    slow_motion = False
    slow_motion_end_time = 0

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)
    pygame.time.set_timer(POWERUP_EVENT, TARGET_INCREMENT * 5)

    while run:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(
                    TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                target_type = random.choice([Target, MovingTarget, FastShrinkingTarget])
                target = target_type(x, y)
                targets.append(target)

            if event.type == POWERUP_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                powerup = PowerUp(x, y)
                powerups.append(powerup)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        if slow_motion and time.time() > slow_motion_end_time:
            slow_motion = False

        for target in targets:
            target.update()

            if target.size <= 0:
                targets.remove(target)
                misses += 1

            if click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_pressed += 1

        for powerup in powerups:
            if click and powerup.collide(*mouse_pos):
                if powerup.type == "extra_life":
                    lives += 1
                elif powerup.type == "slow_motion":
                    slow_motion = True
                    slow_motion_end_time = time.time() + 5
                elif powerup.type == "larger_targets":
                    for target in targets:
                        target.MAX_SIZE *= 1.5
                powerups.remove(powerup)

        if misses >= lives:
            end_screen(WIN, elapsed_time, targets_pressed, clicks)

        draw(WIN, targets, powerups)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses, lives)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
