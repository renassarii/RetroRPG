"""Battle logic: player actions, enemy turn, post-action state transitions."""

import arcade
import random

from src.data.enemies import ENEMIES
from src.data.items import BATTLE_MENU, MAGIC_BP_COST, MAGIC_NAMES, ITEM_NAMES


PUNCH_BASE_DAMAGE = 14
FIRE_BASE_DAMAGE = 10
ICE_BASE_DAMAGE = 20
NATURE_HEAL = 40

HEALTH_POTION_HEAL = 20
MANA_POTION_RESTORE = 20

LEVEL_XP_INCREMENT = 50

def spawn_damage(game, target, damage, is_crit=False):
    color = arcade.color.GRAY if is_crit else arcade.color.YELLOW

    game.damage_numbers.append({
        "text": f"-{damage}",
        "x": target.center_x + 30,
        "y": target.center_y + 40,
        "timer": 1.0,
        "color": color
    })


def perform_player_action(game):
    """Resolve the action currently selected in the battle menu.

    Mutates game state directly. After this returns, the caller decides
    whether to hand the turn to the enemy.
    """
    action = BATTLE_MENU[game.selected]

    if action == "Punch":
        _resolve_punch(game)
    elif action == "Magic":
        _resolve_magic(game)
    elif action == "Item":
        _resolve_item(game)
    elif action == "Escape":
        _resolve_escape(game)

    _check_battle_end(game)


def _resolve_punch(game):
    damage = PUNCH_BASE_DAMAGE

    if game.player_buff_spell:
        if game.enemy_defense:
            shield_damage = int((damage * random.random()) * 2)
            game.enemy_hp -= shield_damage
            spawn_damage(game, game.enemy, shield_damage)
            game.enemy_defense = False
        else:
            game.enemy_hp -= damage * 2
            spawn_damage(game, game.enemy, damage * 2, is_crit=True)

        game.player_buff_spell = False

    else:
        if game.enemy_defense:
            shield_damage = int(damage * random.random())
            game.enemy_hp -= shield_damage
            spawn_damage(game, game.enemy, shield_damage)
            game.enemy_defense = False
        else:
            game.enemy_hp -= damage
            spawn_damage(game, game.enemy, damage)


def _resolve_magic(game):
    magic = MAGIC_NAMES[game.selected_3]
    cost = MAGIC_BP_COST[magic]

    if game.bp < cost:
        game.message = "you don't have enough BP"
        return

    if magic == "Fire Spell":
        game.bp -= cost
        _apply_offensive_magic(game, FIRE_BASE_DAMAGE, "-20 damage")
    elif magic == "Ice Spell":
        game.bp -= cost
        _apply_offensive_magic(game, ICE_BASE_DAMAGE, "-20 damage", buff_doubles=False)
    elif magic == "Copper":
        game.bp -= cost
        game.player_buff_spell = True
    elif magic == "Rakukaja":
        game.bp -= cost
        game.player_debuff_spell = True
    elif magic == "Nature Spell":
        game.bp -= cost
        game.player_hp = min(game.max_hp, game.player_hp + NATURE_HEAL)
        game.message = "you healed yourself"


def _apply_offensive_magic(game, damage, message, buff_doubles=True):
    if buff_doubles and game.player_buff_spell:
        if game.enemy_defense:
            shield_damage = int((damage * random.random()) * 2)
            game.enemy_hp -= shield_damage
            spawn_damage(game, game.enemy, shield_damage)
            game.enemy_defense = False
        else:
            game.enemy_hp -= damage * 2
            spawn_damage(game, game.enemy, damage * 2, is_crit=True)

        game.player_buff_spell = False

    else:
        if game.enemy_defense:
            shield_damage = int(damage * random.random())
            game.enemy_hp -= shield_damage
            spawn_damage(game, game.enemy, shield_damage)
            game.enemy_defense = False
        else:
            game.enemy_hp -= damage
            spawn_damage(game, game.enemy, damage)


def _resolve_item(game):
    item = ITEM_NAMES[game.selected_2]

    if game.inventory[item] <= 0:
        game.message = "No potions left"
        return

    if item == "small Health potion":
        game.player_hp = min(game.max_hp, game.player_hp + HEALTH_POTION_HEAL)
        game.message = "+20 HP"
    elif item == "small Mana potion":
        game.bp = min(game.max_bp, game.bp + MANA_POTION_RESTORE)
        game.message = "+20 BP"
    elif item == "Chug Chug":
        game.player_hp = game.max_hp
        game.bp = game.max_bp
        game.message = "everything fully restored"

    game.inventory[item] -= 1


def _resolve_escape(game):
    if random.random() > 0.5:
        game.state = "explore"
        game.message = "Ran away!"


def _check_battle_end(game):
    if game.enemy_hp <= 0:

        # mark enemy as dead (WICHTIG)
        if game.current_enemy_id is not None:
            game.dead_enemies.add(game.current_enemy_id)

        xp_gain = ENEMIES[game.current_enemy]["xp"]
        game.player_xp += xp_gain
        game.message = f"+{xp_gain} XP"

        game.after_battle = True

        # ❗ NICHT entfernen aus enemy_list hier!
        # ❗ NICHT game.enemy = None hier!

        if game.player_xp >= game.player_max_xp:
            game.player_xp -= game.player_max_xp
            game.level += 1
            game.player_max_xp += LEVEL_XP_INCREMENT
            game.state = "level_choice"
            game.selected_4 = 0
            return

        game.post_battle_xp = max(0, game.player_max_xp - game.player_xp)
        game.state = "post_battle"
        return

    if game.player_hp <= 0:
        game.state = "gameover"
def _dismiss_post_battle(self):
    if self.enemy:
        try:
            self.enemy.kill()
        except:
            pass

    self.enemy = None
    self.state = "explore"
    self.after_battle = False
    self.post_battle_xp = None

def perform_enemy_turn(game):
    """Resolve a single enemy action. Caller decides timing via enemy_timer."""
    if game.player_debuff_spell:
        _enemy_debuffed_turn(game)
        game.player_debuff_spell = False
    else:
        _enemy_normal_turn(game)

    game.enemy_turn = False
    game.player_turn = True


def _enemy_debuffed_turn(game):
    luck = random.random()
    game.enemy_luck = luck

    if luck <= 0.1:
        damage = int(20 * random.random())
        game.player_hp -= damage
        spawn_damage(game, game.player, damage)

    elif luck <= 0.6:
        damage = int(10 * random.random())
        game.player_hp -= damage
        spawn_damage(game, game.player, damage)

    elif luck <= 0.9:
        game.enemy_defense = True

    else:
        game.enemy_hp += 5
        game.message = "Damn this bitch healed himself"


def _enemy_normal_turn(game):
    luck = random.random()
    game.enemy_luck = luck

    if luck <= 0.2:
        game.player_hp -= 20
        spawn_damage(game, game.player, 20)

    elif luck <= 0.6:
        game.player_hp -= 10
        spawn_damage(game, game.player, 10)

    elif luck <= 0.8:
        game.enemy_defense = True

    else:
        heal = 5
        game.enemy_hp += heal
        game.message = f"Damn this bitch healed himself for {heal} hp"