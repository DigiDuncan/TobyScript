import collections
import json
import re
from types import NoneType
from typing import Literal, Optional, TypedDict, cast

RGB = tuple[int, int, int]
RGBA = tuple[int, int, int, int]

def flatten(x):
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


class Settings(TypedDict):
    """
    * `char_name`: replaces `\\[C]`
    * `g`: replaces `\\[G]`
    * `item`: replaces `\\[I]`
    * `one`: replaces `\\[1]`
    * `two`: replaces `\\[2]`
    """
    char_name: str
    g: str
    item: str
    one: str
    two: str


# SETTINGS
settings: Settings = {
    "char_name": "Player",
    "g": "0",
    "item": "Monster Candy",  # item ID 1
    "one": "0",
    "two": "0",
    "fix_black": True
}


class Event:
    def __init__(self, data: str | int | None = None):
        self.data = data

    def __str__(self) -> str:
        data = repr(self.data) if self.data is not None else ''
        data = data.replace("\n", "\\n")
        return f"<{self.__class__.__name__} {data}".strip() + ">"

    def __repr__(self) -> str:
        return self.__str__()

class TextEvent(Event):
    def __init__(self, data: str):
        """Represents text to display on the screen."""
        super().__init__(data)
        self.data = cast(str, self.data)

class PauseEvent(Event):
    def __init__(self, data: int):
        """Delays an amount of time before continuing."""
        super().__init__(data)
        self.data = cast(int, self.data)

class ColorEvent(Event):
    def __init__(self, data: str):
        """Changes the color of upcoming text.

        * `self.name`: `str` - the name of the color.
        * `self.rgba`: `tuple` - the color as an RGBA tuple (as rendered in Undertale).
        * `self.rgb`: `tuple` - the color as an RGB tuple (as rendered in Undertale).
        """
        super().__init__(data)
        self.data = cast(str, self.data)

    @property
    def name(self) -> str:
        match self.data:
            case "R":
                return "red"
            case "G":
                return "green"
            case "W":
                return "white"
            case "Y":
                return "yellow"
            case "X":
                return "white" if settings["fix_black"] else "black"
            case "B":
                return "blue"
            case "O":
                return "orange"
            case "L":
                return "azure"
            case "P":
                return "magenta"
            case "p":
                return "pink"

    @property
    def rgba(self) -> RGBA:
        match self.data:
            case "R":
                return (0xFF, 0x00, 0x00, 0xFF)
            case "G":
                return (0x00, 0xFF, 0x00, 0xFF)
            case "W":
                return (0xFF, 0xFF, 0xFF, 0xFF)
            case "Y":
                return (0xFF, 0xFF, 0x00, 0xFF)
            case "X":
                return (0xFF, 0xFF, 0xFF, 0xFF) if settings["fix_black"] else (0x00, 0x00, 0x00, 0xFF)
            case "B":
                return (0x00, 0x00, 0xFF, 0xFF)
            case "O":
                return (0xFF, 0xA0, 0x40, 0xFF)
            case "L":
                return (0x0E, 0xC0, 0xFD, 0xFF)
            case "P":
                return (0xFF, 0x00, 0xFF, 0xFF)
            case "p":
                return (0xFF, 0xBB, 0xD4, 0xFF)

    @property
    def rgb(self) -> RGB:
        return self.rgba[:2]

class EmotionEvent(Event):
    def __init__(self, data: int):
        """Denotes an emotion for the character on screen (if any) to display."""
        super().__init__(data)

class FaceEvent(Event):
    def __init__(self, data: int):
        """Denotes a character's face to display on screen."""
        super().__init__(data)
        self.data = cast(int, self.data)

    @property
    def character(self) -> str | None:
        match self.data:
            case 0:
                return None
            case 1:
                return "Toriel"
            case 2:
                return "Flowey"
            case 3:
                return "Sans"
            case 4:
                return "Papyrus"
            case 5:
                return "Undyne"
            case 6:
                return "Alphys"
            case 7:
                return "Asgore"
            case 8:
                return "Mettaton"
            case 9:
                return "Asriel"

class SoundEvent(Event):
    def __init__(self, data: str):
        """Manipulate the current sound in some way.

        * `self.type`: `str` - The type of event this is:
            - `on`: text beeps on
            - `off`: text beeps off
            - `phone`: play phone sfx
        """
        super().__init__(data)
        self.data = cast(str, self.data)

    @property
    def type(self) -> str:
        match self.data:
            case "-":
                return "off"
            case "+":
                return "on"
            case "p":
                return "phone"

class TextSizeEvent(Event):
    def __init__(self, data: str):
        """Change the upcoming text size.

        `self.small`: `bool` - whether or not we're changing the text size to small (or normal, if False.)"""
        super().__init__(data)
        self.data = cast(str, self.data)

    @property
    def small(self) -> bool:
        return True if self.data == "-" else False

class SpeakerEvent(Event):
    def __init__(self, data: str):
        """Change the current speaker. Used to change text beep sound, typically.

        * `self.speaker`: the name of the speaker (as listed in Undertale Dialog Simulator.)
        """
        super().__init__(data)
        self.data = cast(str, self.data)

    @property
    def speaker(self) -> str:
        match self.data:
            case "T":
                return "Toriel"
            case "t":
                return "Toriel (Sans)"
            case "0":
                return "Default"
            case "S":
                return "Default (no sound)"
            case "F":
                return "Flowey (evil)"
            case "s":
                return "Sans"
            case "P":
                return "Papryus"
            case "M":
                return "Mettaton"
            case "U":
                return "Undyne"
            case "A":
                return "Alphys"
            case "a":
                return "Asgore"
            case "R":
                return "Asriel"

class WaitEvent(Event):
    def __init__(self):
        """Wait for user input."""
        super().__init__()
        self.data = cast(NoneType, self.data)

class SkipEvent(Event):
    def __init__(self):
        """Continue to the next text box (or rather, clear the current box contents.)"""
        super().__init__()
        self.data = cast(NoneType, self.data)

class CloseEvent(Event):
    def __init__(self):
        """Close the current text box. (Usually denotes the end of an interaction, but not always!)"""
        super().__init__()
        self.data = cast(NoneType, self.data)

def parse(s: str) -> list[Event]:
    """Take a TobyScript string and return an ordered list of Events."""
    events: list[Event] = []
    current_string = ""

    s = s.replace("\\>1", " ").replace("\\z4", "∞").replace("&", "\n").replace("\\C", "")\
        .replace("\\*Z", "[Z]").replace("\\*X", "[X]").replace("\\*C", "[C]").replace("\\*A", "[A]")\
        .replace("\\*D", "[D]").replace("\\[C]", settings["char_name"]) \
                               .replace("\\[I]", settings["item"]) \
                               .replace("\\[G]", settings["g"]) \
                               .replace("\\[1]", settings["one"]) \
                               .replace("\\[2]", settings["two"]).rstrip()

    current_string = ""
    skip = False
    for i in range(len(s)):
        current_char = s[i]

        if skip:
            skip = False
            continue

        # You have to have that % check because both % and %% are flags.
        if current_char in "^\\/&%" and current_string != "%":
            if current_string:
                events.append(TextEvent(current_string))
            current_string = ""

        current_string += current_char

        if re.match(r"\^\d", current_string):
            # Handle the weird postfix thing
            if i != len(s) - 1 and events and isinstance(events[-1], TextEvent):
                events[-1].data += s[i + 1]
                skip = True
            events.append(PauseEvent(int(current_string[1])))
            current_string = ""
        elif re.match(r"\\[RGWYXBOLPp]", current_string):
            events.append(ColorEvent(current_string[1]))
            current_string = ""
        elif re.match(r"\\E\d", current_string):
            events.append(EmotionEvent(int(current_string[2])))
            current_string = ""
        elif re.match(r"\\F\d", current_string):
            events.append(FaceEvent(int(current_string[2])))
            current_string = ""
        elif re.match(r"\\S[-+p]", current_string):
            events.append(SoundEvent(current_string[2]))
            current_string = ""
        elif re.match(r"\\T[-+]", current_string):
            events.append(TextSizeEvent(current_string[2]))
            current_string = ""
        elif re.match(r"\\T\w", current_string):
            events.append(SpeakerEvent(current_string[2]))
            current_string = ""
        elif current_string == "/":
            events.append(WaitEvent())
            current_string = ""
        elif re.match(r"%[^%]+", current_string) or (current_string == "%" and i == len(s) - 1):
            events.append(SkipEvent())
            current_string = ""
        elif current_string == "%%":
            events.append(CloseEvent())

    return events

def parse_lines(s: str, *, split_on: Optional[str] = None, merge: Literal["none", "close", "all"] = "none") -> list[list[Event]]:
    """Parse multiple TobyScript strings into an ordered list of ordered lists of Events.

    * s: `str` - The lines to parse.
    * split_on: `str` - The sequence to `.split()` the string with to denote line breaks. If `None`, defaults to calling `.splitlines()`.
    * merge: `str` - One of either `'none'`, `'close'`, or `'all'`.
    `none` returns the lists split as they were by the split functions.
    `close` returns the lists delimited by `CloseEvent`s.
    `all` returns a sequence of length 1, where all events are combined into one list."""
    event_lists = []

    if split_on is None:
        lines = s.splitlines()
    else:
        lines = s.split(split_on)

    for line in lines:
        parsed_line = parse(line)
        event_lists.append(parsed_line)

    if merge == "none":
        return event_lists
    if merge == "all":
        return [flatten(event_lists)]
    elif merge == "close":
        return_lists = []
        flattened = flatten(event_lists)
        current_list = []
        for event in flattened:
            current_list.append(event)
            if isinstance(event, CloseEvent):
                return_lists.append(current_list)
                current_list = []
        return return_lists

def to_JSON(li: list[Event], **kwargs) -> str:
    """Create a JSON-serializable version of a list of `Event`s."""
    out = []
    for e in li:
        d = {}
        d["type"] = e.__class__.__name__
        d["data"] = e.data
        out.append(d)
    return json.dumps(out, **kwargs)

def test(s: str):
    e = parse(s)
    print(e)


if __name__ == "__main__":
    test(R"\W* Howdy^2!&* I'm\Y FLOWEY\W.^2 &* \YFLOWEY\W the \YFLOWER\W!/")
