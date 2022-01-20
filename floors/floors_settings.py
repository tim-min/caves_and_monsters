from gui_elements import NPC


floor1 = [{
    "enemies": [[None], ['BOS_1'], ['Zombie', 'Archer'], ['Zombie', 'Archer', 'Goblin'], ['Zombie', 'Archer', 'Wolf'], ['Goblin', 'Archer', 'Wolf'], ['Archer'], ['Archer', 'Wolf'], ['BOS_1']],
    "npc": [],
    "npc_coords": [],
    "map": "floors/floormap_0_0.txt",
    "waves": 8,
    "enemies_max_count": [None, 1, 5, 6, 7, 8, 9, 10, 1],
    "spawn_ability": 1,
    "music": "sounds/rooms/0_0.mp3",
    "npc_spawn": 0,
    "main_tile": 0,
    "dark": 0
},
    {
        "enemies": [],
        "npc": [],
        "npc_coords": [],
        "map": "floors/floormap_0_1.txt",
        "waves": 5,
        "enemies_max_count": [0],
        "spawn_ability": 0,
        "npc_spawn": 1,
        'spawn_farm_object': 0,
        "main_tile": 0,
        "dark": 0
    },
    {
        "enemies": [],
        "npc": [("main_npc", 50, ["test"])],
        "npc_coords": [(500, 700)],
        "map": "floors/floormap_0_2.txt",
        "waves": 0,
        "enemies_max_count": [0],
        "spawn_ability": 0,
        "npc_spawn": 1,
        "main_tile": 0,
        "door_position": [300, 200],
        "dark": 0
    },
        {
        "enemies": [['Rock', 'Charcoal', 'Slime', 'Iron', 'Bronze']],
        "npc": [],
        "npc_coords": [],
        "map": "floors/floormap_0_3.txt",
        "waves": 0,
        "enemies_max_count": [25],
        "spawn_ability": 2, # теперь короче если в комнате фарм объекты, то 2
        "npc_spawn": 0,
        "main_tile": 57,
        "dark": 1
    }
]


floor2 = [{
    "enemies": [["Zombie", "Archer", "Goblin", "Wolf"], ["Zombie", "Archer", "IceWolf"], ["Zombie", "Archer", "Goblin", "IceWolf"], ["BOS_2"], ["Archer", "Goblin", "SnowMag"], ["Archer", "SnowMag", "IceWolf"], ["Zombie", "Archer", "Goblin", "Wolf", "IceWolf", "SnowMag"], ["BOS_3"]],
    "npc": [],
    "npc_coords": [],
    "map": "floors/floormap_1_0.txt",
    "waves": 8,
    "enemies_max_count": [8, 8, 8, 1, 10, 10, 10, 1],
    "spawn_ability": 1,
    "npc_spawn": 0,
    "music": "sounds/rooms/0_0.mp3",
    'spawn_farm_object': 0,
    "main_tile": 45,
    "dark": 0
},
    {
        "enemies": [[]],
        "npc": [],
        "npc_coords": [],
        "map": "floors/floormap_1_1.txt",
        "waves": 5,
        "enemies_max_count": [0],
        "spawn_ability": 0,
        "npc_spawn": 1,
        'spawn_farm_object': 0,
        "main_tile": 45,
        "dark": 0
    },
    {
        "enemies": [[]],
        "npc": [("main_npc", 50, ["test"])],
        "npc_coords": [(500, 700)],
        "map": "floors/floormap_1_2.txt",
        "waves": 0,
        "enemies_max_count": [0],
        "spawn_ability": 0,
        "npc_spawn": 1,
        "main_tile": 45,
        "dark": 0
    },
        {
        "enemies": [['Rock', 'Charcoal', 'Slime', 'Iron', 'Bronze', 'Gold', 'Silver']],
        "npc": [],
        "npc_coords": [],
        "map": "floors/floormap_1_3.txt",
        "waves": 0,
        "enemies_max_count": [25],
        "spawn_ability": 2, # теперь короче если в комнате фарм объекты, то 2
        "npc_spawn": 0,
        "main_tile": 57,
        "dark": 1
    }
]

FSETTINGS = [floor1, floor2]
