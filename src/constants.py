import enum
import wx

from wx.lib.newevent import NewEvent


IMAGE_WILDCARD = "JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
JSON_WILDCARD = "JSON files (*.json)|*.json"
SHG_WILDCARD = "SHG files (*.shg)|*.shg"


EXPAND = wx.ALL | wx.EXPAND
CENTER_RIGHT = wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL


UpdateInspectorHitboxEvent, EVT_UPDATE_INSPECTOR_HITBOX = NewEvent()
UpdateInspectorSpriteEvent, EVT_UPDATE_INSPECTOR_SPRITE = NewEvent()


class State(enum.Enum):
    SELECT = enum.auto()
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
