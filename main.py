import arcade
import random
import requests
from io import BytesIO
from PIL import Image

WIDTH = 800
HEIGHT = 450

PLAYER_SPEED = 2

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
    },
    7:{
        "name": "Franz",
        "lines":[
            "here take them"
        ]
    },
    8:{
        "name": "System",
        "lines":[
            "+5 small Health potions",
            "+5 small Mana potions"
        ]
    },
    9:{
        "name": "Franz",
        "lines":[
            "ähhh"
        ]
    },
    10:{
        "name": "System",
        "lines":[
            "Well done you did it a level up",
            "choose do you want to level up your hp or bp"
        ]
    },
    11:{
        "name": "System",
        "lines":[
            "go on with your advanture"
        ]
    },
    12:{
        "name": "System",
        "lines":[
            "brr"
        ]
    },

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
        self.after_battle = False

        # =========================
        # LOADING PICS
        # =========================
        player_texture = load_texture_from_url(url + "assets/images/characters/gandalf.png")
        enemy_texture = load_texture_from_url(url + "assets/images/characters/Franz.png")

        self.background1 = load_texture_from_url(url + "assets/images/backgrounds/hintergrund.png")
        self.gameover = load_texture_from_url(url + "assets/images/backgrounds/gameover.png")
        self.level_ui_bg = load_texture_from_url(url + "assets/images/backgrounds/hintergrund.png")





        self.setup_map()
        # =========================
        # ITEM TEST
        # =========================
        self.item_icons = {
            "small Mana potion": url + "assets/images/items/SmallManaPotion.png",
            "small Health potion": url + "assets/images/items/SmallHealPotion.png"
        }

        self.magic_icons = {
            "Fire Spell": url + "assets/images/level_up_symbols/Fire.png",
            "Ice Spell": url + "assets/images/characters/gandalf.png",
                            }
        self.level_icons = {
            "Hp": load_texture_from_url(url + "assets/images/level_up_symbols/heart.png"),
            "Bp": load_texture_from_url(url + "assets/images/level_up_symbols/ManaSymbol.png"),
        }




        # =========================
        # SPRITES
        # =========================
        self.player = arcade.Sprite(player_texture, 2.5)
        self.enemy = arcade.Sprite(enemy_texture, 2.5)

        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.enemy_list.append(self.enemy)

        self.message_timer = 0

        # =========================
        # HP
        # =========================
        self.player_hp = 100
        self.enemy_hp = 100
        self.max_hp = 100
        self.player_xp = 0
        self.player_max_xp = 100
        self.level = 1

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
        self.menu_2 = ["small Mana potion", "small Health potion"]
        self.selected_2 = 0
        self.inventory = {
            "small Mana potion": 5,
            "small Health potion": 5,
        }
        self.menu_3 = ["Fire Spell", "Ice Spell"]
        self.selected_3 = 0
        self.usage = {
            "Fire Spell":3,
            "Ice Spell":6,
        }
        self.menu_4 = ["Hp", "Bp"]
        self.selected_4 = 0
        self.message = ""


        # =========================
        # ITEM TEXTURES
        # =========================
        self.item_textures = {}
        for item, img_url in self.item_icons.items():
            self.item_textures[item] = load_texture_from_url(img_url)
        self.magic_textures = {}
        for magic, magic_url in self.magic_icons.items():
            self.magic_textures[magic] = load_texture_from_url(magic_url)
        self.keys_held = set()

    def do_action(self):
        action = self.menu[self.selected]

        if action == "Punch":
            self.enemy_hp -= 15
            self.message = "⚔ 15"

        elif action == "Magic":
            magic = self.menu_3[self.selected_3]

            if magic == "Fire Spell":
                if self.bp >= 3:
                    self.enemy_hp -= 10
                    self.bp -=3
                    self.message = "-10 damage"
                else:
                    self.message = "you don't have enough BP"


            elif magic == "Ice Spell":
                if self.bp >= 6:
                    self.enemy_hp -= 20
                    self.bp -=6
                    self.message = "-20 damage"
                else:
                    self.message = "you don't have enough BP"





        elif action == "Item":
            item = self.menu_2[self.selected_2]

            # ❗ prüfen ob vorhanden
            if self.inventory[item] > 0:

                if item == "small Health potion":
                    self.player_hp = min(self.max_hp, self.player_hp + 20)
                    self.message = "+20 HP"

                elif item == "small Mana potion":
                    self.bp = min(self.max_bp, self.bp + 20)
                    self.message = "+20 BP"

                #  reduzieren
                self.inventory[item] -= 1

            else:
                self.message = "No potions left"

        elif action == "Escape":
            if random.random() > 0.5:
                self.state = "explore"
                self.message = "Ran away!"

        if self.enemy_hp > 0:
            self.player_hp -=10

        if self.enemy_hp <= 0:
            self.after_battle = True
            self.player_xp += 100

            if self.player_xp >= self.player_max_xp:
                self.player_xp -= self.player_max_xp
                self.level += 1
                self.player_max_xp += 50

                self.state = "level_choice"
                self.selected_4 = 0
                return
            else:
                self.state = "dialog"
                self.current_dialog_id = 9
                self.dialog_index = 0


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

            if self.enemy:  # falls später mehrere Gegner / gelöscht
                dist = arcade.get_distance_between_sprites(self.player, self.enemy)

                if dist < 80:
                    # Kreis
                    arcade.draw_circle_filled(
                        self.enemy.center_x + 20,
                        self.enemy.center_y + 60,
                        9,
                        arcade.color.BLACK
                    )

                    # "E" Text
                    arcade.draw_text(
                        "E",
                        self.enemy.center_x + 20,
                        self.enemy.center_y + 55,
                        arcade.color.WHITE,
                        10,
                        anchor_x="center"
                    )
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
        if self.state == "battle":
            self.player_list.draw()
            self.enemy_list.draw()

            self.draw_hp_bar(200, 410, self.player_hp, arcade.color.GREEN)
            self.draw_hp_bar(600, 410, self.enemy_hp, arcade.color.RED)
            self.draw_bp_bar(200, 395, self.bp, arcade.color.CYAN)

            arcade.draw_text("Gypsy Luka", 170, 430, arcade.color.WHITE, 14)
            arcade.draw_text("Köpek Franz", 570, 430, arcade.color.WHITE, 14)

            arcade.draw_rect_filled(
                arcade.rect.XYWH(400, 80, 760, 140),
                arcade.color.BLACK
            )
            x = 200
            for i, magic in enumerate(self.menu):
                color = arcade.color.YELLOW if i == self.selected else arcade.color.WHITE
                arcade.draw_text(magic, x + i * 150, 70, color, 18)

            arcade.draw_text(self.message, 250, 20, arcade.color.WHITE, 14)

            if self.menu[self.selected] == "Magic":

                popup_x = 250
                popup_y = 200

                arcade.draw_rect_filled(
                    arcade.rect.XYWH(popup_x, popup_y, 300, 160),
                    arcade.color.BLACK
                )

                for i, magic in enumerate(self.menu_3):
                    y = popup_y + 40 - i * 60

                    texture = self.magic_textures[magic]

                    arcade.draw_texture_rect(texture, arcade.rect.XYWH(popup_x - 80, y, 40, 40))

                    color = arcade.color.YELLOW if i == self.selected_3 else arcade.color.WHITE

                    arcade.draw_text(f"{magic} -{self.usage[magic]} BP", popup_x - 20, y - 10, color, 14)

                    # 👉 SELECTION INDICATOR
                    if i == self.selected_3:
                        arcade.draw_text("▶", popup_x - 50, y - 15, arcade.color.RED, 18)
            arcade.draw_text(f"Level: {self.level}", 20, 430, arcade.color.WHITE, 14)

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

                    arcade.draw_texture_rect(texture, arcade.rect.XYWH(popup_x - 80, y, 40, 40))

                    if self.inventory[self.menu_2[self.selected_2]] == 0:
                        # Aktion blocken
                        return
                    else:
                        color = arcade.color.YELLOW if i == self.selected_2 else arcade.color.WHITE
                    count = self.inventory[item]
                    arcade.draw_text(f"{count}x {item} ", popup_x - 20, y - 10, color, 14)

                    if i == self.selected_2:
                        arcade.draw_text("▶", popup_x - 50, y - 15, arcade.color.RED, 18)
            return

        if self.state == "level_choice":
            arcade.draw_texture_rect(
                self.level_ui_bg,
                arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
            )

            arcade.draw_text(
                "LEVEL UP! Pick your upgrade bitch",
                self.width / 2,
                380,
                arcade.color.WHITE,
                24,
                anchor_x="center"
            )
            options = self.menu_4

            for i, option in enumerate(options):
                x = 600 + i * 300
                y = 200

                # Box
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(x, y, 200, 180),
                    arcade.color.BLACK
                )

                # Icon
                arcade.draw_texture_rect(
                    self.level_icons[option],
                    arcade.rect.XYWH(x, y + 40, 80, 80)
                )

                # Text
                arcade.draw_text(
                    option,
                    x,
                    y - 50,
                    arcade.color.WHITE,
                    18,
                    anchor_x="center"
                )

                # Auswahlmarker
                if self.selected_4 == i:
                    arcade.draw_text(
                        "▶",
                        x - 80,
                        y - 10,
                        arcade.color.RED,
                        30
                    )
                arcade.draw_text(
                    "Press Space to confirm your choice",
                    self.width / 2,
                    330,
                    arcade.color.LIGHT_GRAY,
                    14,
                    anchor_x="center"
                )
            return


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

    def setup_map(self):
        screen_w = self.width
        screen_h = self.height

        img = Image.open(BytesIO(
            requests.get(url + "assets/images/backgrounds/hintergrund.png").content
        )).convert("RGB")

        self.map_img = img.resize((screen_w, screen_h))
        self.map_pixels = self.map_img.load()

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

    def is_water(self, x, y):
        img_x = int(x)
        img_y = self.map_img.height - 1 - int(y)

        if img_x < 0 or img_y < 0 or img_x >= self.map_img.width or img_y >= self.map_img.height:
            return True

        r, g, b = self.map_pixels[img_x, img_y]

        # besserer Wasser-Check
        return b > r and b > g


    def is_blocked(self, x, y):
        points = [
            (0, 0),
            (10, 0), (-10, 0),
            (0, 10), (0, -10),
            (10, 10), (-10, 10),
            (10, -10), (-10, -10),
        ]

        for ox, oy in points:
            if self.is_water(x + ox, y + oy):
                return False

        return False

    def water_depth(self, x, y, max_dist=60):
        for dist in range(0, max_dist, 4):  # Schrittweite = Performance + Genauigkeit
            for dx in range(-dist, dist + 1, 4):
                for dy in range(-dist, dist + 1, 4):
                    check_x = x + dx
                    check_y = y + dy

                    # sobald Land gefunden → Tiefe = Distanz
                    if not self.is_water(check_x, check_y):
                        return dist

        return max_dist  # komplett tief drin

    def on_update(self, delta_time):
        if self.state != "explore":
            return

        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = ""

        depth = self.water_depth(self.player.center_x, self.player.center_y)

        speed = PLAYER_SPEED

        if self.is_water(self.player.center_x, self.player.center_y):
            speed = PLAYER_SPEED * 0.5  # langsamer im Wasser

        dx = 0
        dy = 0

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
        depth_next = self.water_depth(new_x, new_y)

        # 👉 zu tief → stoppen
        if depth_next > 40:
            return

        # check X + Y zusammen (nicht getrennt!)
        if not self.is_blocked(new_x, self.player.center_y):
            self.player.center_x = new_x

        if not self.is_blocked(self.player.center_x, new_y):
            self.player.center_y = new_y



    def on_key_press(self, key, modifiers):
        self.keys_held.add(key)
        if self.state == "level_up" and key == arcade.key.SPACE:
            self.state = "level_choice"
            return
        elif self.state == "level_choice":

            if key == arcade.key.LEFT:
                self.selected_4 = (self.selected_4 - 1) % len(self.menu_4)

            if key == arcade.key.RIGHT:
                self.selected_4 = (self.selected_4 + 1) % len(self.menu_4)

            if key == arcade.key.SPACE:

                choice = self.menu_4[self.selected_4]

                if choice == "Hp":
                    self.max_hp += 20
                    self.player_hp += 20

                elif choice == "Bp":
                    self.max_bp += 20
                    self.bp += 20

                self.state = "dialog"
                self.current_dialog_id = 11
                self.dialog_index = 0

        # enter dialogue
        if self.state == "explore" and key == arcade.key.E:
            dist = arcade.get_distance_between_sprites(self.player, self.enemy)

            if dist < 80:
                self.state = "dialog"
                self.dialog_index = 0
                self.current_dialog_id = 1



        # dialog progression
        if self.state == "dialog" and key == arcade.key.SPACE:
            self.dialog_index += 1

            if self.dialog_index >= len(dialogues[self.current_dialog_id]["lines"]):
                self.dialog_index = 0


                if self.after_battle:
                    if self.player_xp >= self.player_max_xp:
                        self.player_xp = 0
                        self.player_max_xp += 50

                        self.current_dialog_id = 10
                        self.dialog_index = 0
                        self.state = "dialog"
                        self.after_battle = False
                        return
                    else:
                        self.enemy.kill()
                        self.state = "explore"
                        self.after_battle = False
                        return
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
                elif self.story_step == 6:
                    self.current_dialog_id = 7
                elif self.story_step == 7:
                    self.current_dialog_id = 8
                else:
                    self.state = "battle"
                    self.start_battle_positions()
        if self.state == "battle":

            if key == arcade.key.LEFT:
                self.selected = (self.selected - 1) % len(self.menu)

            if key == arcade.key.RIGHT:
                self.selected = (self.selected + 1) % len(self.menu)



            if key == arcade.key.SPACE :
                self.do_action()
            if self.menu[self.selected] == "Item":
                if key == arcade.key.UP:
                    self.selected_2 = (self.selected_2 - 1) % len(self.menu_2)

                if key == arcade.key.DOWN:
                    self.selected_2 = (self.selected_2 + 1) % len(self.menu_2)

            if self.menu[self.selected] == "Magic":
                if key == arcade.key.UP:
                    self.selected_3 = (self.selected_3 - 1) % len(self.menu_3)

                if key == arcade.key.DOWN:
                    self.selected_3 = (self.selected_3 + 1) % len(self.menu_3)

    def on_key_release(self, key, modifiers):
        if key in self.keys_held:
            self.keys_held.remove(key)


if __name__ == "__main__":
    Game()
    arcade.run()