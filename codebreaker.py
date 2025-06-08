# codebreaker.py

import pygame
import sys
import itertools
from collections import Counter

# ─── Settings ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 600, 400
FPS = 60
FONT_SIZE = 28
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (240, 240, 240)
BLACK_PEG_COLOR = (0, 0, 0)
WHITE_PEG_COLOR = (240, 240, 240)
PEG_RADIUS = 8
PEG_SPACING = 20
MAX_TURNS = 5

# ─── Helper Functions ─────────────────────────────────────────────────────────
def get_feedback(secret: str, guess: str):
    """Return (black, white) peg counts for a guess against the secret."""
    # Black = correct digit & position
    black = sum(s == g for s, g in zip(secret, guess))
    # Total matches (ignoring position) minus black = white
    secret_count = Counter(secret)
    guess_count  = Counter(guess)
    total_matches = sum(min(secret_count[d], guess_count[d]) for d in secret_count)
    white = total_matches - black
    return black, white

# ─── AI Class ─────────────────────────────────────────────────────────────────
class CodebreakerAI:
    def __init__(self):
        digits = '123456'
        self.possible = [''.join(p) for p in itertools.product(digits, repeat=4)]
        self.candidates = self.possible.copy()

    def first_guess(self):
        return '1122'

    def next_guess(self, last_guess: str, feedback: tuple):
        black, white = feedback
        # prune candidates
        self.candidates = [
            code for code in self.candidates
            if get_feedback(code, last_guess) == (black, white)
        ]
        # minimax selection
        best_score = None
        best_guess = None
        for guess in self.possible:
            # group candidates by their feedback if this guess were secret
            partitions = Counter(get_feedback(secret, guess) for secret in self.candidates)
            worst_case = max(partitions.values(), default=0)
            if (best_score is None
                or worst_case < best_score
                or (worst_case == best_score
                    and guess in self.candidates
                    and best_guess not in self.candidates)):
                best_score = worst_case
                best_guess = guess
        return best_guess

# ─── Main Game ────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Codebreaker AI Demo")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)

    # Game state
    secret      = ''
    input_mode  = True
    ai          = None
    guess       = ''
    feedback    = (0, 0)
    turn        = 1
    game_over   = False
    result_msg  = ''
    await_next  = False

    prompt_text = 'Enter 4-digit code (1–6) and press Enter:'

    while True:
        screen.fill(BG_COLOR)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Secret entry
            if input_mode and event.type == pygame.KEYDOWN:
                if event.unicode in '123456' and len(secret) < 4:
                    secret += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    secret = secret[:-1]
                elif event.key == pygame.K_RETURN and len(secret) == 4:
                    ai        = CodebreakerAI()
                    guess     = ai.first_guess()
                    input_mode = False
                    await_next = False

            # Step-by-step guess
            if (not input_mode
                and not game_over
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN
                and await_next):

                # compute feedback of last guess
                feedback = get_feedback(secret, guess)
                black, white = feedback

                # check end
                if black == 4:
                    result_msg = f'🏆 Victory! Cracked in {turn} turns.'
                    game_over = True
                elif turn >= MAX_TURNS:
                    result_msg = f'💀 Defeat! The code was {secret}.'
                    game_over = True
                else:
                    # next guess
                    guess = ai.next_guess(guess, feedback)
                    turn += 1

                await_next = False

        # Draw UI
        if input_mode:
            txt_surf = font.render(prompt_text, True, TEXT_COLOR)
            screen.blit(txt_surf, (20, 20))
            code_surf = font.render(secret, True, TEXT_COLOR)
            screen.blit(code_surf, (20, 60))

        else:
            # Show current guess
            guess_surf = font.render(f'Turn {turn}: AI guesses {guess}', True, TEXT_COLOR)
            screen.blit(guess_surf, (20, 20))

            # Always compute feedback for display
            black, white = get_feedback(secret, guess)

            # Draw black pegs (row 1)
            for i in range(black):
                x = 40 + i * PEG_SPACING
                y = 80
                pygame.draw.circle(screen, BLACK_PEG_COLOR, (x, y), PEG_RADIUS)

            # Draw white pegs (row 2)
            for i in range(white):
                x = 40 + i * PEG_SPACING
                y = 80 + PEG_SPACING
                pygame.draw.circle(screen, WHITE_PEG_COLOR, (x, y), PEG_RADIUS)

            # Show result or next-prompt
            if game_over:
                end_surf = font.render(result_msg, True, TEXT_COLOR)
                screen.blit(end_surf, (20, 140))
            else:
                nxt_surf = font.render("Press Enter for next guess", True, TEXT_COLOR)
                screen.blit(nxt_surf, (20, HEIGHT - 40))
                await_next = True

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
