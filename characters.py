from drawable import Drawable
from tiles import Tile, Empty
from event import Event
import csv, os
from config import Config


class Character (Drawable):
    char_map = {}

    @staticmethod
    def load_characters(num):
        Baddie.baddies = []
        with open(os.path.join('levels', 'level{}.csv').format(num), 'rb') as file_data:
            row_num = 0
            for row in csv.reader(file_data):
                for col, value in enumerate(row):
                    if value in char_map:
                        char_map[value](col, row_num)
                row_num += 1


    def __init__(self, x, y, img_path=None):
        super(Character, self).__init__((x, y), img_path)
        self.draw()

        self._x = x
        self._y = y

    def pos(self):
        return self._x, self._y

    def same_loc(self, x, y):
        return (self._x == x and self._y == y)

    def move(self, dx, dy):
        """ Applies a move, if valid. """
        tx = self._x + dx
        ty = self._y + dy
        next_pos = (tx, ty)

        # Only allow movement inside the map
        if tx >= 0 and ty >= 0 and tx < Config.LEVEL_WIDTH and ty < Config.LEVEL_HEIGHT:

            # Only allow movement into passable tiles
            if Tile.query(next_pos, 'passable'):
                # Do not allow player to climb if they are not in a climbable tile
                if dy < 0 and not Tile.query(self.pos(), 'climbable'):
                    return

                self.apply_move(dx, dy)

    def apply_move(self, dx, dy):
        self._x += dx
        self._y += dy
        self.move_img(dx, dy)
        if self._y + 1 < Config.LEVEL_HEIGHT:
            self.fall()

    def fall(self):
        next_pos = (self._x, self._y+1)

        if self._y < Config.LEVEL_HEIGHT:
            if not Tile.query(next_pos, 'standable') and not Tile.query(self.pos(), 'grabbable'):
                self.apply_move(0, 1)

    def redraw(self):
        self.undraw()
        self.draw()


class Player (Character):
    main = None

    def __init__(self, x, y):
        super(Player, self).__init__(x, y, 't_android.gif')
        Player.main = self

    def at_exit(self):
        return (self._y == 0)

    def apply_move(self, dx, dy):
        super(Player, self).apply_move(dx, dy)
        Tile.tile_at(self.pos()).take()
        for baddie in Baddie.baddies:
            if baddie.pos() == self.pos():
                Drawable.lost()

    def dig(self, direction):
        
        def refill(tile):    
            tile.show()
            if Player.main.pos() == tile.coord:
                Drawable.lost()
            for baddie in Baddie.baddies:
                if baddie.pos() == tile.coord:
                    baddie.die()

        x = self._x + direction
        y = self._y + 1

        if self._y < Config.LEVEL_HEIGHT - 1:
            if Tile.query((x, y), 'diggable') and isinstance(Tile.tile_at((x, y-1)), Empty):
                Tile.tile_at((x,y)).hide()

                Event(refill, 120, args=[Tile.tile_at((x, y))])
                for baddie in Baddie.baddies:
                    baddie.fall()




class Baddie (Character):
    baddies = []

    def __init__(self, x, y):
        super(Baddie, self).__init__(x, y, 't_red.gif')
        self.move_event = Event(self.move, 30, recurring=True)
        Baddie.baddies.append(self)

    def move(self):
        move = PathFinder.run(self.pos())
        if move:
            super(Baddie, self).move(*move)
        if self.pos() == Player.main.pos():
            Drawable.lost()

    def die(self):
        self.undraw()
        Event.delete(self.move_event)
        Baddie.baddies.remove(self)

char_map = {'P': Player,
            'B': Baddie}

class PathFinder:
    tiles = None

    @staticmethod
    def valid_tile(pos, last_pos):
        x, y = pos
        if x >= 0 and y >= 0 and x < Config.LEVEL_WIDTH and y < Config.LEVEL_HEIGHT:
            if Tile.query(pos, 'passable'):
                under = (x, y+1)

                if Tile.query(pos, 'grabbable') or Tile.query(under, 'standable'):
                    if not PathFinder.tiles[x][y]:
                        PathFinder.tiles[x][y] = True
                        return True
        return False

    @staticmethod
    def run(start_pos):
        """
        Returns the optimal move from start_pos to get to the Player.
        Returns None if no valid paths exist.
        """
        PathFinder.tiles = [[False for y in range(Config.LEVEL_HEIGHT)] for x in range(Config.LEVEL_WIDTH)]

        x, y = start_pos
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        valid_neighbors = [neighbor for neighbor in neighbors if PathFinder.valid_tile(neighbor, start_pos)]

        children = []
        for valid_pos in valid_neighbors:
            children.append(PathFinder(valid_pos, start_pos))

        
        while children:
            remove_list = []
            for child in children:
                state = child.update()
                if state == 1:
                    return (child.pos[0] - start_pos[0], child.pos[1] - start_pos[1])
                elif state == -1:
                    remove_list.append(child)

            for child in remove_list:
                children.remove(child)

        return None

    @staticmethod
    def valid_neighbors(pos, last_pos):
        x, y = pos
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [neighbor for neighbor in neighbors if not neighbor == last_pos and PathFinder.valid_tile(neighbor, pos)]



    def __init__(self, pos, last_pos):
        self._children = []
        self._x = pos[0]
        self._y = pos[1]
        self.pos = pos
        self.last_pos = last_pos


    def update(self):
        # Get all valid positions for children
        children_pos = PathFinder.valid_neighbors(self.pos, self.last_pos)



        # If children have not yet been created (ie this is a new node)
        if not self._children:
            # If we occupy the player's position, flag this node
            if self.pos == Player.main.pos():
                return 1

            # If there are no valid moves from this child, delete this branch
            if not children_pos:
                return -1

            # Create children at all valid locations
            for child_pos in children_pos:
                if child_pos == Player.main.pos():
                    return 1
                else:
                    self._children.append(PathFinder(child_pos, self.pos))

            return 0


        remove_list = []
        for child in self._children:
            state = child.update()
            if state == 1:
                return 1
            elif state == -1:
                remove_list.append(child)

        for child in remove_list:
            self._children.remove(child)

        if not self._children:
            return -1

        return 0
