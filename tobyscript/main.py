import importlib.resources as pkg_resources
import logging

import arcade
from arcade import Window
import pyglet
from digiformatter import logger as digilogger

import tobyscript.data.fonts
from tobyscript.views.screen import ScreenView

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS_CAP = 240
SCREEN_TITLE = "tobyscript"

for font in ["DTM-SANS.otf", "FNT-SANS.ttf", "FNT-PAPYRUS.ttf", "PIXELATED-WINGDINGS.ttf"]:
    with pkg_resources.path(tobyscript.data.fonts, font) as p:
        arcade.text.load_font(str(p))

# Set up logging
logger: logging.Logger = None
arcadelogger: logging.Logger = None

def setup_logging():
    global logger, arcadelogger
    logging.basicConfig(level=logging.INFO)
    dfhandler = digilogger.DigiFormatterHandler()
    dfhandlersource = digilogger.DigiFormatterHandler(showsource=True)

    logger = logging.getLogger("tobyscript")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(dfhandler)

    arcadelogger = logging.getLogger("arcade")
    arcadelogger.setLevel(logging.WARN)
    arcadelogger.handlers = []
    arcadelogger.propagate = False
    arcadelogger.addHandler(dfhandlersource)


class Game(Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate = 1 / FPS_CAP)

        self.initial_view = ScreenView()

    def setup(self):
        logger.info("Setting up view...")
        self.initial_view.setup()
        logger.info("Showing view...")
        self.show_view(self.initial_view)


def main():
    setup_logging()
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
