import pygame
import random
import sys
import json
import os

# ─────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────
WINDOW_W, WINDOW_H = 800, 600
GRID_SIZE          = 20
GRID_W             = WINDOW_W // GRID_SIZE
GRID_H             = WINDOW_H // GRID_SIZE

# Colours
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = ( 34, 177,  76)
DARK_GREEN = ( 20, 120,  50)
RED        = (220,  50,  50)
YELLOW     = (255, 215,   0)
GRAY       = (180, 180, 180)
DARK_GRAY  = ( 40,  40,  40)
BG_COLOR   = ( 15,  15,  25)
UI_COLOR   = ( 25,  25,  40)

# Speeds (frames per second)
SPEEDS = {"Easy": 8, "Medium": 14, "Hard": 22}

HIGH_SCORE_FILE = "highscore.json"


# ─────────────────────────────────────────
#  HELPER – HIGH SCORE PERSISTENCE
# ─────────────────────────────────────────
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE) as f:
                return json.load(f).get("high_score", 0)
        except Exception:
            pass
    return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump({"high_score": score}, f)


# ─────────────────────────────────────────
#  SNAKE CLASS
# ─────────────────────────────────────────
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.body      = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir  = (1, 0)
        self.grew      = False

    def set_direction(self, new_dir):
        # Prevent 180° reversal
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.next_dir = new_dir

    def move(self):
        self.direction = self.next_dir
        head = (self.body[0][0] + self.direction[0],
                self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        if not self.grew:
            self.body.pop()
        self.grew = False

    def grow(self):
        self.grew = True

    def check_wall_collision(self):
        hx, hy = self.body[0]
        return hx < 0 or hx >= GRID_W or hy < 0 or hy >= GRID_H

    def check_self_collision(self):
        return self.body[0] in self.body[1:]

    def draw(self, surface):
        for i, (x, y) in enumerate(self.body):
            color = GREEN if i == 0 else DARK_GREEN
            rect  = pygame.Rect(x * GRID_SIZE + 1, y * GRID_SIZE + 1,
                                GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(surface, color, rect, border_radius=4)
            # Eyes on head
            if i == 0:
                ex = x * GRID_SIZE + GRID_SIZE // 2
                ey = y * GRID_SIZE + GRID_SIZE // 2
                pygame.draw.circle(surface, WHITE, (ex - 3, ey - 3), 3)
                pygame.draw.circle(surface, WHITE, (ex + 3, ey - 3), 3)
                pygame.draw.circle(surface, BLACK, (ex - 3, ey - 3), 1)
                pygame.draw.circle(surface, BLACK, (ex + 3, ey - 3), 1)


# ─────────────────────────────────────────
#  FOOD CLASS
# ─────────────────────────────────────────
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn([])

    def spawn(self, snake_body):
        while True:
            pos = (random.randint(0, GRID_W - 1),
                   random.randint(0, GRID_H - 1))
            if pos not in snake_body:
                self.position = pos
                break

    def draw(self, surface):
        x, y = self.position
        cx = x * GRID_SIZE + GRID_SIZE // 2
        cy = y * GRID_SIZE + GRID_SIZE // 2
        pygame.draw.circle(surface, RED,    (cx, cy), GRID_SIZE // 2 - 2)
        pygame.draw.circle(surface, YELLOW, (cx - 2, cy - 2), 3)


# ─────────────────────────────────────────
#  GAME CLASS
# ─────────────────────────────────────────
class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🐍 Snake Game")
        self.screen  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock   = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 28)
        self.font_sm = pygame.font.SysFont("Arial", 20)

        self.high_score = load_high_score()
        self.difficulty = "Medium"
        self.state      = "menu"   # menu | playing | game_over

        self.snake = Snake()
        self.food  = Food()
        self.score = 0

    # ── DRAWING HELPERS ──────────────────
    def draw_text_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (WINDOW_W // 2 - surf.get_width() // 2, y))

    def draw_button(self, text, font, color, bg, x, y, w, h):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, bg, rect, border_radius=10)
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=10)
        t = font.render(text, True, color)
        self.screen.blit(t, (x + w // 2 - t.get_width() // 2,
                             y + h // 2 - t.get_height() // 2))
        return rect

    def draw_grid(self):
        for x in range(0, WINDOW_W, GRID_SIZE):
            pygame.draw.line(self.screen, (25, 25, 40), (x, 0), (x, WINDOW_H))
        for y in range(0, WINDOW_H, GRID_SIZE):
            pygame.draw.line(self.screen, (25, 25, 40), (0, y), (WINDOW_W, y))

    # ── SCREENS ──────────────────────────
    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        self.draw_text_center("🐍 SNAKE GAME", self.font_lg, GREEN,  80)
        self.draw_text_center("Classic Arcade", self.font_sm, GRAY, 140)

        self.draw_text_center("Select Difficulty:", self.font_md, WHITE, 210)
        bw, bh, gap = 160, 50, 20
        total = 3 * bw + 2 * gap
        sx = (WINDOW_W - total) // 2
        colors = {"Easy": (50, 200, 100), "Medium": YELLOW, "Hard": RED}
        self.diff_rects = {}
        for i, diff in enumerate(["Easy", "Medium", "Hard"]):
            bx = sx + i * (bw + gap)
            bg = colors[diff] if self.difficulty == diff else DARK_GRAY
            r  = self.draw_button(diff, self.font_sm, colors[diff], bg,
                                  bx, 270, bw, bh)
            self.diff_rects[diff] = r

        self.start_rect = self.draw_button("▶  START GAME", self.font_md,
                                           BLACK, GREEN,
                                           WINDOW_W // 2 - 140, 360, 280, 55)
        self.draw_text_center("Controls: Arrow Keys  |  P = Pause  |  ESC = Quit",
                              self.font_sm, GRAY, 450)
        self.draw_text_center(f"🏆 High Score: {self.high_score}",
                              self.font_md, YELLOW, 510)

    def draw_hud(self):
        pygame.draw.rect(self.screen, UI_COLOR,
                         pygame.Rect(0, WINDOW_H - 40, WINDOW_W, 40))
        score_t = self.font_md.render(f"Score: {self.score}", True, WHITE)
        hi_t    = self.font_md.render(f"Best: {self.high_score}", True, YELLOW)
        diff_t  = self.font_sm.render(f"[{self.difficulty}]", True, GRAY)
        self.screen.blit(score_t, (10, WINDOW_H - 35))
        self.screen.blit(hi_t,    (WINDOW_W // 2 - hi_t.get_width() // 2,
                                    WINDOW_H - 35))
        self.screen.blit(diff_t,  (WINDOW_W - diff_t.get_width() - 10,
                                    WINDOW_H - 30))

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        self.draw_text_center("GAME OVER", self.font_lg, RED,  150)
        self.draw_text_center(f"Score: {self.score}", self.font_md, WHITE, 230)
        if self.score >= self.high_score:
            self.draw_text_center("🏆 New High Score!", self.font_md, YELLOW, 270)
        else:
            self.draw_text_center(f"Best: {self.high_score}", self.font_md, YELLOW, 270)

        self.retry_rect = self.draw_button("▶  Play Again", self.font_md,
                                           BLACK, GREEN,
                                           WINDOW_W // 2 - 120, 330, 240, 50)
        self.menu_rect  = self.draw_button("⌂  Main Menu", self.font_md,
                                           WHITE, DARK_GRAY,
                                           WINDOW_W // 2 - 120, 395, 240, 50)

    def draw_paused(self):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        self.draw_text_center("⏸  PAUSED", self.font_lg, WHITE,
                              WINDOW_H // 2 - 40)
        self.draw_text_center("Press P to resume", self.font_sm, GRAY,
                              WINDOW_H // 2 + 30)

    # ── GAME LOGIC ───────────────────────
    def start_game(self):
        self.snake.reset()
        self.food.spawn(self.snake.body)
        self.score  = 0
        self.paused = False
        self.state  = "playing"

    def update(self):
        self.snake.move()
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            if self.score > self.high_score:
                self.high_score = self.score
                save_high_score(self.high_score)
            self.state = "game_over"
            return
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 10
            self.food.spawn(self.snake.body)

    # ── MAIN LOOP ────────────────────────
    def run(self):
        self.paused = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "menu"
                        else:
                            pygame.quit(); sys.exit()

                    if self.state == "playing":
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                        if not self.paused:
                            if event.key == pygame.K_UP:
                                self.snake.set_direction((0, -1))
                            elif event.key == pygame.K_DOWN:
                                self.snake.set_direction((0,  1))
                            elif event.key == pygame.K_LEFT:
                                self.snake.set_direction((-1, 0))
                            elif event.key == pygame.K_RIGHT:
                                self.snake.set_direction((1,  0))

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if self.state == "menu":
                        for diff, rect in self.diff_rects.items():
                            if rect.collidepoint(pos):
                                self.difficulty = diff
                        if self.start_rect.collidepoint(pos):
                            self.start_game()
                    elif self.state == "game_over":
                        if self.retry_rect.collidepoint(pos):
                            self.start_game()
                        elif self.menu_rect.collidepoint(pos):
                            self.state = "menu"

            # ── RENDER ──
            if self.state == "menu":
                self.draw_menu()

            elif self.state == "playing":
                if not self.paused:
                    self.update()
                self.screen.fill(BG_COLOR)
                self.draw_grid()
                self.food.draw(self.screen)
                self.snake.draw(self.screen)
                self.draw_hud()
                if self.paused:
                    self.draw_paused()

            elif self.state == "game_over":
                # Keep last game frame visible behind overlay
                self.screen.fill(BG_COLOR)
                self.draw_grid()
                self.food.draw(self.screen)
                self.snake.draw(self.screen)
                self.draw_hud()
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(SPEEDS[self.difficulty])


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    SnakeGame().run()
