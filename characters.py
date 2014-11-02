from drawable import Drawable
from tiles import Tile, Empty
from event import Event
import config, csv, os


class Character (Drawable):
    char_map = {}

    @staticmethod
    def load_characters(num):
        with open(os.path.join('levels', 'level{}.csv').format(num), 'rb') as file_data:
            row_num = 0
            for row in csv.reader(file_data):
                for col, value in enumerate(row):
                    if value in char_map:
                        char_map[value](col, row_num)
                row_num += 1


    def __init__(self, img_path, x, y):
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
        if tx >= 0 and ty >= 0 and tx < config.LEVEL_WIDTH and ty < config.LEVEL_HEIGHT:

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
        if self._y + 1 < config.LEVEL_HEIGHT:
            self.fall()

    def fall(self):
        next_pos = (self._x, self._y+1)

        if not Tile.query(next_pos, 'standable') and not Tile.query(self.pos(), 'grabbable'):
            self.apply_move(0, 1)


class Player (Character):
    main = None

    def __init__(self, x, y):
        super(Player, self).__init__('t_android.gif', x, y)
        Player.main = self

    def at_exit(self):
        return (self._y == 0)

    def apply_move(self, dx, dy):
        super(Player, self).apply_move(dx, dy)
        Tile.tile_at(self.pos()).take()

    def dig(self, direction):
        x = self._x + direction
        y = self._y + 1

        if self._y < config.LEVEL_HEIGHT - 1:
            if Tile.query((x, y), 'diggable') and isinstance(Tile.tile_at((x, y-1)), Empty):
                Tile.tile_at((x,y)).hide()
                refill = Event(Tile.tile_at((x, y)).show, 120)

    def redraw(self):
        self.undraw()
        self.draw()


class Baddie (Character):
    def __init__(self, x, y):
        super(Baddie, self).__init__('t_red.gif', x, y)
        self.move_event = Event(self.move, 120, recurring=True)

    def move(self):
        # if player is above the baddie
        if Player.main.pos[1] > self._y:
            # find nearest ladder that leads to player's y position
            #row = [Tile.level[(20 / (self._y+1)) : (20 / (self._y+2))]]

            pass
        else:
            pass

char_map = {'P': Player,
            'B': Baddie}