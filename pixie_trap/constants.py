import enum
import os
import wx

from wx.lib.newevent import NewEvent


BASE_DIR = os.path.dirname(__file__)


IMAGE_WILDCARD = "All files (*)|*|BMP files (*.bmp)|*.bmp|JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
JSON_WILDCARD = "JSON files (*.json)|*.json"
PXT_WILDCARD = "PXT files (*.pxt)|*.pxt"


EXPAND = wx.ALL | wx.EXPAND
CENTER_RIGHT = wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL


UpdateInspectorHitboxEvent, EVT_UPDATE_INSPECTOR_HITBOX = NewEvent()
UpdateInspectorSpriteEvent, EVT_UPDATE_INSPECTOR_SPRITE = NewEvent()


class State(enum.Enum):
    """These define the state of the :class:`Canvas`."""
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
