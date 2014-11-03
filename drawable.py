import os, time
from config import Config
from graphics import Image, Point, GraphWin, Text


class Drawable(object):
    _window = None

    @staticmethod
    def recreateWindow():
        if Drawable._window:
            Drawable._window.close()
        Drawable._window = GraphWin("LodeRunner", Config.WINDOW_WIDTH+20, Config.WINDOW_HEIGHT+20)
        Drawable._window.setBackground('white')

    @staticmethod
    def lost():
        t = Text(Point(Config.WINDOW_WIDTH/2+10, Config.WINDOW_HEIGHT/2+10), 'YOU LOST!')
        t.setSize(36)
        t.setTextColor('red')
        t.draw(Drawable._window)
        Drawable._window.getKey()
        exit(0)

    @staticmethod
    def won():
        t = Text(Point(Config.WINDOW_WIDTH/2+10, Config.WINDOW_HEIGHT/2+10), 'YOU WON!')
        t.setSize(36)
        t.setTextColor('red')
        t.draw(Drawable._window)
        time.sleep(2)

    def __init__(self, coords, img_path=None):
        if img_path:
            self._img = Image(Point((coords[0]+1)*Config.CELL_SIZE-1, (coords[1]+1)*Config.CELL_SIZE-1), os.path.join('graphics', img_path))
        else:
            self._img = None

    def draw(self):
        if self._img:
            self._img.draw(Drawable._window)

    def move_img(self, dx, dy):
        if self._img:
            self._img.move(dx * Config.CELL_SIZE, dy * Config.CELL_SIZE)

    def undraw(self):
        if self._img:
            self._img.undraw()
