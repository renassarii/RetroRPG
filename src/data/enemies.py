"""Enemy stat sheets and their texture paths (relative to BASE_URL)."""

ENEMIES = {
    "Köpek Franz": {"xp": 100, "hp": 100},
    "Altunyarrak": {"xp": 20, "hp": 150},
}

ENEMY_TEXTURE_PATHS = {
    "Köpek Franz": "assets/images/characters/Franz.png",
    "Altunyarrak": "assets/images/characters/emre.png",
}


INITIAL_ENEMY_SPAWNS = [
    ("franz_1","Köpek Franz", 500, 200, "beach"),
    ("Altunyarrak_1","Altunyarrak", 400, 300, "forest_1"),
]
