import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick

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

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paddle = Paddle(width // 2 - 50, height - 30, 100, 14)

        self.ball = Ball(width // 2, height - 50, radius=8)
        self.ball.vx, self.ball.vy = 4, -4

        self.rows, self.cols = 5, 8
        self.bricks = self._build_bricks(self.rows, self.cols)

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
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
        # This game only needs continuously-held-key input for the
        # paddle, handled in handle_input each frame.
        pass

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
        elif self.ball.x + self.ball.radius >= self.width:
            self.ball.x = self.width - self.ball.radius
            self.ball.vx = -abs(self.ball.vx)
        if self.ball.y - self.ball.radius <= 0:
            self.ball.y = self.ball.radius
            self.ball.vy = abs(self.ball.vy)

        paddle_rect = self.paddle.rect()
        if self.ball.rect().colliderect(paddle_rect):
            side = self._resolve_collision(paddle_rect)
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
                break

        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
            else:
                self._reset_ball()

        if all(not b.alive for b in self.bricks):
            self.game_over = True
            self.result = "win"

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
        self.ball.vx, self.ball.vy = 4, -4

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

        if self.game_over and not getattr(self, "_game_over_logged", False):
            # NOTE: no proper end screen yet - see Task 2 in the README.
            if self.result == "win":
                print("You win! Final score:", self.score)
            else:
                print("Game over! Final score:", self.score)
            self._game_over_logged = True
