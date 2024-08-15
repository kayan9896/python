
import pygame
import random
import math

pygame.init()

clock = pygame.time.Clock()

screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Brick Breaker")

black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)


shake_offset = [0, 0]   # Current shake offset
shake_length = 0.66
shake_duration = shake_length     # Duration of shake effect (number of frames)
shake_magnitude = 3     # Maximum offset magnitude
shake_active = False    # Flag to track if shaking is active

max_bounce_angle = 67  # Maximum angle in degrees (adjust as needed)

frames_since_clear = 0

line_angle = 90
line_angle_dir = 1 

# New constants
PADDLE_SPEED = 9   # Max paddle speed 
trail_limit = 10
trail_start_scale = 1  # Trail sprites start at 80% of ball size
trail_end_scale = 0.5   # Trail sprites end at 20% of ball size 
trail_start_alpha = 10

TARGET_FPS = 60
MIN_FPS = 24
FPS_CONSTANT_60 = (1/60.0)
PADDLE_SPEED = 540   # 540 pixels per second at 60 FPS
BASE_BALL_SPEED = 420
TRAIL_DURATION = 0.16 # seconds

launching_ball = True

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size=4, vel_x=0, vel_y=0, gravity=6/FPS_CONSTANT_60):
        super().__init__()
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = -vel_x/2.5 + (float(random.uniform(-20, 20))/10.0)/FPS_CONSTANT_60  # Random horizontal speed
        self.speed_y = vel_y/2.5 + (float(random.uniform(-40, 6))/10.0)/FPS_CONSTANT_60  # Upwards vertical speed
        self.gravity = gravity

        self.x_float = x
        self.y_float = y

    def update(self, delta):
        self.speed_y += self.gravity * delta
        self.x_float += self.speed_x * delta
        self.y_float += self.speed_y * delta

        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

        # Remove when out of bounds
        if self.rect.top > screen_height:
            self.kill()

        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x  *= -1
            self.rect.x += self.speed_x * delta

        if self.rect.top < 0:
            self.speed_y  *= -1
            self.rect.y += self.speed_y * delta

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
        self.radius = 5 
        pygame.draw.circle(self.image, white, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 20
        self.speed_x = random.randint(-5, 5)
        self.speed_y = -5

        self.x_float = self.rect.x 
        self.y_float = self.rect.y


    def update(self, delta):
        self.x_float += self.speed_x * delta
        self.y_float += self.speed_y * delta

        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

        # Bounce off walls
        if self.rect.left < 0 and self.speed_x < 0:
            self.speed_x *= -1
            self.rect.left = 0

        if self.rect.right > screen_width and self.speed_x > 0:
            self.speed_x *= -1
            self.rect.right = screen_width

        if self.rect.top < 0 and self.speed_y < 0:
            self.speed_y *= -1
            self.rect.top = 0

        # Game over if ball goes off bottom
        if self.rect.bottom > screen_height:
            return True  # Game over

        return False  # Game continues

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([75, 10])
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 10


    def update(self, delta):
        # Get desired x position from mouse
        desired_x = pygame.mouse.get_pos()[0] - (self.rect.width // 2)

        # Calculate distance to move
        dist = desired_x - self.rect.x

        max_dist = PADDLE_SPEED * delta
        # Limit distance to max speed
        if dist > max_dist:
            dist = max_dist
        if dist < -max_dist:
            dist = -max_dist

        # Move paddle
        self.rect.x += dist

        # Keep paddle within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

class Brick(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface([35, 15])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def create_particles(x, y, color, quantity=15, size=4, ball_obj = Ball()):
    particle_group = pygame.sprite.Group()
    for _ in range(quantity):
        particle = Particle(x, y, color, size, vel_x=ball_obj.speed_x, vel_y=ball_obj.speed_y)
        particle_group.add(particle)
    return particle_group



def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 

all_sprites = pygame.sprite.Group()
brick_list = pygame.sprite.Group()
trail_group = pygame.sprite.Group()

ball = Ball()
paddle = Paddle()
all_sprites.add(ball, paddle)

rows = 6
columns = 14
colors = [red, red, green, green, blue, blue]
for i in range(rows):
    for j in range(columns):
        brick = Brick(colors[i], j * (35 + 5) + 20, i * (15 + 5) + 40)
        brick_list.add(brick)
        all_sprites.add(brick)

lives = 3
score = 0
font = pygame.font.Font(None, 36)

running = True
game_over = False

launch_timer = 0

particle_groups = []  # Holds all active particle groups

while running:
    # Game clock (limit frame rate)
    elapsed = clock.tick() / 1000
    dt = min(elapsed, 1/MIN_FPS)  # deltaTime in seconds
    catchup = max(math.floor(elapsed/(1/MIN_FPS)),1)

    for F in range(catchup):

      # Rotate line angle
      if line_angle >= max_bounce_angle + 90:
          line_angle_dir = -1
      elif line_angle <= -max_bounce_angle + 90:
          line_angle_dir = 1

      line_angle += 300 * line_angle_dir * dt

      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              running = False
          if event.type == pygame.MOUSEBUTTONDOWN and launching_ball:
              launching_ball = False
              launch_timer = 0

              # Set ball direction along line angle
              ball.speed_x = -BASE_BALL_SPEED * math.cos(math.radians(line_angle))
              ball.speed_y = -BASE_BALL_SPEED * math.sin(math.radians(line_angle))

              launching_ball = False


      if launching_ball:
          ball.rect.centerx = paddle.rect.centerx
          ball.rect.bottom = paddle.rect.top

      else:
          launch_timer += 1

      # Update game objects
      # Screen Edge Collisions
      if ball.rect.right >= screen_width or ball.rect.left <= 0:
          shake_active = True
          shake_magnitude = 3
          shake_length = 0.66
          shake_duration = shake_length  # Reset duration

      if ball.rect.top < 0:
          shake_active = True
          shake_magnitude = 3
          shake_length = 0.66
          shake_duration = shake_length  # Reset duration

      # Update shake offset (if active)
      if shake_active:
          current_duration_fraction = shake_duration / shake_length
          current_magnitude = shake_magnitude * current_duration_fraction ** 2
          shake_offset[0] = random.randint(-int(current_magnitude), int(current_magnitude))
          shake_offset[1] = random.randint(-int(current_magnitude), int(current_magnitude))
          shake_duration -= dt

          if shake_duration <= 0:
              shake_active = False
              shake_offset = [0, 0]  # Reset offset

      if not launching_ball:
        trail = pygame.Surface((2*ball.radius, 2*ball.radius), pygame.SRCALPHA) 
        pygame.draw.circle(trail, white, (ball.radius, ball.radius), ball.radius)
        trail = trail.convert_alpha() # Add this!

        trail_sprite = pygame.sprite.Sprite()
        trail_sprite.image = trail
        trail_sprite.image.set_alpha(trail_start_alpha) 
        trail_sprite.rect = trail.get_rect(center=ball.rect.center)
        trail_sprite.rect.center = ball.rect.center

        trail_sprite.spawn_time = pygame.time.get_ticks()
        trail_sprite.timer = 0

        trail_sprite.origin = trail_sprite.rect.center
        trail_group.add(trail_sprite)

        game_over = ball.update(dt)
        trail_group.update()

        paddle.update(dt)

      for i, trail in enumerate(reversed(trail_group.sprites())):
        # Scale sprite image size
        lerp = trail.timer / TRAIL_DURATION
        scale_factor = lerp * trail_end_scale + (1 - lerp) * trail_start_scale
        trail.image = pygame.transform.scale(trail.image, (int(ball.radius * scale_factor * 2), 
                                                  int(ball.radius * scale_factor * 2)))
        pygame.draw.circle(trail.image, white, (trail.image.get_width()//2, trail.image.get_height()//2), trail.image.get_width()//2)

        trail.timer += dt
        trail.rect = trail.image.get_rect(center=trail.origin)

        if trail.timer < TRAIL_DURATION:
            trail.image.set_alpha(trail_start_alpha - trail.timer/TRAIL_DURATION*trail_start_alpha)

        else:
            trail.kill() 


      # Collision handling
      hit_bricks = pygame.sprite.spritecollide(ball, brick_list, True)
      for brick in hit_bricks:
          brick.kill()
          ball.rect.x -= ball.speed_x * dt
          ball.rect.y -= ball.speed_y * dt

          # Collision with top/bottom of brick (vertical bounce):
          if ball.rect.bottom >= brick.rect.top or ball.rect.top <= brick.rect.bottom:
              if ball.rect.centerx < brick.rect.right and ball.rect.centerx > brick.rect.left:
                  ball.speed_y *= -1  # Reverse y-direction
              else:
                  if ball.speed_x < 0 and brick.rect.right < ball.rect.centerx:
                      ball.speed_x *= -1  # Reverse x-direction
                  elif ball.speed_x > 0 and brick.rect.left > ball.rect.centerx:
                      ball.speed_x *= -1  # Reverse x-direction
                  if ball.rect.centery > brick.rect.bottom or ball.rect.centery < brick.rect.top:
                      ball.speed_y *= -1  # Reverse y-direction

          else:
              ball.speed_y *= -1  # Reverse y-direction
          score += 1

          # Create particles (color based on brick color)
          random.seed()
          new_particles = create_particles(ball.rect.centerx, ball.rect.centery, brick.image.get_at((0,0)), quantity=12, ball_obj=ball)
          particle_groups.append(new_particles)

          shake_active = True
          shake_magnitude = 2
          shake_length = 1
          shake_duration = shake_length  # Reset duration

          # Check if all bricks are destroyed
          if len(brick_list) == 0:
              print("You Won!")
              # Display "You Won" message
              # ... (code to handle winning condition)

      # Check for collision with paddle
      if launch_timer > 5 and pygame.sprite.collide_rect(ball, paddle):
          ball.rect.x -= ball.speed_x * dt # Move ball back to prevent sticking
          ball.rect.bottom = paddle.rect.top-2  # Align ball with top of paddle

          old_speed = ball.speed_x

          # Calculate bounce angle
          collision_offset = clamp((ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2),-1,1)
          bounce_angle = max_bounce_angle * collision_offset + 90

          # Calculate new speeds based on angle
          ball_speed = math.sqrt(ball.speed_x ** 2 + ball.speed_y ** 2)  # Original speed
          ball.speed_x = ball_speed * math.cos(math.radians(bounce_angle))
          ball.speed_y = ball_speed * math.sin(math.radians(bounce_angle))

          if old_speed < 0 and ball.speed_x > 0:
              ball.speed_x *= -1

          if old_speed > 0 and ball.speed_x < 0:
              ball.speed_x *= -1

          # Ensure ball moves upwards after collision
          if ball.speed_y > 0:
              ball.speed_y *= -1 

          new_particles = create_particles(ball.rect.centerx, ball.rect.top, white, quantity=3, size=2, ball_obj=ball)
          particle_groups.append(new_particles)

          shake_active = True
          shake_magnitude = 2
          shake_length = 0.5
          shake_duration = shake_length  # Reset duration

      # Drawing
      screen.fill(black)

      # Apply shake offset
      shifted_screen = screen.copy()  # Create temporary surface

      if game_over:
          # Handle game over (display message, etc.)
          pass  # Placeholder for your game over logic

      if launching_ball:
        line_length = 60 
        end_x = paddle.rect.centerx - line_length * math.cos(math.radians(line_angle))
        end_y = paddle.rect.top - line_length * math.sin(math.radians(line_angle))
        pygame.draw.line(shifted_screen, white, (paddle.rect.centerx, paddle.rect.top), (end_x, end_y))

      # Draw the sprites
      trail_group.draw(shifted_screen)
      all_sprites.draw(shifted_screen)

      # Update and draw all particle groups
      for group in particle_groups:
        group.update(dt)
        if len(group.sprites()) == 0:
          particle_groups.remove(group)
        group.draw(shifted_screen)

      # Draw temporary surface with offset
      screen.blit(shifted_screen, shake_offset)

      # Display score and lives
      text = font.render("Score: " + str(score), True, white)
      screen.blit(text, [20, 10])

      text = font.render("Lives: " + str(lives), True, white)
      screen.blit(text, [screen_width - 100, 10])

      # Update the display
      pygame.display.flip()
