import arcade
import random

WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 4

class Player(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

class Enemy(arcade.Sprite):
    def update(self):
        self.center_x += random.choice([-2, -1, 0, 1, 2])
        self.center_y += random.choice([-2, -1, 0, 1, 2])

class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Mini RPG")
        arcade.set_background_color(arcade.color.DARK_GREEN)

        self.player = Player(":resources:images/animated_characters/male_person/malePerson_idle.png", 1)
        self.player.center_x = 400
        self.player.center_y = 300

        self.enemies = arcade.SpriteList()
        for _ in range(5):
            enemy = Enemy(":resources:images/enemies/slimeBlue.png", 1)
            enemy.center_x = random.randint(0, WIDTH)
            enemy.center_y = random.randint(0, HEIGHT)
            self.enemies.append(enemy)

        self.score = 0

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.enemies.draw()
        arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.player.update()
        self.enemies.update()

        # Kollision check
        hit_list = arcade.check_for_collision_with_list(self.player, self.enemies)
        for enemy in hit_list:
            enemy.remove_from_sprite_lists()
            self.score += 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = PLAYER_SPEED
        elif key == arcade.key.S:
            self.player.change_y = -PLAYER_SPEED
        elif key == arcade.key.A:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.D:
            self.player.change_x = PLAYER_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.W, arcade.key.S]:
            self.player.change_y = 0
        if key in [arcade.key.A, arcade.key.D]:
            self.player.change_x = 0


if __name__ == "__main__":
    game = Game()
    arcade.run()