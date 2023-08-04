import pygame
import sys
import os
from settings import *
from player import Player, Tile, AnimationPlayer, Player2,  Enemy
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from weapon import Weapon,UI
from sky import Rain, Sky
from random import randint
from menu import Menu, Pause,Pause1, Upgrade, MagicPlayer
from random import choice
from timer import Timer

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()  # mô tả bề mặt hiển thị, có thể vẽ lên

        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.visible_sprites = YSortCameraGroup()
        self.attackable_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.map1 = False
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        self.sky = Sky()
        # shop
        self.menu = Menu(self.player, self.toggle_shop)
        self.pause = Pause(self.player, self.toggle_pause)
        self.music_enabled = self.pause.music_enabled
        self.shop_active = False
        self.game_paused = False
        self.game_paused1 = True
        self.menu_paused = False
        # music
        self.success = pygame.mixer.Sound('audio/success.wav')
        self.success.set_volume(0.3)
        self.music = pygame.mixer.Sound('audio/music.mp3')
        self.music.set_volume(0.1)
        self.music.play(loops=-1)
        self.music_playing = True
        self.animation_player = AnimationPlayer()
        #attack
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
        self.ui = UI()

    def setup(self):

        tmx_data = load_pygame('data/map.tmx')

        # house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
        # fence hang rao
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

        # water
        water_frames = import_folder('graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                name=obj.name,
                player_add=self.player_add)

        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
        # collion tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction=self.interaction_sprites,
                    soil_layer=self.soil_layer,
                    toggle_shop=self.toggle_shop,
                    toggle_pause=self.toggle_pause)
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
        Generic(
            pos=(0, 0),
            surf=pygame.image.load('graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground'])

    def create_map(self):
        layouts = {
            'boundary': import_csv_layout(
                'map2/map/map_FloorBlocks.csv'),
            'grass': import_csv_layout(
                'map2/map/map_Grass.csv'),
            'object': import_csv_layout(
                'map2/map/map_Objects.csv'),
            'entities': import_csv_layout(
                'map2/map/map_Entities.csv')
        }
        graphics = {
            'grass': import_folder('map2/graphics/Grass'),
            'objects': import_folder(
                'map2/graphics/objects')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), [self.collision_sprites], 'invisible', z=LAYERS['map2'])
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile(
                                (x, y),
                                [self.visible_sprites, self.collision_sprites, self.attackable_sprites],
                                'grass',
                                random_grass_image,
                                z=LAYERS['map2'])

                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.collision_sprites], 'object', surf,
                                 z=LAYERS['map2'])
                        if style == 'entities':
                            if col == '394':
                                self.player2 = Player2(
                                    (x, y),
                                    self.visible_sprites,
                                    self.collision_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic,
                                    self.toggle_pause1,
                                    self.toggle_menu)

                            else:
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.visible_sprites, self.attackable_sprites],
                                    self.collision_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp,
                                    z=LAYERS['map2'])
    def change(self):

        for sprite in self.all_sprites.sprites():
            sprite.kill()

        for sprite in self.collision_sprites.sprites():
            sprite.kill()

        for sprite in self.tree_sprites.sprites():
            sprite.kill()

        for sprite in self.interaction_sprites.sprites():
            sprite.kill()
        tmx_data = None
        # if os.path.exists('data/map.tmx'):
        #     os.remove('data/map.tmx')
        self.player2_created = False
        self.create_map()
        self.upgrade = Upgrade(self.player2,self.toggle_menu)
        self.pause1 = Pause1(self.player2,self.toggle_pause1, self.music_enabled)
        self.music_enabled1 = self.pause1.music_enabled

    def create_attack(self):

        self.current_attack = Weapon(self.player2, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player2, strength, cost, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player2, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player2, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        if self.player2.vulnerable:
            self.player2.health -= amount
            self.player2.vulnerable = False
            self.player2.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player2.rect.center, [self.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):

        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    def add_exp(self, amount):

        self.player2.exp += amount

    def player_add(self, item):

        self.player.item_inventory[item] += 1
        self.success.play()

    def toggle_shop(self):

        self.shop_active = not self.shop_active
    def toggle_menu(self):
        self.menu_paused = not self.menu_paused
    def toggle_pause(self):
        self.game_paused = not self.game_paused

    def toggle_pause1(self):
        self.game_paused1 = not self.game_paused1

    def reset(self):
        # plant
        self.soil_layer.update_plant()

        # soil
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()
        # apples on the trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # sky
        self.sky.start_color = [255, 255, 255]

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    plant.kill()

    def run(self, dt):

        self.music_enabled = self.pause.music_enabled
        # drawing logic
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        # update
        if self.shop_active:
            self.menu.update()
        elif self.game_paused:
            self.pause.update()
            if self.pause.change_map:
                self.map1 = True
                self.pause.change_map = False
                if not self.printed_change_map:
                    print(self.pause.change_map)
                    self.printed_change_map = True
                    self.change()
                self.toggle_pause()

            else:
                self.pause.change_map = False
                self.printed_change_map = False

        else:
            self.all_sprites.update(dt)
            self.plant_collision()

        # weather
        self.overlay.display()

        # rain
        if self.raining and (not self.shop_active) and (not self.game_paused):
            self.rain.update()

        # daytime
        self.sky.display(dt)

        # transition overlay
        if self.player.sleep:
            self.transition.play()

        if self.music_enabled and not self.music_playing:  # Kiểm tra trạng thái và trạng thái phát nhạc
            self.music.play(loops=-1)
            self.music_playing = True
        elif not self.music_enabled and self.music_playing:
            self.music.stop()
            self.music_playing = False

        if self.map1:
            self.music_enabled1 = self.pause1.music_enabled
            self.visible_sprites.custom_draw(self.player2)
            self.ui.display(self.player2)
            if self.game_paused1:
                self.pause1.update()
            elif self.menu_paused:
                self.upgrade.display()
            else:
                self.visible_sprites.update(dt)
                self.visible_sprites.enemy_update(self.player2)
                self.player_attack_logic()
            if self.music_enabled1 and not self.music_playing:  # Kiểm tra trạng thái và trạng thái phát nhạc
                    self.music.play(loops=-1)
                    self.music_playing = True
            elif not self.music_enabled1 and self.music_playing:
                    self.music.stop()
                    self.music_playing = False
                # pass





class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    # thiết lập camera theo nhân vật
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.z = LAYERS['ground']
        # creating the floor
        self.floor_surf = pygame.image.load(
            'map2/graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):

        # getting the offset
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_pos = sprite.rect.topleft - self.offset
                    self.display_surface.blit(sprite.image, offset_pos)


    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if
                         hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)


