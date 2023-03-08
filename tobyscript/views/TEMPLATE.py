import logging

import arcade

logger = logging.getLogger("tobyscript")


class TemplateView(arcade.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()

    def on_show_view(self):
        pass

    def on_update(self, delta_time):
        super().on_update(delta_time)
        pass

    def on_draw(self):
        self.clear()
        super().on_draw()
