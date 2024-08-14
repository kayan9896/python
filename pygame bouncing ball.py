
import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
width = 500
height = 700
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Breakout")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

# Paddle properties
paddle_width = 50
paddle_height = 10
paddle_x = width // 2 - paddle_width // 2
paddle_y = height - 30

# Ball properties
ball_radius = 5
ball_x = paddle_x + paddle_width // 2
ball_y = paddle_y - ball_radius
ball_speed_x = 0
ball_speed_y = -5
max_speed = 7

# Brick properties
brick_width = 50
brick_height = 20
brick_gap = 3
brick_columns = 8
brick_rows = 5
bricks = []

# Colors
colors = [RED, ORANGE, GREEN, YELLOW, BLUE, PURPLE, PINK, CYAN]

# Lives
lives = 3

# Level
level = 1

# Score
score = 0
high_score = 0
is_game_over = False
is_new_game = True
ball_start = False

# Bonus points
bonus_points = 0
bricks_broken = 0

# Brick Patterns
brick_patterns = [
    [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1]
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 1, 1, 0, 1, 1],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 0]
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 0, 1, 1],
        [1, 0, 1, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ]
]

# Create Bricks
def create_bricks():
    global bricks
    bricks = []
    pattern_index = random.randint(0, len(brick_patterns) - 1)
    pattern = brick_patterns[pattern_index]

    for row in range(brick_rows):
        brick_row = []
        for col in range(brick_columns):
            color_index = random.randint(0, len(colors) - 1)
            if pattern[row][col] == 1:
                brick = {
                    'x': (col * (brick_width + brick_gap)) + ((width - (brick_columns * (brick_width + brick_gap))) // 2),
                    'y': (row * (brick_height + brick_gap)) + 50,
                    'status': True,
                    'color': colors[color_index]
                }
                brick_row.append(brick)
            else:
                brick_row.append(None)
        bricks.append(brick_row)

# Draw Bricks
def draw_bricks():
    for row in bricks:
        for brick in row:
            if brick and brick['status']:
                pygame.draw.rect(window, brick['color'], (brick['x'], brick['y'], brick_width, brick_height))

# Brick Collision
def brick_collision():
    global score, ball_speed_x, ball_speed_y, bonus_points, bricks_broken
    for row in bricks:
        for brick in row:
            if brick and brick['status']:
                if (
                    ball_x + ball_radius > brick['x'] and
                    ball_x - ball_radius < brick['x'] + brick_width and
                    ball_y + ball_radius > brick['y'] and
                    ball_y - ball_radius < brick['y'] + brick_height
                ):
                    brick['status'] = False
                    bricks_broken += 1

                    if bricks_broken <= 10:
                        bonus_points = 0
                    elif bricks_broken <= 20:
                        bonus_points = 1
                    else:
                        bonus_points = 2

                    score += 1 + bonus_points

                    if abs(ball_speed_x) < max_speed:
                        ball_speed_x *= 1.05
                    if abs(ball_speed_y) < max_speed:
                        ball_speed_y *= 1.05

                    collide_right = ball_x + ball_radius - brick['x']
                    collide_left = brick['x'] + brick_width - (ball_x - ball_radius)
                    collide_top = brick['y'] + brick_height - (ball_y - ball_radius)
                    collide_bottom = ball_y + ball_radius - brick['y']

                    min_collision = min(collide_right, collide_left, collide_top, collide_bottom)

                    if min_collision == collide_right or min_collision == collide_left:
                        ball_speed_x = -ball_speed_x
                    else:
                        ball_speed_y = -ball_speed_y

# Reset Ball to Paddle
def ball_reset():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, max_speed, ball_start, bonus_points, bricks_broken
    ball_x = paddle_x + paddle_width // 2
    ball_y = paddle_y - ball_radius
    ball_speed_y = -5
    ball_speed_x = 0
    bonus_points = 0
    bricks_broken = 0
    ball_start = False

# Adjust Ball Movement
def ball_move():
    global ball_x, ball_y
    if ball_start:
        ball_y += ball_speed_y
        ball_x += ball_speed_x
    else:
        ball_x = paddle_x + paddle_width // 2

# Determine What Ball Bounces Off, Score Points, Reset Ball
def ball_boundaries():
    global ball_speed_x, ball_speed_y, lives, is_game_over, bonus_points, bricks_broken

    # Bounce off Left Wall
    if ball_x < ball_radius and ball_speed_x < 0:
        ball_speed_x = -ball_speed_x

    # Bounce off Right Wall
    if ball_x > width - ball_radius and ball_speed_x > 0:
        ball_speed_x = -ball_speed_x

    # Bounce off Ceiling
    if ball_y < ball_radius:
        ball_speed_y = -ball_speed_y

    # Game Over if Ball Goes Off Bottom
    if ball_y > height:
        lives -= 1
        if lives == 0:
            is_game_over = True
        else:
            ball_reset()
            bonus_points = 0
            bricks_broken = 0

    # Bounce off Paddle
    if (
        ball_y > paddle_y - ball_radius and
        ball_x > paddle_x and
        ball_x < paddle_x + paddle_width
    ):
        ball_speed_y = -ball_speed_y
        ball_speed_x = (ball_x - (paddle_x + paddle_width // 2)) * 0.3

# Show Game Over Screen
def show_game_over_screen(winner):
    global high_score
    if score > high_score:
        high_score = score

    font = pygame.font.Font(None, 36)
    text = font.render(winner, True, WHITE)
    text_rect = text.get_rect(center=(width // 2, height // 2 - 50))
    window.blit(text, text_rect)

    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(center=(width // 2, height // 2))
    window.blit(high_score_text, high_score_rect)

    play_again_text = font.render("Press Enter to Play Again", True, WHITE)
    play_again_rect = play_again_text.get_rect(center=(width // 2, height // 2 + 50))
    window.blit(play_again_text, play_again_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
                start_game()
            elif event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                quit()

# Check If All Bricks Are Gone
def game_over():
    global is_game_over, level
    bricks_left = sum(brick['status'] for row in bricks for brick in row if brick)
    if bricks_left == 0:
        level += 1
        if level == 5:
            is_game_over = True
            show_game_over_screen("You Win!")
        else:
            create_bricks()
            ball_reset()
    elif is_game_over:
        show_game_over_screen("Game Over!")

# Start Game, Reset Everything
def start_game():
    global is_game_over, is_new_game, score, lives, level
    is_game_over = False
    is_new_game = False
    score = 0
    lives = 3
    level = 1
    create_bricks()
    ball_reset()

# Show Game Over Screen
def show_game_over_screen(winner):
    global high_score
    if score > high_score:
        high_score = score

    font = pygame.font.Font(None, 36)
    text = font.render(winner, True, WHITE)
    text_rect = text.get_rect(center=(width // 2, height // 2 - 50))
    window.blit(text, text_rect)

    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(center=(width // 2, height // 2))
    window.blit(high_score_text, high_score_rect)

    play_again_text = font.render("Press Enter to Play Again", True, WHITE)
    play_again_rect = play_again_text.get_rect(center=(width // 2, height // 2 + 50))
    window.blit(play_again_text, play_again_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
                start_game()
            elif event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                quit()

# ...

# Game Loop
running = True
clock = pygame.time.Clock()

start_game()  # Start the game initially

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not ball_start:
            ball_start = True

    # Paddle Movement
    mouse_x = pygame.mouse.get_pos()[0]
    paddle_x = mouse_x - paddle_width // 2
    if paddle_x < 0:
        paddle_x = 0
    elif paddle_x > width - paddle_width:
        paddle_x = width - paddle_width

    # Update Game State
    ball_move()
    ball_boundaries()
    brick_collision()
    game_over()

    # Clear Screen
    window.fill(BLACK)

    # Draw Paddle
    pygame.draw.rect(window, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

    # Draw Ball
    pygame.draw.circle(window, WHITE, (int(ball_x), int(ball_y)), ball_radius)

    # Draw Bricks
    draw_bricks()

    # Draw Lives
    font = pygame.font.Font(None, 24)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    window.blit(lives_text, (width - 100, 10))

    # Draw Level
    level_text = font.render(f"Level: {level}", True, WHITE)
    window.blit(level_text, (width - 200, 10))

    # Draw Score
    score_text = font.render(f"Score: {score}", True, WHITE)
    window.blit(score_text, (width - 300, 10))

    # Draw High Score
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    window.blit(high_score_text, (10, 10))

    # Draw Click to Start
    if not ball_start:
        start_text = font.render("Click to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(width // 2, height // 2))
        window.blit(start_text, start_rect)

    # Update Display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()


'''

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Breakout</title>
    <link rel="icon" type="image/png" href="favicon.png">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Script -->
    <script src="script.js"></script>
</body>
</html>

body {
  margin: 0;
  background-color: rgb(39, 39, 39);
  display: flex;
  justify-content: center;
  font-family: "Courier New", Courier, monospace;
}

canvas {
  margin-top: 25px;
  z-index: 10;
}

.game-over-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  height: 700px;
  background-color: rgb(56, 56, 56);
  margin-top: -4px;
  z-index: 11;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: whitesmoke;
}

button {
  cursor: pointer;
  color: rgb(0, 0, 0);
  background-color: rgb(195, 195, 195);
  border: none;
  height: 50px;
  width: 200px;
  border-radius: 5px;
  font-size: 20px;
  font-family: "Courier New", Courier, monospace;
}

button:hover {
  filter: brightness(80%);
}

button:active {
  transform: scale(0.95);
}

button:focus {
  outline: none;
}

/* Montior and Larger */
@media screen and (min-width: 1800px) {
  canvas {
    margin-top: 100px;
  }

  .game-over-container {
    margin-top: -19px;
  }
}

/* Large Smartphone (Vertical) */
@media screen and (max-width: 500px) {
  canvas {
    width: 100%;
    height: 700px;
    margin-top: 50px;
  }

  .game-over-container {
    width: 100%;
    height: 700px;
  }
}



// Canvas
const { body } = document;
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');
const width = 500;
const height = 700;
const screenWidth = window.screen.width;
const canvasPosition = screenWidth / 2 - width / 2;
const isMobile = window.matchMedia('(max-width: 600px)');
const gameOverEl = document.createElement('div');

// Paddle
const paddleHeight = 10;
const paddleWidth = 50;
const paddleDiff = 25;
let paddleBottomX = 225;
let playerMoved = false;

// Ball
let ballX = paddleBottomX + paddleDiff;
let ballY = height - 30;
const ballRadius = 5;

// Speed
let speedY;
let speedX;
let maxSpeed = 5;

// Bricks
const brickWidth = 50;
const brickHeight = 20;
const brickGap = 3;
const brickColumns = 8;
const brickRows = 5;
const bricks = [];

// Colors
const colors = ['red', 'orange', 'green', 'yellow', 'blue', 'purple', 'pink', 'cyan'];

// Lives
let lives = 3;

// Level
let level = 1;

// Score
let score = 0;
let isGameOver = true;
let isNewGame = true;
let ballStart = false;

// Brick Patterns
const brickPatterns = [
  [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1]
  ],
  [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
  ],
  [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 0, 1],
    [0, 1, 1, 1, 1, 1, 1, 0]
  ],
  [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 0, 1, 0, 1],
    [1, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
  ]
];

// Create Bricks
function createBricks() {
  const patternIndex = Math.floor(Math.random() * brickPatterns.length);
  const pattern = brickPatterns[patternIndex];

  for (let row = 0; row < brickRows; row++) {
    bricks[row] = [];
    for (let col = 0; col < brickColumns; col++) {
      const colorIndex = Math.floor(Math.random() * colors.length);
      if (pattern[row][col] === 1) {
        bricks[row][col] = {
          x: (col * (brickWidth + brickGap)) + ((width - (brickColumns * (brickWidth + brickGap))) / 2),
          y: (row * (brickHeight + brickGap)) + 50,
          status: true,
          color: colors[colorIndex]
        };
      } else {
        bricks[row][col] = {
          x: 0,
          y: 0,
          status: false,
          color: ''
        };
      }
    }
  }
}

// Draw Bricks
function drawBricks() {
  bricks.forEach(column => {
    column.forEach(brick => {
      if (brick.status) {
        context.fillStyle = brick.color;
        context.fillRect(brick.x, brick.y, brickWidth, brickHeight);
      }
    });
  });
}

// Brick Collision
function brickCollision() {
  bricks.forEach(column => {
    column.forEach(brick => {
      if (brick.status) {
        if (
          ballX + ballRadius > brick.x &&
          ballX - ballRadius < brick.x + brickWidth &&
          ballY + ballRadius > brick.y &&
          ballY - ballRadius < brick.y + brickHeight
        ) {
          brick.status = false;
          score++;

          // Determine from which side the collision happened
          const collideRight = ballX + ballRadius - brick.x;
          const collideLeft = brick.x + brickWidth - (ballX - ballRadius);
          const collideTop = brick.y + brickHeight - (ballY - ballRadius);
          const collideBottom = ballY + ballRadius - brick.y;

          const min = Math.min(collideRight, collideLeft, collideTop, collideBottom);

          if (min === collideRight || min === collideLeft) {
            speedX = -speedX; // Reverse horizontal direction
          } else {
            speedY = -speedY; // Reverse vertical direction
          }
        }
      }
    });
  });
}

// Render Everything on Canvas
function renderCanvas() {
  // Canvas Background
  context.fillStyle = 'black';
  context.fillRect(0, 0, width, height);

  // Paddle
  context.fillStyle = 'white';
  context.fillRect(paddleBottomX, height - 20, paddleWidth, paddleHeight);

  // Ball
  context.beginPath();
  context.arc(ballX, ballY, ballRadius, 2 * Math.PI, false);
  context.fillStyle = 'white';
  context.fill();

  // Bricks
  drawBricks();

  // Lives
  context.fillStyle = 'white';
  context.font = '16px Courier New';
  context.fillText(`Lives: ${lives}`, width - 100, 20);

  // Level
  context.fillStyle = 'white';
  context.font = '16px Courier New';
  context.fillText(`Level: ${level}`, width - 200, 20);

  // Score
  context.fillStyle = 'white';
  context.font = '16px Courier New';
  context.fillText(`Score: ${score}`, width - 300, 20);

  // Click to Start
  if (!ballStart) {
    context.fillStyle = 'white';
    context.font = '20px Courier New';
    context.fillText(`Click to Start`, width / 2 - 50, height / 2);
  }
}

// Create Canvas Element
function createCanvas() {
  canvas.width = width;
  canvas.height = height;
  body.appendChild(canvas);
  renderCanvas();
}

// Reset Ball to Paddle
function ballReset() {
  ballX = paddleBottomX + paddleDiff;
  ballY = height - 30;
  speedY = -3;
  speedX = 0;
  maxSpeed = 5;
  ballStart = false;
}

// Adjust Ball Movement
function ballMove() {
  if (ballStart) {
    // Vertical Speed
    ballY += speedY;
    // Horizontal Speed
    if (playerMoved) {
      ballX += speedX;
    }
  } else {
    ballX = paddleBottomX + paddleDiff;
  }
}

// Determine What Ball Bounces Off, Score Points, Reset Ball
function ballBoundaries() {
  // Bounce off Left Wall
  if (ballX < 0 && speedX < 0) {
    speedX = -speedX;
  }
  // Bounce off Right Wall
  if (ballX > width && speedX > 0) {
    speedX = -speedX;
  }
  // Bounce off Ceiling
  if (ballY < 0) {
    speedY = -speedY;
  }
  // Game Over if Ball Goes Off Bottom
  if (ballY > height) {
    lives--;
    if (lives === 0) {
      isGameOver = true;
    } else {
      ballReset();
    }
  }
  // Bounce off Paddle
  if (ballY > height - paddleDiff) {
    if (ballX > paddleBottomX && ballX < paddleBottomX + paddleWidth) {
      speedY = -speedY;
      if (playerMoved) {
        speedX = (ballX - (paddleBottomX + paddleDiff)) * 0.3;
      }
    }
  }
}

function showGameOverEl(winner) {
  // Hide Canvas
  canvas.hidden = true;

  // Container
  gameOverEl.textContent = '';
  gameOverEl.classList.add('game-over-container');

  // Title
  const title = document.createElement('h1');
  title.textContent = `${winner}`;

  // Button
  const playAgainBtn = document.createElement('button');
  playAgainBtn.setAttribute('onclick', 'startGame()');
  playAgainBtn.textContent = 'Play Again';

  // Append
  gameOverEl.append(title, playAgainBtn);
  body.appendChild(gameOverEl);
}

// Check If All Bricks Are Gone
function gameOver() {
  const bricksLeft = bricks.flat().filter(brick => brick.status).length;
  if (bricksLeft === 0) {
    level++;
    if (level === 5) {
      isGameOver = true;
      showGameOverEl('You Win!');
    } else {
      createBricks();
      ballReset();
    }
  } else if (isGameOver) {
    showGameOverEl('Game Over!');
  }
}

// Called Every Frame
function animate() {
  renderCanvas();
  ballMove();
  ballBoundaries();
  brickCollision();
  gameOver();
  if (!isGameOver) {
    window.requestAnimationFrame(animate);
  }
}

// Start Game, Reset Everything
function startGame() {
  if (isGameOver && !isNewGame) {
    body.removeChild(gameOverEl);
    canvas.hidden = false;
  }
  isGameOver = false;
  isNewGame = false;
  score = 0;
  lives = 3;
  level = 1;
  createBricks();
  ballReset();
  createCanvas();
  canvas.addEventListener('click', () => {
    ballStart = true;
  });
  animate();
  canvas.addEventListener('mousemove', (e) => {
    playerMoved = true;
    // Compensate for canvas being centered
    paddleBottomX = e.clientX - canvasPosition - paddleDiff;
    if (paddleBottomX < paddleDiff) {
      paddleBottomX = 0;
    }
    if (paddleBottomX > width - paddleWidth) {
      paddleBottomX = width - paddleWidth;
    }
    // Hide Cursor
    canvas.style.cursor = 'none';
  });
}

// On Load
startGame();

'''
