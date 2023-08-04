import pygame
import sys
from settings import *
from level import *
from player import *
import json
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Sprout Land')
        icon = pygame.image.load('icon.png')
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.menu_active = True

    def draw_menu(self):
        # Vẽ hình nền menu
        menu_background = pygame.image.load('background.png')
        menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(menu_background, (0, 0))


        option_font = pygame.font.Font('font/LycheeSoda.ttf', 64)
        play_text = option_font.render('Play', True, MENU_OPTION_COLOR)
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(play_text, play_rect)
        quit_text = option_font.render('Quit', True, MENU_OPTION_COLOR)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quit_text, quit_rect)

        # Kiểm tra lựa chọn người chơi
        mouse_pos = pygame.mouse.get_pos()
        if play_rect.collidepoint(mouse_pos):
            play_text = option_font.render('Play', True, MENU_OPTION_HOVER_COLOR)
            self.screen.blit(play_text, play_rect)
            if pygame.mouse.get_pressed()[0]:
                self.menu_active = False
        elif quit_rect.collidepoint(mouse_pos):
            quit_text = option_font.render('Quit', True, MENU_OPTION_HOVER_COLOR)
            self.screen.blit(quit_text, quit_rect)
            if pygame.mouse.get_pressed()[0]:
                pygame.quit()
                sys.exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick(FPS) / 1000

            if self.menu_active:
                self.draw_menu()
            else:
                self.level.run(dt)

            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
