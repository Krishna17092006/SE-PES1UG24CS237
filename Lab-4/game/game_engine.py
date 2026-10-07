import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick
from .sounds import Sounds

# Game Engine

WHITE = (255, 255, 255)
BG = (15, 15, 25)
BRICK_COLORS = [
    (200, 60, 60),
    (200, 140, 60),
    (200, 200, 60),
    (80, 180, 80),
    (80, 140, 200),
]

# name: (ball speed per axis, paddle width)
DIFFICULTIES = {
    "Easy": (3, 140),
    "Medium": (4, 100),
    "Hard": (6, 70),
}
DIFFICULTY_NAMES = list(DIFFICULTIES)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rows, self.cols = 5, 8

        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.sounds = Sounds()

        self.difficulty = "Medium"
        self.menu_index = DIFFICULTY_NAMES.index(self.difficulty)
        self.reset()

    def reset(self, difficulty=None):
        """Start a fresh round: new paddle, ball, bricks, lives and score."""
        if difficulty is not None:
            self.difficulty = difficulty
        self.ball_speed, paddle_w = DIFFICULTIES[self.difficulty]

        self.paddle = Paddle(self.width // 2 - paddle_w // 2, self.height - 30, paddle_w, 14)

        self.ball = Ball(self.width // 2, self.height - 50, radius=8)
        self.ball.vx, self.ball.vy = self.ball_speed, -self.ball_speed

        self.bricks = self._build_bricks(self.rows, self.cols)

        self.lives = 3
        self.score = 0
        self.game_over = False
        self.result = None  # "win" or "lose"

    def _build_bricks(self, rows, cols):
        bricks = []
        margin, gap, top = 30, 6, 60
        brick_w = (self.width - margin * 2 - gap * (cols - 1)) // cols
        brick_h = 22
        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)
                bricks.append(Brick(x, y, brick_w, brick_h))
        return bricks

    def handle_event(self, event):
        # Paddle movement is held-key input, handled in handle_input.
        # Here we only handle key presses on the end screen.
        if not self.game_over or event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(DIFFICULTY_NAMES)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(DIFFICULTY_NAMES)
        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
            self.menu_index = event.key - pygame.K_1
            self.reset(DIFFICULTY_NAMES[self.menu_index])
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.reset(DIFFICULTY_NAMES[self.menu_index])
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-self.paddle.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(self.paddle.speed, self.width)

    def update(self):
        if self.game_over:
            return

        self.ball.move()

        # Walls: clamp the ball inside and force the velocity away from
        # the wall, so it can never get stuck flipping back and forth.
        if self.ball.x - self.ball.radius <= 0:
            self.ball.x = self.ball.radius
            self.ball.vx = abs(self.ball.vx)
            self.sounds.play("wall")
        elif self.ball.x + self.ball.radius >= self.width:
            self.ball.x = self.width - self.ball.radius
            self.ball.vx = -abs(self.ball.vx)
            self.sounds.play("wall")
        if self.ball.y - self.ball.radius <= 0:
            self.ball.y = self.ball.radius
            self.ball.vy = abs(self.ball.vy)
            self.sounds.play("wall")

        paddle_rect = self.paddle.rect()
        if self.ball.rect().colliderect(paddle_rect):
            side = self._resolve_collision(paddle_rect)
            self.sounds.play("paddle")
            if side == "top":
                # Steer the ball based on where it hit the paddle:
                # edges send it out at a sharper angle than the centre.
                speed = (self.ball.vx ** 2 + self.ball.vy ** 2) ** 0.5
                offset = (self.ball.x - paddle_rect.centerx) / (paddle_rect.width / 2)
                offset = max(-0.75, min(0.75, offset))
                self.ball.vx = speed * offset
                self.ball.vy = -(speed ** 2 - self.ball.vx ** 2) ** 0.5

        for brick in self.bricks:
            if brick.alive and self.ball.rect().colliderect(brick.rect()):
                brick.alive = False
                self.score += 1
                self._resolve_collision(brick.rect())
                self.sounds.play("brick")
                break

        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
                self.sounds.play("game_over")
            else:
                self.sounds.play("lose_life")
                self._reset_ball()

        if all(not b.alive for b in self.bricks):
            self.game_over = True
            self.result = "win"
            self.sounds.play("win")

    def _resolve_collision(self, rect):
        """Bounce the ball off `rect` based on which side it hit.

        The side is the axis with the smallest overlap between the
        ball and the rect. The ball is pushed back out along that axis
        and its velocity on that axis is pointed away from the rect.
        Returns "top", "bottom", "left" or "right".
        """
        ball = self.ball.rect()
        overlap_left = ball.right - rect.left
        overlap_right = rect.right - ball.left
        overlap_top = ball.bottom - rect.top
        overlap_bottom = rect.bottom - ball.top
        overlap_x = min(overlap_left, overlap_right)
        overlap_y = min(overlap_top, overlap_bottom)

        if overlap_x < overlap_y:
            if overlap_left < overlap_right:
                self.ball.x -= overlap_left
                self.ball.vx = -abs(self.ball.vx)
                return "left"
            self.ball.x += overlap_right
            self.ball.vx = abs(self.ball.vx)
            return "right"

        if overlap_top < overlap_bottom:
            self.ball.y -= overlap_top
            self.ball.vy = -abs(self.ball.vy)
            return "top"
        self.ball.y += overlap_bottom
        self.ball.vy = abs(self.ball.vy)
        return "bottom"

    def _reset_ball(self):
        self.ball.x, self.ball.y = self.width // 2, self.height - 50
        self.ball.vx, self.ball.vy = self.ball_speed, -self.ball_speed

    def render(self, screen):
        screen.fill(BG)

        pygame.draw.rect(screen, WHITE, self.paddle.rect())
        pygame.draw.circle(screen, WHITE, (int(self.ball.x), int(self.ball.y)), self.ball.radius)

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                pygame.draw.rect(screen, color, brick.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))

        if self.game_over:
            self._render_end_screen(screen)

    def _render_end_screen(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if self.result == "win":
            title, color = "YOU WIN!", (90, 220, 120)
        else:
            title, color = "GAME OVER", (230, 80, 80)

        lines = [
            (self.big_font, title, color, -130),
            (self.font, f"Final score: {self.score}", WHITE, -70),
            (self.small_font, "Play again - choose difficulty:", (190, 190, 200), -20),
        ]
        for i, name in enumerate(DIFFICULTY_NAMES):
            selected = i == self.menu_index
            text = f"{'>  ' if selected else ''}{i + 1}. {name}{'  <' if selected else ''}"
            col = (255, 220, 90) if selected else (170, 170, 180)
            lines.append((self.font, text, col, 20 + i * 38))
        lines.append((self.small_font, "UP/DOWN + ENTER (or 1/2/3) to play, ESC to quit",
                      (150, 150, 160), 150))

        for font, text, col, dy in lines:
            surf = font.render(text, True, col)
            screen.blit(surf, surf.get_rect(center=(self.width // 2, self.height // 2 + dy)))
