import pygame
from src.game.game import Game
from src.vision.hand_tracking import HandTracker

def main():
    pygame.init()

    game = Game()
    tracker = HandTracker()

    running = True
    while running:
        gestures = tracker.get_gestures()
        events = pygame.event.get()
        
        game.update(gestures, events)
        game.draw(gestures)

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()

if __name__ == "__main__":
    main()