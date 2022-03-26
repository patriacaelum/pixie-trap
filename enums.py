import enum


class State(enum.Enum):
    MOVE = enum.auto()
    DRAW = enum.auto()


class Scale(enum.Enum):
    TOP = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    BOTTOM = enum.auto()
    TOP_LEFT = enum.auto()
    TOP_RIGHT = enum.auto()
    BOTTOM_LEFT = enum.auto()
    BOTTOM_RIGHT = enum.auto()
