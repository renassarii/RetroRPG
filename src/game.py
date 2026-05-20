"""Top-level Game window. Owns state and delegates rendering and rules to
the dedicated modules under src.systems and src.ui.
"""

import random

import arcade

from src.config import BASE_URL, HEIGHT, PLAYER_SPEED, WIDTH, WINDOW_TITLE
from src.data.dialogues import DIALOGUES, STORY_SEQUENCE
from src.data.enemies import (
    ENEMIES,
    ENEMY_TEXTURE_PATHS,
    INITIAL_ENEMY_SPAWNS,
)
from src.data.items import (
    BATTLE_MENU,
    INITIAL_INVENTORY,
    ITEM_NAMES,
    ITEM_TEXTURE_PATHS,
    LEVEL_UP_OPTIONS,
    LEVEL_UP_TEXTURE_PATHS,
    MAGIC_NAMES,
    MAGIC_TEXTURE_PATHS,
)
from src.systems import battle, world
from src.systems.progression import apply_level_choice
from src.ui.scenes import draw_scene
from src.utils.textures import load_texture_from_url


PLAYER_SPAWN = (200, 320)
ENEMY_BATTLE_POS = (600, 320)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, WINDOW_TITLE, fullscreen=True)
        self.set_fullscreen(True)

        self._init_state()
        self._load_textures()
        self._init_world()
        self._init_sprites()
        self._init_player_stats()
        self._init_menu_state()

        self.keys_held = set()

    def _init_state(self):
        self.state = "explore"
        self.dialog_index = 0
        self.after_battle = False
        self.current_dialog_id = 1
        self.story_step = 0
        self.message = ""
        self.message_timer = 0
        self.post_battle_xp = None

    def _load_textures(self):
        self.background1 = load_texture_from_url(
            BASE_URL + "assets/images/backgrounds/hintergrund.png"
        )
        self.gameover = load_texture_from_url(
            BASE_URL + "assets/images/backgrounds/gameover.png"
        )
        self.level_ui_bg = self.background1

        self.item_textures = {
            name: load_texture_from_url(BASE_URL + path)
            for name, path in ITEM_TEXTURE_PATHS.items()
        }
        self.magic_textures = {
            name: load_texture_from_url(BASE_URL + path)
            for name, path in MAGIC_TEXTURE_PATHS.items()
        }
        self.level_icons = {
            name: load_texture_from_url(BASE_URL + path)
            for name, path in LEVEL_UP_TEXTURE_PATHS.items()
        }
        self.enemy_textures = {
            name: load_texture_from_url(BASE_URL + path)
            for name, path in ENEMY_TEXTURE_PATHS.items()
        }

        self._player_texture = load_texture_from_url(
            BASE_URL + "assets/images/characters/gandalf.png"
        )

    def _init_world(self):
        self.map_img, self.map_pixels = world.load_map(self.width, self.height)

    def _init_sprites(self):
        self.player = arcade.Sprite(self._player_texture, 2.5)
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        for name, x, y in INITIAL_ENEMY_SPAWNS:
            self.spawn_enemy(name, x, y)

        self.player_list.append(self.player)

        self.enemy = None
        self.current_enemy = None
        self.set_spawn_points()

    def _init_player_stats(self):
        self.player_hp = 100
        self.max_hp = 100
        self.bp = 20
        self.max_bp = 20
        self.player_xp = 0
        self.player_max_xp = 100
        self.level = 1

        self.player_buff_spell = False
        self.player_debuff_spell = False
        self.enemy_hp = 100
        self.enemy_max_hp = 100
        self.enemy_luck = 0
        self.enemy_defense = False

        self.enemy_turn = False
        self.enemy_timer = 0
        self.player_turn = True

    def _init_menu_state(self):
        self.selected = 0
        self.selected_2 = 0
        self.selected_3 = 0
        self.selected_4 = 0

        self.inventory = dict(INITIAL_INVENTORY)

        self.magic_scroll = 0
        self.visible_magic = 3
        self.item_scroll = 0
        self.visible_item = 3

    def spawn_enemy(self, name, x, y):
        enemy = arcade.Sprite()
        enemy.texture = self.enemy_textures[name]
        enemy.scale = 2.5
        enemy.center_x = x
        enemy.center_y = y
        enemy.name = name
        self.enemy_list.append(enemy)
        return enemy

    def get_enemy_sprite(self, name):
        for e in self.enemy_list:
            if getattr(e, "name", None) == name:
                return e
        return None

    def set_spawn_points(self):
        self.player.center_x, self.player.center_y = PLAYER_SPAWN

    def start_battle_positions(self):
        self.player.center_x, self.player.center_y = PLAYER_SPAWN
        if self.enemy is not None:
            self.enemy.center_x, self.enemy.center_y = ENEMY_BATTLE_POS

    def on_draw(self):
        self.clear()
        draw_scene(self)

    def on_update(self, delta_time):
        if self.state == "battle" and self.enemy_turn:
            self.enemy_timer -= delta_time
            if self.enemy_timer <= 0:
                battle.perform_enemy_turn(self)
            return

        if self.state == "explore":
            self._update_explore(delta_time)

    def _update_explore(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = ""

        speed = PLAYER_SPEED
        if world.is_water(
            self.map_img, self.map_pixels,
            self.player.center_x, self.player.center_y,
        ):
            speed = PLAYER_SPEED * 0.5

        dx = dy = 0
        if arcade.key.W in self.keys_held:
            dy += speed
        if arcade.key.S in self.keys_held:
            dy -= speed
        if arcade.key.A in self.keys_held:
            dx -= speed
        if arcade.key.D in self.keys_held:
            dx += speed

        new_x = self.player.center_x + dx
        new_y = self.player.center_y + dy

        if world.water_depth(self.map_img, self.map_pixels, new_x, new_y) > 40:
            return

        if not world.is_blocked(
            self.map_img, self.map_pixels, new_x, self.player.center_y
        ):
            self.player.center_x = new_x

        if not world.is_blocked(
            self.map_img, self.map_pixels, self.player.center_x, new_y
        ):
            self.player.center_y = new_y

    def on_key_press(self, key, modifiers):
        self.keys_held.add(key)

        if self.state == "level_up" and key == arcade.key.SPACE:
            self.state = "level_choice"
            return

        if self.state == "level_choice":
            self._handle_level_choice_input(key)

        if self.state == "explore" and key == arcade.key.E:
            self._try_interact()
            return

        if self.state == "dialog" and key == arcade.key.SPACE:
            self._advance_dialog()
            return

        if self.state == "battle":
            self._handle_battle_input(key)
            return

        if self.state == "post_battle" and key == arcade.key.SPACE:
            self._dismiss_post_battle()
            return

    def on_key_release(self, key, modifiers):
        self.keys_held.discard(key)

    def _handle_level_choice_input(self, key):
        if key == arcade.key.LEFT:
            self.selected_4 = (self.selected_4 - 1) % len(LEVEL_UP_OPTIONS)
        if key == arcade.key.RIGHT:
            self.selected_4 = (self.selected_4 + 1) % len(LEVEL_UP_OPTIONS)
        if key == arcade.key.SPACE:
            apply_level_choice(self)

    def _try_interact(self):
        for enemy in self.enemy_list:
            dist = arcade.get_distance_between_sprites(self.player, enemy)
            if dist >= 80:
                continue

            self.enemy = enemy
            self.current_enemy = enemy.name

            enemy_data = ENEMIES[self.current_enemy]
            self.enemy_hp = enemy_data["hp"]
            self.enemy_max_hp = enemy_data["hp"]

            if self.current_enemy == "Köpek Franz":
                self.state = "dialog"
                self.dialog_index = 0
                self.current_dialog_id = 1
            else:
                self.state = "battle"
                self.start_battle_positions()
                self._roll_first_turn()
            return

    def _roll_first_turn(self):
        if random.random() < 0.5:
            self.player_turn = True
            self.enemy_turn = False
            self.message = "You start!"
        else:
            self.player_turn = False
            self.enemy_turn = True
            self.enemy_timer = 0.5
            self.message = "Enemy starts!"

    def _advance_dialog(self):
        self.dialog_index += 1
        lines = DIALOGUES[self.current_dialog_id]["lines"]
        if self.dialog_index < len(lines):
            return

        self.dialog_index = 0

        if self.after_battle:
            if self.player_xp >= self.player_max_xp:
                self.player_xp = 0
                self.player_max_xp += 50
                self.current_dialog_id = 10
                self.dialog_index = 0
                self.state = "dialog"
                self.after_battle = False
            else:
                self.enemy.kill()
                self.state = "explore"
                self.after_battle = False
            return

        self.story_step += 1
        if 1 <= self.story_step <= len(STORY_SEQUENCE):
            self.current_dialog_id = STORY_SEQUENCE[self.story_step - 1]
            return

        self.current_enemy = "Köpek Franz"
        self.enemy = self.get_enemy_sprite(self.current_enemy)

        enemy_data = ENEMIES[self.current_enemy]
        self.enemy_hp = enemy_data["hp"]
        self.enemy_max_hp = enemy_data["hp"]

        self.state = "battle"
        self.start_battle_positions()
        self._roll_first_turn()

    def _handle_battle_input(self, key):
        if key == arcade.key.J:
            self.selected = (self.selected - 1) % len(BATTLE_MENU)
            return
        if key == arcade.key.L:
            self.selected = (self.selected + 1) % len(BATTLE_MENU)
            return
        if key == arcade.key.SPACE and self.player_turn:
            battle.perform_player_action(self)
            self.player_turn = False
            self.enemy_turn = True
            self.enemy_timer = 0.5
            return

        action = BATTLE_MENU[self.selected]
        if action == "Item":
            self._scroll_submenu(
                key,
                attr_selected="selected_2",
                attr_scroll="item_scroll",
                visible="visible_item",
                length=len(ITEM_NAMES),
            )
        elif action == "Magic":
            self._scroll_submenu(
                key,
                attr_selected="selected_3",
                attr_scroll="magic_scroll",
                visible="visible_magic",
                length=len(MAGIC_NAMES),
            )

    def _scroll_submenu(self, key, attr_selected, attr_scroll, visible, length):
        selected = getattr(self, attr_selected)
        scroll = getattr(self, attr_scroll)
        visible_count = getattr(self, visible)

        if key == arcade.key.I and selected > 0:
            selected -= 1
            if selected < scroll:
                scroll = selected
        elif key == arcade.key.K and selected < length - 1:
            selected += 1
            if selected >= scroll + visible_count:
                scroll = selected - visible_count + 1
        else:
            return

        setattr(self, attr_selected, selected)
        setattr(self, attr_scroll, scroll)

    def _dismiss_post_battle(self):
        if self.player_xp >= self.player_max_xp:
            self.player_xp = 0
            self.player_max_xp += 50
            self.level += 1
            self.state = "level_choice"
            self.selected_4 = 0
            self.post_battle_xp = None
            return

        try:
            self.enemy.kill()
        except Exception:
            pass
        self.state = "explore"
        self.after_battle = False
        self.post_battle_xp = None
