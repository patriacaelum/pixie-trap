import enum
import os
import wx

from wx.lib.newevent import NewEvent


BASE_DIR = os.path.dirname(__file__)


IMAGE_WILDCARD = "All files (*)|*|BMP files (*.bmp)|*.bmp|JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
JSON_WILDCARD = "JSON files (*.json)|*.json"
PXT_WILDCARD = "PXT files (*.pxt)|*.pxt"


ALL_EXPAND = wx.ALL | wx.EXPAND
CENTER_RIGHT = wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL


UpdateHitboxEvent, EVT_UPDATE_HITBOX = NewEvent()
SpriteSelectedEvent, EVT_SPRITE_SELECTED = NewEvent()


class Mode(enum.Enum):
    """These define the mode of the :class:`Canvas`."""

    SELECT = enum.auto()
    MOVE = enum.auto()
    DRAW = enum.auto()


class Scale(enum.Enum):
    """These define the possible scaling transformations that can be applied."""

    TOP = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    BOTTOM = enum.auto()
    TOP_LEFT = enum.auto()
    TOP_RIGHT = enum.auto()
    BOTTOM_LEFT = enum.auto()
    BOTTOM_RIGHT = enum.auto()
