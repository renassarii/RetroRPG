import arcade
import random
import requests
from io import BytesIO
from PIL import Image

WIDTH = 800
HEIGHT = 450

PLAYER_SPEED = 3

url = "https://raw.githubusercontent.com/renassarii/RetroRPG/main/"

# =========================
# DIALOG
# =========================
dialogues = {
    1: {
        "name": "Franz",
        "lines":[
            "wtf how did you get here?",
            "isn't the harbor closed?",
            "you shouldn't be here do you know what type of things live here?",
            "do you even know how to use magic?",
        ]
    },
    2: {
        "name": "Luka",
        "lines":[
            "who tf are you and why can a dog speak to me?"
        ]
    },
    3:{
        "name": "Franz",
        "lines":[
            "I am no dog bitch",
            "And answer my fucking question"
        ]
    },
    4:{
        "name": "Luka",
        "lines":[
            "Don't lie to me there is no something like magic"
        ]
    },
    5:{
        "name": "Franz",
        "lines":[
            "okay your fucked"
        ]
    },
    6:{
        "name": "Franz",
        "lines":[
            "Look I will only explain this once",
            "You have Punch that's the most basic attack you just go up to him and smack him",
            "You can use Magic you just channel your Mana(Bp) and just release a spell you only have one right now",
            "You can get Items on this Island i will give you 5 Heal and Mana potions",
            "At last the pussy move is running away with Escape.",
            "Now fight me"
        ]
    }
}


def load_texture_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return arcade.Texture(name=url, image=img)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "RPG SYSTEM", fullscreen=True)
        self.set_fullscreen(True)

        # =========================
        # STATE
        # =========================
        self.state = "explore"
        self.dialog_index = 0

        # =========================
        # LOADING PICS
        # =========================
        player_texture = load_texture_from_url(url + "assets/images/characters/gandalf.png")
        enemy_texture = load_texture_from_url(url + "assets/images/characters/Franz.png")

        self.background1 = load_texture_from_url(url + "assets/images/backgrounds/hintergrund.png")
        self.gameover = load_texture_from_url(url + "assets/images/backgrounds/gameover.png")

        # =========================
        # ITEM TEST
        # =========================
        self.item_icons = {
            "Mana potion": url + "assets/images/characters/Franz.png",
            "Health potion": url + "assets/images/characters/gandalf.png"
        }

        # =========================
        # SPRITES
        # =========================
        self.player = arcade.Sprite(player_texture, 2)
        self.enemy = arcade.Sprite(enemy_texture, 2)

        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.enemy_list.append(self.enemy)

        # =========================
        # HP
        # =========================
        self.player_hp = 100
        self.enemy_hp = 100
        self.max_hp = 100

        self.bp = 20
        self.max_bp = 20

        self.set_spawn_points()

        # dialog control
        self.current_dialog_id = 1
        self.story_step = 0

        # =========================
        # MENU
        # =========================
        self.menu = ["Punch", "Magic", "Item", "Escape"]
        self.selected = 0
        self.menu_2 = ["Mana potion", "Health potion"]
        self.selected_2 = 0
        self.message = ""

        # =========================
        # ITEM TEXTURES
        # =========================
        self.item_textures = {}
        for item, img_url in self.item_icons.items():
            self.item_textures[item] = load_texture_from_url(img_url)

        self.keys_held = set()

    def do_action(self):
        action = self.menu[self.selected]

        if action == "Punch":
            self.enemy_hp -= 15
            self.message = "⚔ 15"

        elif action == "Magic":
            if self.bp >= 3:
                self.bp -= 3
                self.enemy_hp -= 15
                self.message = "✨ 15"
            else:
                self.message = "Not enough BP"

        elif action == "Item":
            item = self.menu_2[self.selected_2]

            if item == "Health potion":
                self.player_hp = min(self.max_hp, self.player_hp + 20)
                self.message = "+20 HP"

            elif item == "Mana potion":
                self.bp = min(self.max_bp, self.bp + 20)
                self.message = "+20 BP"

        elif action == "Escape":
            if random.random() > 0.5:
                self.state = "explore"
                self.message = "Ran away!"

        if self.enemy_hp > 0:
            self.player_hp -=10

        if self.enemy_hp <= 0:
            self.state = "explore"
            self.enemy.kill()
        if self.player_hp <= 0:
            self.state = "gameover"


    def set_spawn_points(self):
        self.player.center_x = 200
        self.player.center_y = 320
        self.enemy.center_x = 600
        self.enemy.center_y = 320

    def start_battle_positions(self):
        self.player.center_x = 200
        self.player.center_y = 320
        self.enemy.center_x = 600
        self.enemy.center_y = 320

    # =========================
    # DRAW
    # =========================
    def on_draw(self):
        self.clear()
        if self.state == "gameover":
            arcade.draw_texture_rect(
                self.gameover,
                arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
            )
            arcade.draw_text("Drücke R zum Neustart",
                             self.width / 2, 80,
                             arcade.color.WHITE, 20,
                             anchor_x="center")
            return

        arcade.draw_texture_rect(
            self.background1,
            arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        )

        arcade.draw_texture_rect(
            self.background1,
            arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        )

        if self.state == "explore":
            self.player_list.draw()
            self.enemy_list.draw()
            return


        if self.state == "dialog":
            self.player_list.draw()
            self.enemy_list.draw()

            arcade.draw_rect_filled(
                arcade.rect.XYWH(400, 80, 3000, 140),
                arcade.color.BLACK
            )


            # ✅ FIXED DIALOG ACCESS
            arcade.draw_text(
                dialogues[self.current_dialog_id]["name"],
                40,
                100,
                arcade.color.WHITE,
                18
            )

            arcade.draw_text(
                dialogues[self.current_dialog_id]["lines"][self.dialog_index],
                120,
                70,
                arcade.color.WHITE,
                18
            )
            return

        # =========================
        # BATTLE MODE
        # =========================
        self.player_list.draw()
        self.enemy_list.draw()

        self.draw_hp_bar(200, 410, self.player_hp, arcade.color.GREEN)
        self.draw_hp_bar(600, 410, self.enemy_hp, arcade.color.RED)
        self.draw_bp_bar(200, 395, self.bp, arcade.color.CYAN)

        arcade.draw_text("Gypsy Luka", 170, 430, arcade.color.WHITE, 14)
        arcade.draw_text("FRANZ", 570, 430, arcade.color.WHITE, 14)

        arcade.draw_rect_filled(
            arcade.rect.XYWH(400, 80, 760, 140),
            arcade.color.BLACK
        )

        x = 200
        for i, item in enumerate(self.menu):
            color = arcade.color.YELLOW if i == self.selected else arcade.color.WHITE
            arcade.draw_text(item, x + i * 150, 70, color, 18)

        arcade.draw_text(self.message, 250, 20, arcade.color.WHITE, 14)

        if self.menu[self.selected] == "Item":

            popup_x = 450
            popup_y = 200

            arcade.draw_rect_filled(
                arcade.rect.XYWH(popup_x, popup_y, 300, 160),
                arcade.color.BLACK
            )

            for i, item in enumerate(self.menu_2):
                y = popup_y + 40 - i * 60

                texture = self.item_textures[item]

                arcade.draw_texture_rect(
                    texture,
                    arcade.rect.XYWH(popup_x - 80, y, 40, 40)
                )

                color = arcade.color.YELLOW if i == self.selected_2 else arcade.color.WHITE
                arcade.draw_text(item, popup_x - 20, y - 10, color, 14)

    # =========================
    # HP BAR
    # =========================
    def draw_hp_bar(self, x, y, hp, color):
        width = 160
        height = 12

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, width, height),
            arcade.color.DARK_RED
        )

        fill = max(0, (hp / self.max_hp) * width)

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x - (width - fill) / 2, y, fill, height),
            color
        )

    def draw_bp_bar(self, x, y, bp, color):
        width = 160
        height = 12

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, width, height),
            arcade.color.DARK_BLUE
        )

        fill = (bp / self.max_bp) * width

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x - (width - fill) / 2, y, fill, height),
            color
        )

    def on_update(self, delta_time):
        if self.state != "explore":
            return

        if arcade.key.W in self.keys_held:
            self.player.center_y += PLAYER_SPEED
        if arcade.key.S in self.keys_held:
            self.player.center_y -= PLAYER_SPEED
        if arcade.key.A in self.keys_held:
            self.player.center_x -= PLAYER_SPEED
        if arcade.key.D in self.keys_held:
            self.player.center_x += PLAYER_SPEED

    def on_key_press(self, key, modifiers):
        self.keys_held.add(key)

        # enter dialogue
        if self.state == "explore" and key == arcade.key.E:
            if self.player.collides_with_sprite(self.enemy):
                self.state = "dialog"
                self.dialog_index = 0
                self.current_dialog_id = 1

        # dialog progression
        elif self.state == "dialog" and key == arcade.key.SPACE:
            self.dialog_index += 1

            if self.dialog_index >= len(dialogues[self.current_dialog_id]["lines"]):
                self.dialog_index = 0
                self.story_step += 1

                if self.story_step == 1:
                    self.current_dialog_id = 2
                elif self.story_step == 2:
                    self.current_dialog_id = 3
                elif self.story_step == 3:
                    self.current_dialog_id = 4
                elif self.story_step == 4:
                    self.current_dialog_id = 5
                elif self.story_step == 5:
                    self.current_dialog_id = 6
                else:
                    self.state = "battle"
                    self.start_battle_positions()
        elif self.state == "battle":

            if key == arcade.key.LEFT:
                self.selected = (self.selected - 1) % len(self.menu)

            if key == arcade.key.RIGHT:
                self.selected = (self.selected + 1) % len(self.menu)

            if key == arcade.key.UP:
                self.selected_2 = (self.selected_2 - 1) % len(self.menu_2)

            if key == arcade.key.DOWN:
                self.selected_2 = (self.selected_2 + 1) % len(self.menu_2)

            if key == arcade.key.SPACE :
                self.do_action()

    def on_key_release(self, key, modifiers):
        if key in self.keys_held:
            self.keys_held.remove(key)


if __name__ == "__main__":
    Game()
    arcade.run()