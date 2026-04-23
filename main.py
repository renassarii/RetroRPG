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
        super().__init__(WIDTH, HEIGHT, "Köpek RPG", fullscreen=True)
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
            "small Health potion": url + "assets/images/items/SmallHealPotion.png",
            "Chug Chug": url + "assets/images/items/mix.png"
        }

        self.magic_icons = {
            "Fire Spell": url + "assets/images/level_up_symbols/Fire.png",
            "Ice Spell": url + "assets/images/level_up_symbols/Ice.png",
            "Rakukaja": url + "assets/images/level_up_symbols/Fire.png",
            "Copper": url + "assets/images/level_up_symbols/copper.png",
            "Nature Spell": url + "assets/images/level_up_symbols/heart.png",
                            }
        self.level_icons = {
            "Health points": load_texture_from_url(url + "assets/images/level_up_symbols/heart.png"),
            "Mana": load_texture_from_url(url + "assets/images/level_up_symbols/ManaSymbol.png"),
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
        self.player_debuff_spell = False
        self.player_buff_spell = False
        self.enemy_hp = 100
        self.enemy_max_hp = 100
        self.enemy_luck = 0
        self.enemy_defense = False
        self.max_hp = 100
        self.player_xp = 0
        self.player_max_xp = 100
        self.level = 1

        self.bp = 20
        self.max_bp = 20

        self.magic_scroll = 0
        self.visible_magic = 3

        self.item_scroll = 0
        self.visible_item = 3

        self.set_spawn_points()

        # dialog control
        self.current_dialog_id = 1
        self.story_step = 0

        # =========================
        # MENU
        # =========================
        self.menu = ["Punch", "Magic", "Item", "Escape"]
        self.selected = 0
        self.menu_2 = ["small Mana potion", "small Health potion", "Chug Chug"]
        self.selected_2 = 0
        self.inventory = {
            "small Mana potion": 5,
            "small Health potion": 5,
            "Chug Chug": 1,
        }
        self.menu_3 = ["Fire Spell", "Ice Spell", "Rakukaja", "Copper", "Nature Spell"]
        self.selected_3 = 0
        self.usage = {
            "Fire Spell":3,
            "Ice Spell":6,
            "Rakukaja":4,
            "Copper":5,
            "Nature Spell":7,
        }
        self.menu_4 = ["Health points", "Mana"]
        self.selected_4 = 0
        self.message = ""

        self.enemy_turn = False
        self.enemy_timer = 0
        self.player_turn = True


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
        # post-battle XP popup
        self.post_battle_xp = None

    def do_action(self):
        action = self.menu[self.selected]
        action_done = False

        if action == "Punch":
            damage = 14
            if self.player_buff_spell:
                if self.enemy_defense:
                    shield_damage = int((damage * random.random()) * 2)
                    self.enemy_hp -= shield_damage
                    self.message = f"he shielded himself {shield_damage} damage"
                    action_done = True
                    self.enemy_defense = False
                    self.player_buff_spell = False
                else:
                    self.enemy_hp -= (damage * 2)
                    self.message = "you did -28 damage"
                    action_done = True
                    self.player_buff_spell = False

            else:
                if self.enemy_defense:
                    shield_damage = int(damage * random.random())
                    self.enemy_hp -= shield_damage
                    self.message = f"he shielded himself {shield_damage} damage"
                    action_done = True
                    self.enemy_defense = False
                else:
                    self.enemy_hp -= damage
                    self.message = "you did -14 damage"
                    action_done = True
        elif action == "Magic":
            magic = self.menu_3[self.selected_3]

            if magic == "Fire Spell":
                if self.bp >= 3:
                    damage = 10
                    self.bp -= 3
                    if self.player_buff_spell:
                        if self.enemy_defense:
                            shield_damage = int((damage * random.random())* 2)
                            self.enemy_hp -= shield_damage
                            self.message = f"he shielded himself {shield_damage} damage"
                            action_done  = True
                            self.enemy_defense = False
                            self.player_buff_spell = False
                        else:
                            self.enemy_hp -= (damage * 2)
                            self.message = "-20 damage"
                            action_done = True
                            self.player_buff_spell = False
                    else:
                        if self.enemy_defense:
                            shield_damage = int(damage * random.random())
                            self.enemy_hp -= shield_damage
                            self.message = f"he shielded himself {shield_damage} damage"
                            action_done  = True
                            self.enemy_defense = False
                        else:
                            self.enemy_hp -= damage
                            self.message = "-20 damage"
                            action_done = True
                else:
                    self.message = "you don't have enough BP"


            elif magic == "Ice Spell":
                if self.bp >= 6:
                    damage = 20
                    self.bp -= 6
                    if self.enemy_defense:
                        shield_damage = int(damage * random.random())
                        self.enemy_hp -= shield_damage
                        self.message = f"he shielded himself {shield_damage} damage"
                        action_done = True
                        self.enemy_defense = False
                    else:
                        self.enemy_hp -= damage
                        self.message = "-20 damage"
                        action_done = True
                else:
                    self.message = "you don't have enough BP"
            if magic == "Copper":
                if self.bp >= 5:
                    self.player_buff_spell = True
                    self.bp -= 5
                else:
                    self.message = "you don't have enough BP"

            if magic == "Rakukaja":
                if self.bp >= 4:
                    self.player_debuff_spell = True
                    self.bp -= 4
                else:
                    self.message = "you don't have enough BP"

            if magic == "Nature Spell":
                if self.bp >= 7:
                    self.player_hp = min(self.max_hp, self.player_hp + 40)
                    self.bp -= 7
                    self.message = "you healed yourself"
                else:
                    self.message = "you don't have enough BP"

        elif action == "Item":
            item = self.menu_2[self.selected_2]

            # ❗ prüfen ob vorhanden
            if self.inventory[item] > 0:

                if item == "small Health potion":
                    self.player_hp = min(self.max_hp, self.player_hp + 20)
                    self.message = "+20 HP"
                    action_done = True

                elif item == "small Mana potion":
                    self.bp = min(self.max_bp, self.bp + 20)
                    self.message = "+20 BP"
                    action_done = True
                elif item == "Chug Chug":
                    self.player_hp = self.max_hp
                    self.bp = self.max_bp
                    self.message = "everything fully restored"
                    action_done = True

                #  reduzieren
                self.inventory[item] -= 1

            else:
                self.message = "No potions left"


        elif action == "Escape":
            if random.random() > 0.5:
                self.state = "explore"
                self.message = "Ran away!"
                action_done = True

        if self.enemy_hp <= 0:
            self.after_battle = True
            self.player_xp += 50
            if self.player_xp >= self.player_max_xp:
                # sofort Level-Up: Wechsel zur Level-Choice
                self.player_xp -= self.player_max_xp
                self.level += 1
                self.player_max_xp += 50

                self.state = "level_choice"
                self.selected_4 = 0
                return
            else:
                # Berechne wie viel XP noch bis zum nächsten Level fehlt
                xp_to_next = max(0, self.player_max_xp - self.player_xp)
                self.post_battle_xp = xp_to_next
                # Zeige einen kurzen Post-Battle-Popup an
                self.state = "post_battle"
                return


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

        # Post-battle XP popup (zeigt kurz, wie viel XP bis zum nächsten Level fehlt)
        if self.state == "post_battle":
            # Zeichne Szene im Hintergrund
            self.player_list.draw()
            self.enemy_list.draw()

            # Popup-Box
            popup_w = 420
            popup_h = 120
            popup_x = self.width // 2
            popup_y = 450

            arcade.draw_rect_filled(
                arcade.rect.XYWH(popup_x, popup_y, popup_w, popup_h),
                arcade.color.DARK_OLIVE_GREEN
            )

            arcade.draw_text(
                f"Noch {self.post_battle_xp} XP bis zum nächsten Level",
                popup_x,
                popup_y + 20,
                arcade.color.WHITE,
                18,
                anchor_x="center"
            )

            arcade.draw_text(
                "Press Space to continue",
                popup_x,
                popup_y - 30,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="center"
            )

            return

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

            self.draw_hp_bar(200, 410, self.player_hp,self.max_hp, arcade.color.GREEN)
            self.draw_hp_bar(600, 410, self.enemy_hp,self.enemy_max_hp, arcade.color.RED)
            self.draw_bp_bar(200, 395, self.bp, arcade.color.CYAN)

            arcade.draw_text("Gypsy Luka", 170, 430, arcade.color.WHITE, 14)
            arcade.draw_text("Köpek Franz", 570, 430, arcade.color.WHITE, 14)

            arcade.draw_rect_filled(
                arcade.rect.XYWH(400, 80, 4000, 140),
                arcade.color.BLACK
            )

            x = 200
            msg_color = arcade.color.WHITE

            arcade.draw_text(
                self.message,
                250,
                20,
                msg_color,
                14
            )

            if self.menu[self.selected] == "Magic":

                popup_x = 250
                popup_y = 200
                popup_width = 200
                popup_height = 160

                arcade.draw_rect_filled(
                    arcade.rect.XYWH(popup_x, popup_y, popup_width, popup_height),
                    arcade.color.BLACK
                )

                start = self.magic_scroll
                end = start + self.visible_magic

                for i, magic in enumerate(self.menu_3[start:end]):
                    real_index = start + i
                    y = popup_y + 70 - i * 45

                    is_selected = (real_index == self.selected_3)

                    if is_selected:
                        arcade.draw_rect_filled(
                            arcade.rect.XYWH(popup_x, y, popup_width, 40),
                            (160, 80, 255, 180)
                        )

                        # glow effekt (etwas heller/lila)
                        arcade.draw_rect_filled(
                            arcade.rect.XYWH(popup_x, y, 220, 40),
                            (190, 120, 255, 140)
                        )

                    # ICON
                    texture = self.magic_textures[magic]
                    arcade.draw_texture_rect(
                        texture,
                        arcade.rect.XYWH(popup_x - 80, y, 30, 30)
                    )

                    # TEXT
                    color = arcade.color.WHITE if is_selected else arcade.color.LIGHT_GRAY
                    arcade.draw_text(
                        magic,
                        popup_x - 40,
                        y - 8,
                        color,
                        12
                    )

                    # COST rechts
                    arcade.draw_text(
                        f"-{self.usage[magic]} BP",
                        popup_x + 60,
                        y - 8,
                        arcade.color.WHITE if is_selected else arcade.color.GRAY,
                        12
                    )

                    # CURSOR
                    if is_selected:
                        arcade.draw_text(
                            "▶",
                            popup_x - 110,
                            y - 10,
                            arcade.color.BLACK,
                            18
                        )

                if self.magic_scroll > 0:
                    arcade.draw_text("↑", popup_x + 70, popup_y + 80, arcade.color.WHITE, 16)

                if self.magic_scroll + self.visible_magic < len(self.menu_3):
                    arcade.draw_text("↓", popup_x + 70, popup_y - 60, arcade.color.WHITE, 16)

            arcade.draw_text(f"Level: {self.level}", 20, 430, arcade.color.WHITE, 14)

            for i, item in enumerate(self.menu):
                # Einheitliche Farb-Logik: bei Auswahl je nach Item unterschiedliche Farben
                if i == self.selected:
                    if item == "Magic":
                        color = (160, 80, 255)  # violet
                    elif item == "Escape":
                        color = (255, 16, 240)  # neon pink
                    elif item == "Punch":
                        color = (150, 0, 24)  # carmin red
                    else:
                        color = (255, 255, 0)  # yellow (z.B. Item)
                else:
                    color = arcade.color.WHITE

                arcade.draw_text(item, x + i * 150, 70, color, 18)

            arcade.draw_text(self.message, 250, 20, arcade.color.WHITE, 14)

            if self.menu[self.selected] == "Item":

                popup_x = 250
                popup_y = 200
                popup_width = 200
                popup_height = 160

                arcade.draw_rect_filled(
                    arcade.rect.XYWH(popup_x, popup_y, popup_width, popup_height),
                    arcade.color.BLACK
                )

                start = self.item_scroll
                end = start + self.visible_item

                for i, item in enumerate(self.menu_2[start:end]):

                    real_index = start + i
                    y = popup_y + 70 - i * 45

                    is_selected = (real_index == self.selected_2)

                    if is_selected:
                        arcade.draw_rect_filled(
                            arcade.rect.XYWH(popup_x, y, popup_width, 40),
                            (255, 220, 0, 180)
                        )

                        arcade.draw_rect_filled(
                            arcade.rect.XYWH(popup_x, y, 220, 40),
                            (255, 220, 0, 180)
                        )

                    texture = self.item_textures[item]

                    arcade.draw_texture_rect(
                        texture,
                        arcade.rect.XYWH(popup_x - 80, y, 30, 30)
                    )

                    color = arcade.color.BLACK if is_selected else arcade.color.WHITE

                    count = self.inventory[item]

                    arcade.draw_text(
                        f"{count}x {item}",
                        popup_x - 50,
                        y - 8,
                        color,
                        12
                    )

                    if is_selected:
                        arcade.draw_text(
                            "▶",
                            popup_x - 110,
                            y - 10,
                            arcade.color.BLACK,
                            18
                        )

                # =========================
                # SCROLL ARROWS
                # =========================

                if self.item_scroll > 0:
                    arcade.draw_text("↑", popup_x + 70, popup_y + 80, arcade.color.WHITE, 16)

                if self.item_scroll + self.visible_item < len(self.menu_2):
                    arcade.draw_text("↓", popup_x + 70, popup_y - 60, arcade.color.WHITE, 16)

                arcade.draw_text(f"Level: {self.level}", 20, 430, arcade.color.WHITE, 14)






        if self.state == "level_choice":
            arcade.draw_texture_rect(
                self.level_ui_bg,
                arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
            )

            arcade.draw_text(
                "LEVEL UP! Pick your upgrade",
                self.width / 2,
                380,
                arcade.color.WHITE,
                24,
                anchor_x="center"
            )


            for i, option in enumerate(self.menu_4):
                x = 600 + i * 300
                y = 200

                if self.selected_4 == i:
                    if option == "Health points":
                        box_color = (150, 0, 24)  # carmin red
                    else:
                        box_color = (40, 60, 180)  # blau
                else:
                    box_color = arcade.color.BLACK

                arcade.draw_rect_filled(
                    arcade.rect.XYWH(x, y, 200, 180),
                    box_color
                )

                # Icon
                arcade.draw_texture_rect(
                    self.level_icons[option],
                    arcade.rect.XYWH(x, y + 40, 80, 80)
                )

                # Text (immer weiß auf der Box)
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
                        "▲",
                        x -17 ,
                        y - 80,
                        arcade.color.WHITE,
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
    def draw_hp_bar(self, x, y, hp, max_hp, color):
        width = 160
        height = 12

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, width, height),
            arcade.color.DARK_RED
        )

        ratio = max(0, min(hp / max_hp, 1))
        fill = width * ratio

        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                x - width / 2 + fill / 2,
                y,
                fill,
                height
            ),
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

        return max_dist

    def on_update(self, delta_time):

        if self.state == "battle" and self.enemy_turn:
            self.enemy_timer -= delta_time

            if self.enemy_timer <= 0:
                if self.player_debuff_spell:
                    self.enemy_luck = random.random()
                    if self.enemy_luck <= 0.1:
                        damage = int(20 * random.random())
                        self.player_hp -= damage
                        self.message = f"Crit damage {damage}"
                        self.player_debuff_spell = False
                    elif 0.1 < self.enemy_luck <= 0.6:
                        damage = int(10 * random.random())
                        self.player_hp -= int(10 * random.random())
                        self.message = f"{damage}"
                        self.player_debuff_spell = False
                    elif 0.6 < self.enemy_luck <= 0.9:
                        self.enemy_defense = True
                    elif self.enemy_luck > 0.9:
                        self.enemy_hp += 5
                        self.message = "Damn this bitch healed himself"
                    self.enemy_turn = False
                    self.player_turn = True
                else:
                    self.enemy_luck = random.random()
                    if self.enemy_luck <= 0.2:
                        self.player_hp -= 20
                        self.message = "Crit damage -20HP"
                    elif 0.2 <= self.enemy_luck <= 0.6:
                        self.player_hp -= 10
                        self.message = "-10 damage"
                    elif 0.6 <= self.enemy_luck <= 0.8:
                        self.enemy_defense = True
                    elif self.enemy_luck >= 0.8:
                        heal = 5
                        self.enemy_hp += heal
                        self.message = f"Damn this bitch healed himself for {heal} hp"
                    self.enemy_turn = False
                    self.player_turn = True

        if self.state == "explore":
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

                # Nach dem Upgrade dem Spieler sagen, wie viel XP bis zum nächsten Level fehlt
                xp_to_next = max(0, self.player_max_xp - self.player_xp)
                dialogues[99] = {
                    "name": "System",
                    "lines": [
                        f"Noch {xp_to_next} XP bis zum nächsten Level"
                    ]
                }

                self.state = "dialog"
                self.current_dialog_id = 99
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

                    if random.random() < 0.5:
                        self.player_turn = True
                        self.enemy_turn = False
                        self.message = "You start!"
                    else:
                        self.player_turn = False
                        self.enemy_turn = True
                        self.enemy_timer = 0.5
                        self.message = "Enemy starts!"

        if self.state == "battle":

            if key == arcade.key.LEFT:
                self.selected = (self.selected - 1) % len(self.menu)
                return

            elif key == arcade.key.RIGHT:
                self.selected = (self.selected + 1) % len(self.menu)
                return

            elif key == arcade.key.SPACE and self.player_turn:
                self.do_action()
                self.player_turn = False
                self.enemy_turn = True
                self.enemy_timer = 0.5
                return

        

            elif self.menu[self.selected] == "Item":
                if key == arcade.key.UP:

                    if self.selected_2 > 0:

                        self.selected_2 -= 1

                        # scroll nach oben fixen

                        if self.selected_2 < self.item_scroll:
                            self.item_scroll = self.selected_2

                    return

                if key == arcade.key.DOWN:

                    if self.selected_2 < len(self.menu_2) - 1:

                        self.selected_2 += 1

                        # scroll nach unten fixen

                        if self.selected_2 >= self.item_scroll + self.visible_item:
                            self.item_scroll = self.selected_2 - self.visible_item + 1
                    return



            elif self.menu[self.selected] == "Magic":

                if key == arcade.key.UP:

                    if self.selected_3 > 0:

                        self.selected_3 -= 1

                        # scroll nach oben fixen

                        if self.selected_3 < self.magic_scroll:
                            self.magic_scroll = self.selected_3

                    return

                if key == arcade.key.DOWN:

                    if self.selected_3 < len(self.menu_3) - 1:

                        self.selected_3 += 1

                        # scroll nach unten fixen

                        if self.selected_3 >= self.magic_scroll + self.visible_magic:
                            self.magic_scroll = self.selected_3 - self.visible_magic + 1
                    return
        # Post-battle popup bestätigen
        if self.state == "post_battle" and key == arcade.key.SPACE:
            # Wenn der Spieler durch die erhaltenen XP ein Level erreicht hätte,
            # wird dies hier behandelt (ansonsten zurück zur Erkundung).
            if self.player_xp >= self.player_max_xp:
                # Level-Up: gehe in level_choice
                self.player_xp = 0
                self.player_max_xp += 50
                self.level += 1
                self.state = "level_choice"
                self.selected_4 = 0
                self.post_battle_xp = None
                return
            else:
                # Kein Level-Up: Gegner entfernen und zurück zur Erkundung
                try:
                    self.enemy.kill()
                except Exception:
                    pass
                self.state = "explore"
                self.after_battle = False
                self.post_battle_xp = None
                return
    def on_key_release(self, key, modifiers):
        if key in self.keys_held:
            self.keys_held.remove(key)


if __name__ == "__main__":
    Game()
    arcade.run()