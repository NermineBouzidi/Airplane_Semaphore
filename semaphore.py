import pygame
import threading
import time
from pygame.locals import *
from threading import Semaphore

# Initialize pygame
pygame.init()

# Initialize the mixer for sound effects
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Airplane Landing Simulation")

# Load and scale the background image
background_img = pygame.image.load("background.jpg")  
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (82, 139, 133, 255)

# Fonts
font = pygame.font.SysFont("Arial", 24)
collision_font = pygame.font.SysFont("Arial", 40, bold=True)

# Load airplane image
airplane_img = pygame.image.load("airplane.png")
airplane_img = pygame.transform.scale(airplane_img, (190, 60))

# Button positions
button1_rect = pygame.Rect(200, 550, 200, 40)
button2_rect = pygame.Rect(450, 550, 200, 40)

# Load sound effects
landing_sound = pygame.mixer.Sound("landing.wav")  # Sound when airplane lands
collision_sound = pygame.mixer.Sound("collision.wav")  # Sound when planes collide

# Airplane class
class Airplane(threading.Thread):
    def __init__(self, id, start_delay=0, semaphore=None):
        super().__init__()
        self.id = id
        self.x = WIDTH - 200  # Start from top-right
        self.y = -100  # Start off-screen
        self.landing = False
        self.landed = False
        self.running = True
        self.semaphore = semaphore
        self.start_delay = start_delay
        self.message = f"Airplane {self.id} wants to land"

    def run(self):
        global messages, collisions
        time.sleep(self.start_delay)  # Add delay for sequential landing
        
        if self.semaphore:
            self.semaphore.acquire()
        
        self.landing = True
        messages[self.id] = f"Airplane {self.id} is landing..."

        # Play landing sound as soon as the plane starts descending
        landing_sound.play()

        # Move downward (landing)
        while self.y < 470:
            self.y += 2
            self.x -= 1
            time.sleep(0.03)

        # Collision check
        for plane in airplanes:
            if plane.id != self.id and plane.y == 470:  # Check if the plane is on the ground
                if abs(self.x - plane.x) < 190:
                    if not any(plane1.id == self.id and plane2.id == plane.id or plane1.id == plane.id and plane2.id == self.id for plane1, plane2 in collisions):
                         messages["collision"] = "COLLISION!"
                         collisions.append((self, plane))  # Add the pair of planes that collided
                         collision_sound.play()  # Play collision sound
                         break  # Stop checking further once a collision is detected

        self.landed = True
        messages[self.id] = f"Airplane {self.id} has landed!"

        # Move to the left after landing
        while self.x > -150:
            self.x -= 3
            time.sleep(0.03)
        
        self.running = False
        messages[self.id] = ""

        if self.semaphore:
            self.semaphore.release()

# Game loop variables
running = True
mode = None
semaphore = Semaphore(1)
messages = {}
collisions = []  # List to track which planes have collided

def start_simulation(with_semaphore):
    global mode, messages, collisions
    mode = "semaphore" if with_semaphore else "no_semaphore"
    airplanes.clear()
    messages.clear()
    collisions.clear()

    for i in range(4):
        delay = i * 1  # Delay for sequential landing
        plane = Airplane(i + 1, delay, semaphore if with_semaphore else None)
        airplanes.append(plane)
        messages[i + 1] = plane.message
        plane.start()

def draw_scene():
    screen.blit(background_img, (0, 0))  # Set background image

    # Display airplane status at the top
    y_offset = 10
    for msg in messages.values():
        text = font.render(msg, True, BLACK)
        screen.blit(text, (20, y_offset))
        y_offset += 30

    # Draw airplanes
    for plane in airplanes:
        if plane.running:
            screen.blit(airplane_img, (plane.x, plane.y))

    # Draw collisions
    for plane1, plane2 in collisions:
        collision_text = collision_font.render("COLLISION!", True, RED)
        # Display the collision message halfway between the two planes
        avg_x = (plane1.x + plane2.x) // 2
        avg_y = (plane1.y + plane2.y) // 2
        screen.blit(collision_text, (avg_x, avg_y - 40))  # Display above the collision spot

    # Draw buttons
    pygame.draw.rect(screen, GREEN, button1_rect, border_radius=15)
    pygame.draw.rect(screen, GREEN, button2_rect, border_radius=15)
    text1 = font.render("Without Semaphore", True, WHITE)
    text2 = font.render("With Semaphore", True, WHITE)
    screen.blit(text1, (button1_rect.x + 15, button1_rect.y + 5))
    screen.blit(text2, (button2_rect.x + 30, button2_rect.y + 5))

    pygame.display.flip()

# Main game loop
airplanes = []
while running:
    screen.fill(WHITE)
    draw_scene()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            if button1_rect.collidepoint(event.pos):
                start_simulation(False)
            elif button2_rect.collidepoint(event.pos):
                start_simulation(True)

    pygame.time.delay(50)

pygame.quit()