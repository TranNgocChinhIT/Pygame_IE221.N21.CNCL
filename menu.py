import pygame
import sys
from settings import *
from timer import Timer
from random import randint


class Menu:
    def __init__(self, player, toggle_shop):

        # genera setup
        self.player = player
        self.toggle_shop = toggle_shop
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)

        # options
        self.width = 400
        self.space = 10
        self.padding = 8

        # entries
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()
        # movement
        self.index = 0
        self.timer = Timer(200)

    def display_money(self):
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + self.padding * 2
        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

        # buy/ sell
        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_shop()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()
            if keys[pygame.K_SPACE]:
                self.timer.activate()

                # get item
                current_item = self.options[self.index]

                # sell
                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                # buy
                else:
                    seed_price = PURCHASE_PRICES[current_item]
                    if self.player.money >= seed_price:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= PURCHASE_PRICES[current_item]

        # clamo the values
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0

    def show_entry(self, text_surf, amount, top, selected):

        # background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + self.padding * 2)
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        # text
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        # amount
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        # selected
        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)
            if self.index > self.sell_border:  # sell
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:  # buy
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)

    def update(self):
        self.input()
        self.display_money()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)


class Pause:
    def __init__(self, player, toggle_pause, music_enabled=True):
        # General setup
        self.player = player
        self.toggle_pause = toggle_pause
        self.change_map = False
        self.music_enabled = music_enabled
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)
        self.mouse_clicked = False

    def update(self):
        # Display pause menu
        menu_width = 400
        menu_height = 250
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        menu_surface = pygame.Surface((menu_width, menu_height))
        background_color = (221, 196, 136)
        border_color = (165, 140, 82)
        line_color = (165, 140, 82)

        # Fill màu nền cho khung menu nhỏ
        menu_surface.fill(background_color)

        # Vẽ viền cho khung menu
        pygame.draw.rect(menu_surface, border_color, menu_surface.get_rect(), 3)

        # Hiển thị khung menu nhỏ tại vị trí tính toán
        self.display_surface.blit(menu_surface, (menu_x, menu_y))

        # Render menu options
        option_font = pygame.font.Font('font/LycheeSoda.ttf', 36)

        # Render tiêu đề menu
        title_font = pygame.font.Font('font/LycheeSoda.ttf', 48)
        title_text = title_font.render('Option', True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 40))
        self.display_surface.blit(title_text, title_rect)

        # Vẽ các ô lựa chọn
        option_width = 20
        option_height = 20
        option_x = menu_x + 20
        option_y = menu_y + 90

        pygame.draw.rect(menu_surface, border_color, (option_x, option_y, option_width, option_height),
                         2)  # Ô lựa chọn 1
        pygame.draw.rect(menu_surface, border_color, (option_x, option_y + 40, option_width, option_height),
                         2)  # Ô lựa chọn 2
        pygame.draw.rect(menu_surface, border_color, (option_x, option_y + 80, option_width, option_height),
                         2)  # Ô lựa chọn 3
        pygame.draw.rect(menu_surface, border_color, (option_x, option_y + 120, option_width, option_height),
                         2)  # Ô lựa chọn 4

        pause_text = option_font.render('Resume', True, (255, 255, 255))
        pause_rect = pause_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))  # Giảm vị trí theo chiều cao mới
        self.display_surface.blit(pause_text, pause_rect)

        map_text = option_font.render('Choose Map', True, (255, 255, 255))
        map_rect = map_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.display_surface.blit(map_text, map_rect)

        music_text = option_font.render('Music: On', True,
                                        (255, 255, 255)) if self.music_enabled else option_font.render(
            'Music: Off', True, (255, 255, 255))
        music_rect = music_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.display_surface.blit(music_text, music_rect)

        quit_text = option_font.render('Quit Game', True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.display_surface.blit(quit_text, quit_rect)

        # Check for menu option selection
        mouse_pos = pygame.mouse.get_pos()
        if pause_rect.collidepoint(mouse_pos):
            pause_text = option_font.render('Resume', True, (138, 43, 226))
            self.display_surface.blit(pause_text, pause_rect)
            if pygame.mouse.get_pressed()[0]:
                self.toggle_pause()
        elif map_rect.collidepoint(mouse_pos):
            map_text = option_font.render('Choose Map', True, (138, 43, 226))
            self.display_surface.blit(map_text, map_rect)
            if pygame.mouse.get_pressed()[0]:
                self.change_map = True

        elif music_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] and not self.mouse_clicked:
                self.mouse_clicked = True
                self.music_enabled = not self.music_enabled
            music_text = option_font.render('Music: On', True,
                                            (138, 43, 226)) if self.music_enabled else option_font.render('Music: Off',
                                                                                                          True,
                                                                                                          (
                                                                                                          138, 43, 226))
            self.display_surface.blit(music_text, music_rect)
        elif quit_rect.collidepoint(mouse_pos):
            quit_text = option_font.render('Quit Game', True, (138, 43, 226))
            self.display_surface.blit(quit_text, quit_rect)
            if pygame.mouse.get_pressed()[0]:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.toggle_pause()
        if not pygame.mouse.get_pressed()[0]:
            self.mouse_clicked = False


class Pause1:
    def __init__(self, player,toggle_pause1, music_enabled):
        # General setup
        self.player = player
        self.toggle_pause1 = toggle_pause1
        self.music_enabled = music_enabled
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)
        self.mouse_clicked = False

    def update(self):
        # Display pause menu
        menu_width = 400
        menu_height = 200
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        menu_surface = pygame.Surface((menu_width, menu_height))
        background_color = (221, 196, 136)
        border_color = (165, 140, 82)

        # Fill màu nền cho khung menu nhỏ
        menu_surface.fill(background_color)

        # Vẽ viền cho khung menu
        pygame.draw.rect(menu_surface, border_color, menu_surface.get_rect(), 3)

        # Hiển thị khung menu nhỏ tại vị trí tính toán
        self.display_surface.blit(menu_surface, (menu_x, menu_y))

        # Render menu options
        option_font = pygame.font.Font('font/LycheeSoda.ttf', 36)

        # Render tiêu đề menu
        title_font = pygame.font.Font('font/LycheeSoda.ttf', 48)
        title_text = title_font.render('Option', True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 40))
        self.display_surface.blit(title_text, title_rect)

        # Vẽ các ô lựa chọn
        option_x = menu_x + 20
        option_y = menu_y + 90

        music_text = option_font.render('Music: On', True,
                                        (255, 255, 255)) if self.music_enabled else option_font.render(
            'Music: Off', True, (255, 255, 255))
        music_rect = music_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.display_surface.blit(music_text, music_rect)

        quit_text = option_font.render('Quit Game', True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.display_surface.blit(quit_text, quit_rect)

        # Check for menu option selection
        mouse_pos = pygame.mouse.get_pos()
        if music_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] and not self.mouse_clicked:
                self.mouse_clicked = True
                self.music_enabled = not self.music_enabled
            music_text = option_font.render('Music: On', True,
                                            (138, 43, 226)) if self.music_enabled else option_font.render('Music: Off',
                                                                                                          True,
                                                                                                          (
                                                                                                              138, 43,
                                                                                                              226))
            self.display_surface.blit(music_text, music_rect)
        elif quit_rect.collidepoint(mouse_pos):
            quit_text = option_font.render('Quit Game', True, (138, 43, 226))
            self.display_surface.blit(quit_text, quit_rect)
            if pygame.mouse.get_pressed()[0]:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.toggle_pause1()
        if not pygame.mouse.get_pressed()[0]:
            self.mouse_clicked = False




class Upgrade:
    def __init__(self, player, toggle_menu):

        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_nr = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # item creation
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // 6
        self.create_items()
        self.toggle_menu = toggle_menu
        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True
        self.z = LAYERS['menu']

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()
        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].trigger(self.player)

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 300:
                self.can_move = True

    def create_items(self):
        self.item_list = []

        for item, index in enumerate(range(self.attribute_nr)):
            # horizontal position
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attribute_nr
            left = (item * increment) + (increment - self.width) // 2

            # vertical position
            top = self.display_surface.get_size()[1] * 0.1

            # create the object
            item = Item(left, top, self.width, self.height, index, self.font)
            self.item_list.append(item)

    def display(self):
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            # get attributes
            name = self.attribute_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)
            item.display(self.display_surface, self.selection_index, name, value, max_value, cost)


class Item:
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font

    def display_names(self, surface, name, cost, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        # title
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        # cost
        cost_surf = self.font.render(f'{int(cost)}', False, color)
        cost_rect = cost_surf.get_rect(midbottom=self.rect.midbottom - pygame.math.Vector2(0, 20))

        # draw
        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)

    def display_bar(self, surface, value, max_value, selected):

        # drawing setup
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        # bar setup
        full_height = bottom[1] - top[1]
        relative_number = (value / max_value) * full_height
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_number, 30, 10)

        # draw elements
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def trigger(self, player):
        upgrade_attribute = list(player.stats.keys())[self.index]

        if player.exp >= player.upgrade_cost[upgrade_attribute] and player.stats[upgrade_attribute] < player.max_stats[
            upgrade_attribute]:
            player.exp -= player.upgrade_cost[upgrade_attribute]
            player.stats[upgrade_attribute] *= 1.2
            player.upgrade_cost[upgrade_attribute] *= 1.4

        if player.stats[upgrade_attribute] > player.max_stats[upgrade_attribute]:
            player.stats[upgrade_attribute] = player.max_stats[upgrade_attribute]

    def display(self, surface, selection_num, name, value, max_value, cost):
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, value, max_value, self.index == selection_num)


class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player
        self.sounds = {
            'heal': pygame.mixer.Sound('map2/audio/heal.wav'),
            'flame': pygame.mixer.Sound('map2/audio/Fire.wav')
        }

    def heal(self, player, strength, cost, groups):
        if player.energy >= cost:
            self.sounds['heal'].play()
            player.health += strength
            player.energy -= cost
            if player.health >= player.stats['health']:
                player.health = player.stats['health']
            self.animation_player.create_particles('aura', player.rect.center, groups)
            self.animation_player.create_particles('heal', player.rect.center, groups)

    def flame(self, player, cost, groups):
        if player.energy >= cost:
            player.energy -= cost
            self.sounds['flame'].play()

            if player.status.split('_')[0] == 'right':
                direction = pygame.math.Vector2(1, 0)
            elif player.status.split('_')[0] == 'left':
                direction = pygame.math.Vector2(-1, 0)
            elif player.status.split('_')[0] == 'up':
                direction = pygame.math.Vector2(0, -1)
            else:
                direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x:  # horizontal
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), groups)
                else:  # vertical
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), groups)
