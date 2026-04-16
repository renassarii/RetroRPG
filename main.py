import arcade
import random

WIDTH = 800
HEIGHT = 450

PLAYER_SPEED = 3

url = "https://raw.githubusercontent.com/renassarii/RetroRPG/main/"
# =========================
# DIALOG
# =========================
dialogues = {
    1: [
        "Franz: Hey du!",
        "Was willst du hier?",
        "Dann kämpfen wir!"
    ]
}


class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "RPG SYSTEM", fullscreen=True)
        self.set_fullscreen(True)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # =========================
        # STATE
        # =========================
        self.state = "explore"
        self.dialog_index = 0

        # =========================
        # SPRITES
        # =========================
        self.player = arcade.Sprite(url + "assets/images/character/gandalf.png", 2)
        self.enemy = arcade.Sprite(url +"assets/images/character/Franz.png", 2)

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

        # =========================
        # MENU
        # =========================
        self.menu = ["SCHLAG", "MAGIE", "ITEM", "FLUCHT"]
        self.selected = 0

        self.message = ""

        # movement
        self.keys_held = set()

    # =========================
    # POSITION FIX (KAMPF SETUP)
    # =========================
    def start_battle_positions(self):
        # unter HP Bars positionieren
        self.player.center_x = 200
        self.player.center_y = 320

        self.enemy.center_x = 600
        self.enemy.center_y = 320

    # =========================
    # DRAW
    # =========================
    def on_draw(self):
        self.clear()

        # =========================
        # EXPLORE MODE
        # =========================
        if self.state == "explore":
            self.player_list.draw()
            self.enemy_list.draw()
            return

        # =========================
        # DIALOG MODE
        # =========================
        if self.state == "dialog":
            self.player_list.draw()
            self.enemy_list.draw()

            arcade.draw_rect_filled(
                arcade.rect.XYWH(400, 80, 760, 140),
                arcade.color.BLACK
            )

            arcade.draw_text(
                dialogues[1][self.dialog_index],
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

        # HP
        self.draw_hp_bar(200, 410, self.player_hp, arcade.color.GREEN)
        self.draw_hp_bar(600, 410, self.enemy_hp, arcade.color.RED)

        arcade.draw_text("DU", 170, 430, arcade.color.WHITE, 14)
        arcade.draw_text("FRANZ", 570, 430, arcade.color.WHITE, 14)

        # UI BOX
        arcade.draw_rect_filled(
            arcade.rect.XYWH(400, 80, 760, 140),
            arcade.color.BLACK
        )

        arcade.draw_rect_outline(
            arcade.rect.XYWH(400, 80, 760, 140),
            arcade.color.WHITE,
            3
        )

        x = 200
        for i, item in enumerate(self.menu):
            color = arcade.color.YELLOW if i == self.selected else arcade.color.WHITE
            arcade.draw_text(item, x + i * 150, 70, color, 18)

        arcade.draw_text(self.message, 250, 20, arcade.color.WHITE, 14)

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

        fill = (hp / self.max_hp) * width

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x - (width - fill) / 2, y, fill, height),
            color
        )

    # =========================
    # UPDATE MOVEMENT (nur explore)
    # =========================
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

    # =========================
    # INPUT
    # =========================
    def on_key_press(self, key, modifiers):

        self.keys_held.add(key)

        # ESC FULLSCREEN
        if key == arcade.key.ESCAPE:
            self.set_fullscreen(not self.fullscreen)

        # =========================
        # START DIALOG
        # =========================
        if self.state == "explore" and key == arcade.key.E:
            if self.player.collides_with_sprite(self.enemy):
                self.state = "dialog"
                self.dialog_index = 0

        # =========================
        # DIALOG NEXT
        # =========================
        elif self.state == "dialog" and key == arcade.key.SPACE:
            self.dialog_index += 1

            if self.dialog_index >= len(dialogues[1]):
                self.state = "battle"
                self.start_battle_positions()

        # =========================
        # BATTLE
        # =========================
        elif self.state == "battle":

            if key == arcade.key.LEFT:
                self.selected = (self.selected - 1) % len(self.menu)

            if key == arcade.key.RIGHT:
                self.selected = (self.selected + 1) % len(self.menu)

            if key == arcade.key.SPACE:
                self.do_action()

    def on_key_release(self, key, modifiers):
        if key in self.keys_held:
            self.keys_held.remove(key)

    # =========================
    # BATTLE LOGIC
    # =========================
    def do_action(self):

        action = self.menu[self.selected]

        if action == "SCHLAG":
            dmg = random.randint(10, 20)
            self.enemy_hp -= dmg
            self.message = f"⚔ {dmg}"

        elif action == "MAGIE":
            dmg = random.randint(15, 30)
            self.enemy_hp -= dmg
            self.message = f"✨ {dmg}"

        elif action == "ITEM":
            heal = random.randint(10, 25)
            self.player_hp = min(self.max_hp, self.player_hp + heal)
            self.message = f"+{heal} HP"

        elif action == "FLUCHT":
            if random.random() > 0.5:
                self.state = "explore"
                self.message = "Geflohen!"
                return
            else:
                self.message = "Flucht fehlgeschlagen!"

        # enemy turn
        if self.enemy_hp > 0:
            self.player_hp -= random.randint(5, 15)


if __name__ == "__main__":
    Game()
    arcade.run()