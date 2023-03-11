import logging
import importlib.resources as pkg_resources

import arcade
from arcade.experimental.crt_filter import CRTFilter
import arcade.key
import pyglet
from pymunk import Vec2d

import tobyscript.data
from tobyscript.lib.script import CloseEvent, EmotionEvent, FaceEvent, SkipEvent, SoundEvent, SpeakerEvent, WaitEvent, parse, Event, TextEvent, PauseEvent, ColorEvent, TextSizeEvent

logger = logging.getLogger("tobyscript")

pyglet.options["debug_font"] = True
pyglet.options["advanced_font_features"] = True


class ScreenView(arcade.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        window = arcade.get_window()

        self.crt_filter = CRTFilter(window.width, window.height,
                            resolution_down_scale=1.0,
                            hard_scan=-8.0,
                            hard_pix=-3.0,
                            display_warp = Vec2d(1.0 / 32.0, 1.0 / 18.0),
                            mask_dark=0.5,
                            mask_light=1.5)
        self.filter_on = False

        self.font_name = "Determination Mono"
        self._font_size = 30
        self.font_small = False
        self.font_color = arcade.color.WHITE
        self.sound_on = True

        self.speaker = 0
        self.emotion = 0
        self.face = 0

        with pkg_resources.path(tobyscript.data, "snd_txt1.wav") as p:
            self.beep: pyglet.media.StaticSource = pyglet.media.load(str(p.absolute()), streaming = False)
        with pkg_resources.path(tobyscript.data, "snd_phone.wav") as p:
            self.phone: pyglet.media.StaticSource = pyglet.media.load(str(p.absolute()), streaming = False)

        self.text_box: arcade.Sprite = None
        self.text_label: pyglet.text.DocumentLabel = None

        self.delay_per_character = 1 / 30
        self.paused = True
        self.debug = True

    def setup(self):
        with pkg_resources.path(tobyscript.data, "spr_message_box.png") as p:
            self.text_box = arcade.Sprite(p)
        self.text_box.center_x = self.window.width / 2
        self.text_box.center_y = self.window.height / 2
        self.document = pyglet.text.document.FormattedDocument("")
        self.text_label = pyglet.text.DocumentLabel(document = self.document,
            x = self.text_box.left, y = self.text_box.top,
            width = self.text_box.width, height = self.text_box.height,
            anchor_x = "left", anchor_y = "baseline", multiline = "True")

        self.recalc(1.5)

        self.lines: list[str] = ["* ENTRY NUMBER 5/",
            "s* I've done it./",
            "* Using the blueprints^1, I've&  extracted it from the&  human SOULs./",
            "* I believe this is what&  gives their SOULs the strength&  to persist after death./",
            "* The will to keep living..^1.&* The resolve to change fate./",
            "* Let's call this power.../&\\Y* \"Determination.\"/%%"]
        # self.lines: list[str] = ["* SOUL power can only be&  derived from what was&  once living./"]
        self.current_line = ""
        self.text_events: list[Event] = []

        self.debug_label = pyglet.text.Label(self.current_line, font_name="Determination Mono", font_size = 10,
            width = self.window.width,
            x = 5, y = 5, anchor_x = "left", anchor_y = "baseline", color = arcade.color.WHITE)

        self.emotion_label = pyglet.text.Label("Default [F0:E0]", font_name="Determination Mono", font_size = 10,
            width = self.window.width,
            x = 5, y = 20, anchor_x = "left", anchor_y = "baseline", color = arcade.color.WHITE)

        self._current_string = ""
        self._current_wait = 0.0
        self._current_pause = 0.0

        self.paused = True
        self.debug = True

        self.font_name = "Determination Mono"
        self._font_size = 30
        self.font_small = False
        self.font_color = arcade.color.WHITE
        self.sound_on = True
        self.show_box = False

        self.speaker = 0
        self.emotion = 0
        self.face = 0

    @property
    def font_size(self) -> float:
        return self.font_size * 0.75 if self.font_small else self._font_size

    def recalc(self, new_scale: float):
        self.text_box.scale = new_scale

        text_position = (28 * new_scale, 46 * new_scale)
        self._font_size = 20.5 * new_scale

        # self.text_label.text = self.text
        self.text_label.width = self.text_box.width - text_position[0]
        self.text_label.height = self.text_box.height - text_position[1]
        self.text_label.x = self.text_box.left + text_position[0]
        self.text_label.y = self.text_box.top - text_position[1]

    def push_char(self, c: str):
        self.document.insert_text(len(self.document.text), c, {
            "font_name": self.font_name,
            "font_size": self.font_size,
            "color": self.font_color})
        self.document.set_paragraph_style(0, len(self.document.text), {
            "margin_bottom": 4 * self.text_box.scale
        })
        if self.sound_on:
            self.beep.play()

    def setup_text(self):
        self.text_events = parse(self.current_line)
        self.debug_label.text = self.current_line
        self.font_color = arcade.color.WHITE
        self.speaker = "Default"
        self.emotion = 0
        self.face = 0
        self.font_name = "Determination Mono"
        logger.info(f"Displaying string: {self.current_line}")

    def next_line(self):
        self.document.delete_text(0, len(self.document.text))
        self.current_line = self.lines.pop(0)
        self.setup_text()

    def on_show_view(self):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.F and modifiers & arcade.key.MOD_CTRL:
            self.filter_on = not self.filter_on
        if symbol == arcade.key.ENTER:
            if self._current_string:
                return
            self.paused = False
            if not self.paused and self.lines:
                self.next_line()
        if symbol == arcade.key.D and modifiers & arcade.key.MOD_CTRL:
            self.debug = not self.debug
        if symbol == arcade.key.BACKSPACE:
            self.setup()

    def on_update(self, delta_time: float):
        if self.paused:
            return

        self._current_wait += delta_time

        if self._current_pause and self._current_pause < self._current_wait:
            self._current_pause = 0
        elif self._current_pause:
            return

        if not self._current_string:
            if self.text_events:
                event = self.text_events.pop(0)
                if isinstance(event, TextEvent):
                    if self.show_box is False:
                        self.show_box = True
                    self._current_string = event.data
                elif isinstance(event, PauseEvent):
                    self._current_pause = self.delay_per_character * event.data * 10
                elif isinstance(event, WaitEvent):
                    self.paused = True
                elif isinstance(event, ColorEvent):
                    self.font_color = event.rgba
                elif isinstance(event, TextSizeEvent):
                    self.font_small = event.small
                elif isinstance(event, SkipEvent):
                    self.next_line()
                elif isinstance(event, EmotionEvent):
                    self.emotion = event.data
                elif isinstance(event, FaceEvent):
                    self.face = event.data
                elif isinstance(event, SpeakerEvent):
                    self.speaker = event.speaker
                    if event.speaker == "Sans":
                        self.font_name = "Sans Undertale"
                    elif event.speaker == "Papryus":
                        self.font_name = "Papryus Pixel Mono"
                    else:
                        self.font_name = "Determination Mono"
                elif isinstance(event, SoundEvent):
                    if event.type == "phone":
                        self.phone.play()
                    else:
                        self.sound_on = True if event.data == "on" else False
                elif isinstance(event, CloseEvent):
                    self.setup()
                else:
                    logger.warn(f"Unknown event: {event}")
        else:
            if self._current_wait > self.delay_per_character:
                self.push_char(self._current_string[0])
                self._current_string = self._current_string[1:]
                self._current_wait = 0

        emotion_string = f"{self.speaker} [F{self.face}:E{self.emotion}]"
        if self.emotion_label.text != emotion_string:
            self.emotion_label.text = emotion_string

    def draw(self):
        if self.show_box:
            self.text_box.draw(pixelated=True)
        with self.window.ctx.pyglet_rendering():
            self.text_label.draw()
            if self.debug:
                self.debug_label.draw()
                self.emotion_label.draw()

    def on_draw(self):
        if self.filter_on:
            self.crt_filter.use()
            self.crt_filter.clear()
            self.draw()

            self.window.use()
            self.clear()
            self.crt_filter.draw()
        else:
            self.window.use()
            self.clear()
            self.draw()
