"""
BLE sensor reading and paddle controls by Raiun
Foundation of Pong Code adopted from CYBERXPLOIT on Github, with further modifications by Raiun
"""

#Importing the module pygame
import queue
import pygame
import struct
import asyncio
import threading
from ble_sensor_reader import connect_arduino
from bleak import BleakClient

pygame.init()
read_arduino = True

#Setting our window screen
win = pygame.display.set_mode((750, 500))
pygame.display.set_caption("Pong Game")

#Colours to be used in the game
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

#creating a class of objects to be used in the game such as the paddle and ball
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10, 75])
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.points = 0

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10, 10])
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.speed = 10
        self.dx = 1
        self.dy = 1

paddle1 = Paddle()
paddle1.rect.x = 25
paddle1.rect.y = 225

paddle2 = Paddle()
paddle2.rect.x = 715
paddle2.rect.y = 225

paddle_speed = 10

ball = Ball()
ball.rect.x = 375
ball.rect.y = 250

all_sprites = pygame.sprite.Group()
all_sprites.add(paddle1, paddle2, ball)

#Displaying the game screen
def redraw():
    win.fill(black)
    #Title Font
    font = pygame.font.SysFont("SYNCOPATE", 60)
    text = font.render("PONG", False, white)
    textRect = text.get_rect()
    textRect.center = (750 // 2, 25)
    win.blit(text, textRect)

    #Player 1 Score
    p1_score = font.render(str(paddle1.points), False, white)
    p1Rect = p1_score.get_rect()
    p1Rect.center = (50, 50)
    win.blit(p1_score, p1Rect)

    #Player 2 Score
    p2_score = font.render(str(paddle2.points), False, white)
    p2Rect = p2_score.get_rect()
    p2Rect.center = (700, 50)
    win.blit(p2_score, p2Rect)

    all_sprites.draw(win)
    pygame.display.update()

async def read_imu(user_input, device, data_queue):
    async with BleakClient(device) as client:
        while read_arduino == True:
            data = await client.read_gatt_char("00002101-0000-1000-8000-00805f9b34fb")
            #print(f"data: {data}")
            # Update user_input based on the received BLE value
            user_input = struct.unpack("f", data)
            print(f"user input = {user_input}")
            data_queue.put(user_input)
            #asyncio.sleep(0.5)

def start_ble_task(user_input, device, data_queue):
    asyncio.run(read_imu(user_input, device, data_queue))

# Main loop
if __name__ == "__main__":
    run = True
    p1_input = 0
    p2_input = 0
    clock = pygame.time.Clock()
    p1_controller = asyncio.run(connect_arduino())
    p2_controller = asyncio.run(connect_arduino(name="Player 2 Nano"))
    data_queue = queue.Queue()
    ble_thread = threading.Thread(target=start_ble_task, args=(p1_input, p1_controller, data_queue))
    ble_thread2 = threading.Thread(target=start_ble_task, args=(p2_input, p2_controller, data_queue))
    ble_thread.start()

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                read_arduino = False

        if p1_input > 0.3:
            if (paddle1.rect.y > -0.3):
                paddle1.rect.y += -paddle_speed
        elif p1_input < 0:
            if (paddle1.rect.y < 425):
                paddle1.rect.y += paddle_speed
        
        if p2_input > 0.3:
            if (paddle2.rect.y > 0):
                paddle1.rect.y += -paddle_speed
        elif p2_input < -0.3:
            if (paddle2.rect.y < 425):
                paddle1.rect.y += paddle_speed

        # Ball movement
        ball.rect.x += ball.speed * ball.dx
        ball.rect.y += ball.speed * ball.dy

        # Ball collisions with the walls i.e The ball bounces back instead of moving continously
        if ball.rect.y > 490:
            ball.dy = -1

        if ball.rect.x > 740:
            ball.rect.x, ball.rect.y = 375, 250
            ball.dx = -1
            paddle1.points +=1

        if ball.rect.y < 10:
            ball.dy = 1

        if ball.rect.x < 10:
            ball.rect.x, ball.rect.y = 375, 250
            ball.dx = 1
            paddle2.points += 1
        
        if paddle1.rect.colliderect(ball.rect):
            ball.dx = 1

        if paddle2.rect.colliderect(ball.rect):
            ball.dx = -1

        while not data_queue.empty():
            user_input = data_queue.get()
        
        # Calling the redraw function
        redraw()

    ble_thread.join()
    pygame.quit()