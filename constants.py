import enum
import wx


EXPAND = wx.ALL | wx.EXPAND
CENTER_RIGHT = wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL


IMAGE_WILDCARD = "JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
JSON_WILDCARD = "JSON files (*.json)|*.json"


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
