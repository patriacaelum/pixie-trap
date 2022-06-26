from copy import deepcopy
from math import floor

import numpy as np
import wx

from pixie_trap.constants import (
    SpriteSelectedEvent, 
    UpdateHitboxEvent,
    Mode,
)
from pixie_trap.primitives import Point, Rect, Rects, ScaleRects


class Canvas(wx.Panel):
    """The canvas is where the image and hitboxes are drawn and edited.

    The canvas consists of the components:

    - background
    - spritesheet
    - rulers
    - hitboxes

    Parameters
    ------------
    parent: wx.Frame
        the parent window of the application.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        # wxpython settings
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Internal parameters
        self.left_down = Point()
        self.middle_down = Point()

        self.scale_select = None # A `Scale` value
        self.zoom_level = 0
        self.scale_factor = 1
        self.scale_rects = ScaleRects()

        self.mode = None
        self.isolate = False

        self.spritesheet = wx.Bitmap()
        self.spritesheet_bmp = wx.Bitmap()
        self.spritesheet_loaded = False
        self.spritesheet_pos = Rect()

        self.counter = 0
        self.destinations = Rects()
        self.hitbox_labels = {} # Maps a counter to a label
        self.hitbox_select = None
        self.hitboxes = {} # Maps a counter to bitmap
        self.indices = {} # Maps a counter to an index
        self.sprites = {} # Maps tuples (x, y) to a set of counters

        self.preview_bmp = wx.Bitmap() # A red bitmap covering the selection preview
        self.preview_pos = Rect()
        self.sprite_bg = wx.Bitmap() # A black bitmap covering the entire canvas
        self.sprite_labels = {} # Maps a tuple (x, y) to an label
        self.sprite_pos = Rect()
        self.sprite_select = None # A tuple (x, y)

        self.ruler_nrows = 1
        self.ruler_ncols = 1
        self.hrulers = np.array([])
        self.vrulers = np.array([])

        self.Bind(wx.EVT_LEFT_DOWN, self.__on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.__on_left_up)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.__on_middle_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self.__on_mousewheel)
        self.Bind(wx.EVT_MOTION, self.__on_motion)

        self.Bind(wx.EVT_PAINT, self.__on_paint)

    def load_json(self, data: dict):
        """Loads hitboxes from JSON.

        Parameters
        ------------
        data: dict
            the JSON data.
        """
        spritesheet = data["spritesheet"]
        self.set_rulers(rows=spritesheet["rows"], cols=spritesheet["cols"])

        sprites = data["sprites"]

        for sprite_label, sprite in sprites.items():
            location = sprite["location"]
            hitboxes = sprite["hitboxes"]

            key = (location["x"], location["y"])

            self.sprite_labels[key] = sprite_label
            counters = set()

            for hitbox_label, hitbox in hitboxes.items():
                counters.add(self.counter)
                self.hitbox_labels[self.counter] = hitbox_label
                self.indices[self.counter] = self.counter
                rect = Rect(
                    x=hitbox.get("x", 0),
                    y=hitbox.get("y", 0),
                    w=hitbox.get("w", 0),
                    h=hitbox.get("h", 0),
                )
                self.destinations.append(rect)
                self.hitboxes[self.counter] = wx.Bitmap.FromRGBA(
                    width=rect.w,
                    height=rect.h,
                    red=255,
                    green=0,
                    blue=0,
                    alpha=127,
                )

                self.counter += 1

            self.sprites[key] = counters

    def load_spritesheet(self, filepath: str):
        """Loads an image as a spritesheet.

        Parameters
        ------------
        filepath: str
            the path to the spritesheet file. 
        """
        self.spritesheet.LoadFile(name=filepath)
        self.__size_bitmaps()
        self.set_rulers(rows=1, cols=1)

        self.spritesheet_loaded = True

    def reset(self):
        """Resets the canvas to default parameters."""
        self.left_down = Point()
        self.middle_down = Point()

        self.zoom_level = 0
        self.scale_factor = 1

        self.mode = None
        self.isolate = False

        self.spritesheet_pos = Rect()
        self.spritesheet_loaded = False

        self.hitbox_select = None
        self.counter = 0
        self.sprites = {}
        self.hitbox_labels = {}
        self.indices = {}
        self.destinations = Rects()

        self.sprite_select = None
        self.sprite_labels = {}
        self.sprite_pos = Rect()
        self.preview_pos = Rect()

        self.ruler_nrows = 1
        self.ruler_ncols = 1
        self.hrulers = np.array([])
        self.vrulers = np.array([])

    def set_alpha(self, alpha: int):
        """Sets the alpha value for each hitbox.

        Parameters
        ------------
        alpha: int
            the alpha value is between 0 and 255, where 0 is fully transparent
            and 255 is fully opaque.
        """
        for bitmap in self.hitboxes.values():
            image = bitmap.ConvertToImage()
            image.SetAlpha(alpha)
            bitmap = image.ConvertToBitmap()

        self.Refresh()

    def set_rulers(self, rows: int = None, cols: int = None):
        """Sets the number of rulers and the size of the preview.

        Parameters
        ------------
        rows: int
            the number of rows in the spritesheet.
        cols: int
            the number of columns in the spritesheet.
        """
        if rows is not None:
            self.ruler_nrows = rows

        if cols is not None:
            self.ruler_ncols = cols

        self.hrulers = np.linspace(
            start=0, 
            stop=self.spritesheet_pos.h + 1, 
            num=self.ruler_nrows + 1
        )
        self.vrulers = np.linspace(
            start=0, 
            stop=self.spritesheet_pos.w + 1, 
            num=self.ruler_ncols + 1
        )
        self.__size_bitmaps()

    def to_dict(self):
        """Returns information about the canvas in a JSON compatible format.

        The JSON data is written in the format::

            {
                "spritesheet": {
                    "rows": int,
                    "cols": int,
                },
                "sprites": {
                    "sprite_label_0": {
                        "location": {
                            "x": int,
                            "y": int,
                        },
                        "hitboxes": {
                            "hitbox_label_0": {
                                "x": int,
                                "y": int,
                                "w": int,
                                "h": int,
                            },
                            "hitbox_label_1": {
                                ...
                            },
                        },
                    },
                    "sprite_label_1": {
                        ...
                    },
                    ...
                },
            }

        Returns
        ---------
        data: dict
            information about the canvas in a JSON compatible format.
        """

        data = {
            "spritesheet": {
                "rows": self.ruler_nrows,
                "columns": self.ruler_ncols,
            },
        }

        sprite_data = {}

        for sprite_location, counters in self.sprites.items():
            sprite_label = self.sprite_labels[sprite_location]

            hitboxes = {}

            for counter in counters:
                hitbox_label = self.hitbox_labels[counter]
                hitbox = self.destinations.get(counter)

                hitboxes[hitbox_label] = hitbox.to_dict()

            sprite_data[sprite_label] = {
                "location": {
                    "x": sprite_location[0],
                    "y": sprite_location[1],
                },
                "hitboxes": hitboxes,
            }


        data["sprites"] = sprite_data

        return data

    def to_json(self):
        """Returns the hitboxes as JSON.

        The JSON data has the structure::

            {
                "sprite_label_0": {
                    "sprite": {
                        "x": int,
                        "y": int,
                        "w": int,
                        "h": int
                    },
                    "hitboxes": {
                        "hitbox_label_0": {
                            "x": int,
                            "y": int,
                            "w": int,
                            "h": int,
                        }
                        "hitbox_label_1": {
                            ...
                        },
                        ...
                    }
                },
                "sprite_label_1": {
                    ...
                },
                ...
            }

        Returns
        ---------
        data: dict
            information about the hitboxes as JSON.
        """
        data = {}
        destinations = deepcopy(self.destinations)
        destinations.x = destinations.x * self.scale_factor - self.spritesheet_pos.x
        destinations.y = destinations.y * self.scale_factor - self.spritesheet_pos.y
        destinations.w /= self.scale_factor
        destinations.h /= self.scale_factor

        for sprite_location, counters in self.sprites.items():
            sprite_label = self.sprite_labels[sprite_location]

            hitboxes = {}

            for counter in counters:
                hitbox_label = self.hitbox_labels[counter]
                hitbox = destinations.get(counter)

                hitboxes[hitbox_label] = hitbox.to_dict()

            data[sprite_label] = {
                "sprite": {
                    "x": int(self.vrulers[sprite_location[0]]),
                    "y": int(self.hrulers[sprite_location[1]]),
                    "w": int(self.spritesheet.GetWidth() // self.ruler_ncols),
                    "h": int(self.spritesheet.GetHeight() // self.ruler_nrows),
                },
                "hitboxes": hitboxes,
            }

        return data

    def __create_hitbox(self):
        """Initializes drawing a hitbox."""
        label = f"hitbox_{self.counter}"
        hitbox = Rect(x=self.left_down.x, y=self.left_down.y, w=0, h=0)

        self.destinations.append(hitbox)
        self.indices[self.counter] = self.destinations.size() - 1
        self.hitbox_labels[self.counter] = label
        self.sprites[self.sprite_select].add(self.counter)

        self.hitbox_select = self.counter
        self.counter += 1

        wx.PostEvent(
            self.Parent,
            UpdateHitboxEvent(
                label=label,
                global_x=int((hitbox.x - self.spritesheet_pos.x) / self.scale_factor),
                global_y=int((hitbox.y - self.spritesheet_pos.y) / self.scale_factor),
                local_x=int((hitbox.x - self.sprite_pos.x) / self.scale_factor),
                local_y=int((hitbox.y - self.sprite_pos.y) / self.scale_factor),
                width=int(hitbox.w / self.scale_factor),
                height=int(hitbox.h / self.scale_factor),
            )
        )

    def __draw_hitbox(self, point: Point):
        """Draws a hitbox.

        Parameters
        ------------
        point: Point
            the location of the mouse.
        """
        dx = abs(point.x - self.left_down.x)
        dy = abs(point.y - self.left_down.y)

        dx_scale = floor(dx / self.scale_factor)
        dy_scale = floor(dy / self.scale_factor)

        if dx_scale <= 0 or dy_scale <= 0:
            return

        hitbox = Rect(
            x=min(self.left_down.x, point.x),
            y=min(self.left_down.y, point.y),
            w=dx,
            h=dy,
        )

        self.destinations.set(index=self.hitbox_select, rect=hitbox)
        self.hitboxes[self.hitbox_select] = wx.Bitmap.FromRGBA(
            width=dx,
            height=dy,
            red=255,
            green=0,
            blue=0,
            alpha=127,
        )

        wx.PostEvent(
            self.Parent,
            UpdateHitboxEvent(
                label=self.hitbox_labels[self.hitbox_select],
                global_x=int((hitbox.x - self.spritesheet_pos.x) / self.scale_factor),
                global_y=int((hitbox.y - self.spritesheet_pos.y) / self.scale_factor),
                local_x=int((hitbox.x - self.sprite_pos.x) / self.scale_factor),
                local_y=int((hitbox.y - self.sprite_pos.y) / self.scale_factor),
                width=int(hitbox.w / self.scale_factor),
                height=int(hitbox.h / self.scale_factor),
            )
        )

        self.Refresh()

    def __on_left_down(self, event: wx.MouseEvent):
        """Processes left mouse button presses.

        Parameters
        ------------
        event: wx.MouseEvent
            the event containing information about mouse button presses and
            releases and mouse movements.
        """
        self.left_down.set(*event.GetPosition())

        if self.mode == Mode.SELECT:
            self.__set_selection_zone()

        elif self.sprite_select is not None:
            if self.mode == Mode.MOVE:
                if self.hitbox_select is not None:
                    self.scale_select = self.scale_rects.select_scale(self.left_down)

                if self.scale_select is None:
                    self.__set_scaling_rects()

            elif self.mode == Mode.DRAW:
                self.__create_hitbox()

    def __on_left_up(self, event: wx.MouseEvent):
        """Processes left mouse button releases.

        Parameters
        ------------
        event: wx.MouseEvent
            the event containing information about mouse button presses and
            releases and mouse movements.
        """
        if self.mode == Mode.MOVE:
            self.scale_select = None

        elif self.mode == Mode.DRAW:
            w = int(self.destinations.w[self.hitbox_select])
            h = int(self.destinations.h[self.hitbox_select])

            if w == 0 or h == 0:
                self.destinations.delete(index=self.hitbox_select)
                del self.indices[self.hitbox_select]
                del self.hitbox_labels[self.hitbox_select]
                self.sprites[self.sprite_select].remove(self.hitbox_select)

            self.hitbox_select = None

    def __on_middle_down(self, event: wx.MouseEvent):
        """Processes middle moust button presses.

        Parameters
        ------------
        event: wx.MouseEvent
            the event containing information about mouse button presses and
            releases and mouse movements.
        """

        self.middle_down.set(*event.GetPosition())

    def __on_motion(self, event: wx.MouseEvent):
        """Processes mouse movements.

        Parameters
        ------------
        event: wx.MouseEvent
            the event containing information about mouse button presses and
            releases and mouse movements.
        """

        if self.mode == Mode.SELECT:
            point = Point(*event.GetPosition())
            self.__set_preview_zone(point=point)

        if event.LeftIsDown():
            if self.mode == Mode.MOVE and self.hitbox_select is not None:
                point = Point(*event.GetPosition())

                if self.scale_select is not None:
                    self.__scale_hitbox(point=point)

                else:
                    self.__translate_hitbox(point=point)

            elif self.mode == Mode.DRAW and self.hitbox_select is not None:
                point = Point(*event.GetPosition())
                self.__draw_hitbox(point=point)

        elif event.MiddleIsDown():
            point = Point(*event.GetPosition())
            self.__pan(point=point)

    def __on_mousewheel(self, event: wx.MouseEvent):
        """Zooms in or out of the canvas.

        The equation for calculating the scale factor is::

            (|x| + 1)^{\\frac{x}{|x|}}

        Parameters
        ------------
        event: wx.MouseEvent
            the event containing information about mouse button presses and
            releases and mouse movements.
        """
        if not self.spritesheet_loaded:
            return

        x, y = event.GetPosition()
        rotation = event.GetWheelRotation()

        # Update zoom level and scale factor
        if rotation > 0:
            self.zoom_level += 1
        
        elif rotation < 0:
            self.zoom_level -= 1

        old_factor = self.scale_factor

        if self.zoom_level == 0:
            self.scale_factor = 1
        
        else:
            self.scale_factor  = (abs(self.zoom_level) + 1) ** (self.zoom_level / abs(self.zoom_level))

        factor = self.scale_factor / old_factor

        # Update affected positions and bitmaps
        self.spritesheet_pos.set(
            x=x - factor * (x - self.spritesheet_pos.x),
            y=y - factor * (y - self.spritesheet_pos.y),
        )

        self.sprite_pos.set(
            x=x - factor * (x - self.sprite_pos.x),
            y=y - factor * (y - self.sprite_pos.y),
        )

        self.destinations.x = x - factor * (x - self.destinations.x)
        self.destinations.y = y - factor * (y - self.destinations.y)
        self.destinations.w *= factor
        self.destinations.h *= factor

        self.scale_rects.set(rect=self.destinations.get(self.indices[self.hitbox_select]))

        self.__size_bitmaps()
        self.set_rulers()

        self.Refresh()

    def __on_paint(self, event: wx.PaintEvent):
        """Repaints the canvas.

        Parameters
        ------------
        event: wx.PaintEvent
            a paint event is sent when the canvas's contents need to be
            repainted.
        """
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        # Paint spritesheet
        if self.spritesheet_loaded:
            gc.DrawBitmap(
                bmp=self.spritesheet_bmp, 
                **self.spritesheet_pos.to_dict(),
            )

            self.__paint_rulers(dc=dc)

        # Paint selection preview
        if self.mode == Mode.SELECT or self.sprite_select is not None:
            self.__paint_selection_zone(gc=gc)

        self.__paint_hitboxes(gc=gc)

        if self.mode == Mode.MOVE and self.hitbox_select is not None:
            self.__paint_scale_rects(gc=gc)

    def __paint_hitboxes(self, gc: wx.GraphicsContext):
        """Paints the hitboxes to the canvas.

        Parameters
        ------------
        gc: wx.GraphicsContext
            the object drawn upon.
        """ 
        for sprite, counters in self.sprites.items():
            if self.isolate and sprite != self.sprite_select:
                continue

            for index in counters:
                hitbox = self.destinations.get(index)

                if hitbox.w <= 0 or hitbox.h <= 0:
                    continue

                gc.DrawBitmap(
                    bmp=self.hitboxes[index],
                    **hitbox.to_dict(),
                )

    def __paint_rulers(self, dc: wx.DC):
        """Paints rulers on the canvas.

        Parameters
        ------------
        dc: wx.DC
            the device context where graphics are drawn.
        """
        # Set colour to cyan
        dc.SetPen(wx.Pen(colour=wx.Colour(0, 255, 255, 100), width=2))

        canvas_w, canvas_h = self.GetSize()

        hrulers = self.hrulers + self.spritesheet_pos.y
        rows = np.zeros(shape=(self.ruler_nrows + 1, 4), dtype=int)
        rows[:, 1] = hrulers
        rows[:, 2] = canvas_w
        rows[:, 3] = hrulers

        vrulers = self.vrulers + self.spritesheet_pos.x
        cols = np.zeros(shape=(self.ruler_ncols + 1, 4), dtype=int)
        cols[:, 0] = vrulers
        cols[:, 2] = vrulers
        cols[:, 3] = canvas_h

        dc.DrawLineList(rows.tolist())
        dc.DrawLineList(cols.tolist())

    def __paint_scale_rects(self, gc: wx.GraphicsContext):
        """Paints the scale rectangles on the selected hitbox.

        The scaling pins are always the same size on the canvas, independent of
        the zoom level. The scaling pins consist of a circle in the centre of
        the hitbox and squares on each corner and midpoint around the
        perimeter.

        Parameters
        ------------
        gc: wx.GraphicsContext
            the object drawn upon.
        """
        gc.SetPen(wx.Pen(colour=wx.Colour(0, 0, 0, 255), width=2))

        hitbox = self.destinations.get(self.indices[self.hitbox_select])
        centre = hitbox.centre

        # Draw a circle in the centre of the hitbox
        gc.DrawEllipse(
            x=centre.x,
            y=centre.y,
            w=20,
            h=20,
        )

        # Draw squares on each corner and midpoint
        for index in self.scale_rects.keys.values():
            gc.DrawRectangle(**self.scale_rects.rects.get(index).to_dict())

    def __paint_selection_zone(self, gc: wx.GraphicsContext):
        """Paints the selection zone.

        Parameters
        ------------
        gc: wx.GraphicsContext
            the object drawn upon.
        """
        w = self.sprite_bg.GetWidth()
        h = self.sprite_bg.GetHeight()

        if self.sprite_select is None:
            # Darken the entire canvas
            gc.DrawBitmap(bmp=self.sprite_bg, x=0, y=0, w=w, h=h)

        else:
            # Darken everywhere except the selection zone

            # Top left
            gc.DrawBitmap(
                bmp=self.sprite_bg,
                x=self.sprite_pos.x + self.sprite_pos.w - w,
                y=self.sprite_pos.y - h,
                w=w,
                h=h,
            )

            # Top right
            gc.DrawBitmap(
                bmp=self.sprite_bg,
                x=self.sprite_pos.x + self.sprite_pos.w,
                y=self.sprite_pos.y + self.sprite_pos.h - h,
                w=w,
                h=h,
            )

            # Bottom right
            gc.DrawBitmap(
                bmp=self.sprite_bg,
                x=self.sprite_pos.x,
                y=self.sprite_pos.y + self.sprite_pos.h,
                w=w,
                h=h,
            )

            # Bottom left
            gc.DrawBitmap(
                bmp=self.sprite_bg,
                x=self.sprite_pos.x - w,
                y=self.sprite_pos.y,
                w=w,
                h=h,
            )

        if self.preview_pos.x > 0 and self.preview_pos.y > 0:
            # Redden selection zone preview
            gc.DrawBitmap(
                bmp=self.preview_bmp,
                x=self.preview_pos.x,
                y=self.preview_pos.y,
                w=self.preview_pos.w,
                h=self.preview_pos.h,
            )

    def __pan(self, point: Point):
        """Moves all drawn objects.

        Parameters
        ------------
        point: Point
            the location of the mouse.
        """
        dx = point.x - self.middle_down.x
        dy = point.y - self.middle_down.y

        self.spritesheet_pos.move(dx=dx, dy=dy)

        if self.sprite_select is not None:
            self.sprite_pos.move(dx=dx, dy=dy)

        self.destinations.move(dx=dx, dy=dy)

        if self.hitbox_select is not None:
            self.scale_rects.move(dx=dx, dy=dy)

        self.middle_down.set(**point.to_dict())

        self.Refresh()

    def __scale(self, bitmap: wx.Bitmap):
        """Scales a bitmap to the current scale factor."""
        return (
            bitmap.ConvertToImage()
                .Scale(
                    width=int(bitmap.GetWidth() * self.scale_factor),
                    height=int(bitmap.GetHeight() * self.scale_factor),
                )
                .ConvertToBitmap()
        )

    def __set_preview_zone(self, point: Point):
        """Find the preview zone given the mouse coordinates.

        Parameters
        ------------
        point: Point
            the location of the mouse.
        """
        vrulers = self.vrulers + self.spritesheet_pos.x
        hrulers = self.hrulers + self.spritesheet_pos.y

        # Find which rectangle in the grid contains (x, y)
        x_in = np.logical_and(vrulers[:-1] <= point.x, point.x < vrulers[1:])
        y_in = np.logical_and(hrulers[:-1] <= point.y, point.y < hrulers[1:])

        # Define the rectangle parameters
        rect_x = np.sum(x_in * vrulers[:-1])
        rect_y = np.sum(y_in * hrulers[:-1])
        rect_w = np.sum(x_in * vrulers[1:]) - rect_x
        rect_h = np.sum(y_in * hrulers[1:]) - rect_y

        self.preview_pos.set(x=rect_x, y=rect_y, w=rect_w, h=rect_h)

        self.Refresh()

    def __set_scaling_rects(self):
        """Find a hitbox in the mouse position."""
        x_in = np.logical_and(
            self.destinations.x <= self.left_down.x,
            self.left_down.x <= self.destinations.x + self.destinations.w,
        )
        y_in = np.logical_and(
            self.destinations.y <= self.left_down.y,
            self.left_down.y <= self.destinations.y + self.destinations.h,
        )
        left_down_in = np.logical_and(x_in, y_in)

        for counter in self.sprites[self.sprite_select]:
            if left_down_in[self.indices[counter]]:
                self.hitbox_select = counter
                hitbox = self.destinations.get(self.hitbox_select)
                self.scale_rects.set(rect=hitbox)

                wx.PostEvent(
                    self.Parent,
                    UpdateHitboxEvent(
                        label=self.hitbox_labels[self.hitbox_select],
                        global_x=int((hitbox.x - self.spritesheet_pos.x) / self.scale_factor),
                        global_y=int((hitbox.y - self.spritesheet_pos.y) / self.scale_factor),
                        local_x=int((hitbox.x - self.sprite_pos.x) / self.scale_factor),
                        local_y=int((hitbox.y - self.sprite_pos.y) / self.scale_factor),
                        width=int(hitbox.w / self.scale_factor),
                        height=int(hitbox.h / self.scale_factor),
                    )
                )

                self.Refresh()

                break

    def __set_selection_zone(self):
        """Sets the selection zone from the preview zone."""
        # Select the rectangle currently hovered over
        self.sprite_pos.set(**self.preview_pos.to_dict())

        # Ignore mouse clicks outside the spritesheet
        if self.sprite_pos.w <= 0 or self.sprite_pos.h <= 0:
            self.sprite_select = None

            return

        # Selection is indices of spritesheet
        self.sprite_select = (
            int(self.sprite_pos.x // (self.spritesheet_pos.w // self.ruler_ncols)), 
            int(self.sprite_pos.y // (self.spritesheet_pos.h // self.ruler_nrows)),
        )

        if self.sprite_labels.get(self.sprite_select) is None:
            self.sprite_labels[self.sprite_select] = f"x{self.sprite_select[0]}_y{self.sprite_select[1]}"

        if self.sprites.get(self.sprite_select) is None:
            self.sprites[self.sprite_select] = set()

        wx.PostEvent(self.Parent, SpriteSelectedEvent(label=self.sprite_labels[self.sprite_select]))

        self.Refresh()

    def __scale_hitbox(self, point: Point):
        """Scales a hitbox.

        Parameters
        ------------
        point: Point
            the position of the mouse.
        """
        dx = point.x - self.left_down.x
        dy = point.y - self.left_down.y

        dx_scale = floor(dx / self.scale_factor)
        dy_scale = floor(dy / self.scale_factor)

        if dx_scale == 0:
            dx = 0

        if dy_scale == 0:
            dy = 0

        index = self.indices[self.hitbox_select]
        hitbox = self.destinations.get(index=index)
        hitbox.scale(scale=self.scale_select, dx=dx, dy=dy)
        self.destinations.set(index=index, rect=hitbox)

        self.left_down.move(dx=dx, dy=dy)
        self.scale_rects.set(hitbox)

        wx.PostEvent(
            self.Parent,
            UpdateHitboxEvent(
                label=self.hitbox_labels[self.hitbox_select],
                global_x=int((hitbox.x - self.spritesheet_pos.x) / self.scale_factor),
                global_y=int((hitbox.y - self.spritesheet_pos.y) / self.scale_factor),
                local_x=int((hitbox.x - self.sprite_pos.x) / self.scale_factor),
                local_y=int((hitbox.y - self.sprite_pos.y) / self.scale_factor),
                width=int(hitbox.w / self.scale_factor),
                height=int(hitbox.h / self.scale_factor),
            )
        )

        self.Refresh()

    def __size_bitmaps(self):
        """Resizes the bitmaps based on the zoom level."""
        self.spritesheet_bmp = self.__scale(self.spritesheet)

        spritesheet_w = self.spritesheet_bmp.GetWidth()
        spritesheet_h = self.spritesheet_bmp.GetHeight()

        self.spritesheet_pos.set(w=spritesheet_w, h=spritesheet_h)

        select_w = int(spritesheet_w // self.ruler_ncols)
        select_h = int(spritesheet_h // self.ruler_nrows)

        self.preview_bmp = wx.Bitmap.FromRGBA(
            width=select_w,
            height=select_h,
            red=255,
            green=0,
            blue=0,
            alpha=127,
        )
        self.sprite_pos.set(w=select_w, h=select_h)

        canvas_w, canvas_h = self.GetSize()

        self.sprite_bg = wx.Bitmap.FromRGBA(
            width=canvas_w,
            height=canvas_h,
            red=0,
            green=0,
            blue=0,
            alpha=127,
        )

    def __translate_hitbox(self, point: Point):
        """Translates a hitbox.
        
        Parameters
        ------------
        point: Point
            the position of the mouse.
        """
        dx = point.x - self.left_down.x
        dy = point.y - self.left_down.y

        dx_scale = floor(dx / self.scale_factor)
        dy_scale = floor(dy / self.scale_factor)

        index = self.indices[self.hitbox_select]

        if dx_scale == 0:
            dx = 0

        if dy_scale == 0:
            dy = 0

        self.destinations.move_rect(
            index=index,
            dx=dx,
            dy=dy,
        )
        self.left_down.move(dx=dx, dy=dy)
        self.scale_rects.set(rect=self.destinations.get(index))

        hitbox = self.destinations.get(index=index)

        wx.PostEvent(
            self.Parent,
            UpdateHitboxEvent(
                label=self.hitbox_labels[self.hitbox_select],
                global_x=int((hitbox.x - self.spritesheet_pos.x) / self.scale_factor),
                global_y=int((hitbox.y - self.spritesheet_pos.y) / self.scale_factor),
                local_x=int((hitbox.x - self.sprite_pos.x) / self.scale_factor),
                local_y=int((hitbox.y - self.sprite_pos.y) / self.scale_factor),
                width=int(hitbox.w / self.scale_factor),
                height=int(hitbox.h / self.scale_factor),
            )
        )

        self.Refresh()
