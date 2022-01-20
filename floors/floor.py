class Floor:
    def __init__(self, rooms):
        self.rooms = rooms
        self.current_room = 2
    
    def generate_rooms(self, objects, screen, tile_size):
        for room in self.rooms:
            room.generate_map(objects, screen, tile_size)

    def loop(self, screen, player, fps,pos=None):
        self.rooms[self.current_room].loop(screen, player, fps,pos)
