import json
import numpy as np
import os
import shutil
import wx

from constants import State
from constants import UpdateInspectorHitboxEvent, UpdateInspectorSpriteEvent
from primitives import Point, Rect, Sprite, ScaleRects


class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.bmp_loaded = False
        self.isolate = False
        self.saved = True
        self.state = None

        self.magnify = 1
        self.magnify_factor = 1

        self.left_down = Point()
        self.middle_down = Point()

        self.bg_colour = wx.Colour(128, 128, 128, 255)

        self.bmp = wx.Bitmap()
        self.bmp_position = Rect()
        self.rows = 1
        self.cols = 1

        self.select = None
        self.select_position = Rect()
        self.select_preview = Rect()

        self.sprites = dict()
        self.n_hitboxes_created = 0
        self.hitbox_buffer = Point()
        self.hitbox_colour = wx.Colour(255, 50, 0, 50)
        self.hitbox_select = None

        self.scale_select = None
        self.scale_radius = 5
        self.scale_rects = ScaleRects()
        
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)

        self.Bind(wx.EVT_MIDDLE_DOWN, self.onMiddleDown)

        self.Bind(wx.EVT_MOTION, self.onMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)

        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaintCanvas)

    def ExportJSON(self, filepath):
        """Exports the current canvas as JSON to disk."""
        data = {
            sprite.label: {
                hitbox.label: {
                    "x": hitbox.x - self.select_position.x,
                    "y": hitbox.y - self.select_position.y,
                    "w": hitbox.w,
                    "h": hitbox.h,
                }
                for hitbox in sprite.hitboxes.values()
            }
            for sprite in self.sprites.values()
        }

        try:
            with open(filepath, "w") as file:
                json.dump(data, file)
        except IOError:
            wx.LogError(f"Failed to save file in {filepath}")

    def FindSelectionZone(self, x, y):
        """Finds the selection zone on the canvas.

        If no selection zone is found, `None` is returned.
        """
        x = (x - self.bmp_position.x) // self.magnify_factor
        y = (y - self.bmp_position.y) // self.magnify_factor
        w, h = self.bmp.GetSize()

        vrulers = np.arange(
            start=0, 
            stop=w + 1, 
            step=int(w // self.cols),
        )
        hrulers = np.arange(
            start=0,
            stop=h + 1, 
            step=int(h // self.rows)
        )

        x_in = np.logical_and(vrulers[:-1] <= x, x < vrulers[1:])
        y_in = np.logical_and(hrulers[:-1] <= y, y < hrulers[1:])

        rect_x = np.sum(x_in * vrulers[:-1])
        rect_y = np.sum(y_in * hrulers[:-1])
        rect_w = np.sum(x_in * vrulers[1:]) - rect_x
        rect_h = np.sum(y_in * hrulers[1:]) - rect_y

        return rect_x, rect_y, rect_w, rect_h

    def LoadImage(self, path):
        """Reads and loads an image file to the canvas."""
        self.bmp.LoadFile(name=path)
        self.bmp_position.Set(
            x=0, 
            y=0, 
            w=self.bmp.GetWidth(), 
            h=self.bmp.GetHeight()
        )

        self.magnify = 1
        self.magnify_factor = 1

        self.bmp_loaded = True
        self.saved = False

    def LoadPXT(self, filepath):
        """Loads data from a PXT file into the current canvas."""
        temp_dir = filepath + ".temp"
        canvas_filepath = os.path.join(temp_dir, "canvas.bmp")
        data_filepath = os.path.join(temp_dir, "data.json")

        # Decompress data into a temporary directory
        shutil.unpack_archive(
            filename=filepath,
            extract_dir=temp_dir,
            format="gztar",
        )

        with open(data_filepath, "r") as file:
            data = json.load(file)

        # Load data into the canvas
        self.LoadImage(canvas_filepath)

        spritesheet_properties = data["spritesheet_properties"]
        sprite_properties = data["sprite_properties"]

        self.rows = spritesheet_properties["spritesheet_rows"]
        self.cols = spritesheet_properties["spritesheet_cols"]

        self.sprites = dict()

        for sprite_label, sprite in sprite_properties.items():
            sprite_key = tuple(sprite["sprite_key"])

            self.sprites[sprite_key] = Sprite(sprite_label)

            for hitbox_key, hitbox in sprite["hitboxes"].items():
                self.sprites[sprite_key].hitboxes[hitbox_key] = Rect(
                    x=hitbox["x"],
                    y=hitbox["y"],
                    w=hitbox["w"],
                    h=hitbox["h"],
                    label=hitbox["label"],
                )

        # Remove temporary directory
        shutil.rmtree(temp_dir)

        self.bmp_loaded = True
        self.saved = False

    def PaintBMP(self, gc):
        """Paints the loaded image to the canvas."""
        w, h = self.bmp.GetSize()

        gc.DrawBitmap(
            bmp=self.bmp,
            x=self.bmp_position.x,
            y=self.bmp_position.y,
            w=w * self.magnify_factor,
            h=h * self.magnify_factor,
        )

    def PaintHitboxes(self, gc):
        """Paints the drawn hitboxes to the canvas."""
        for sprite_label, sprite in self.sprites.items():
            if self.isolate and sprite_label != self.select:
                continue

            for hitbox in sprite.hitboxes.values():
                if hitbox.w <= 0 or hitbox.h <= 0:
                    continue

                bmp = wx.Bitmap.FromRGBA(
                    width=hitbox.w,
                    height=hitbox.h,
                    red=self.hitbox_colour.red,
                    green=self.hitbox_colour.green,
                    blue=self.hitbox_colour.blue,
                    alpha=self.hitbox_colour.alpha,
                )

                gc.DrawBitmap(
                    bmp=bmp,
                    x=int(self.bmp_position.x + hitbox.x * self.magnify_factor),
                    y=int(self.bmp_position.y + hitbox.y * self.magnify_factor),
                    w=int(hitbox.w * self.magnify_factor),
                    h=int(hitbox.h * self.magnify_factor),
                )

    def PaintRulers(self, dc):
        """Paints the rulers on the canvas."""
        dc.SetPen(wx.Pen(
            colour=wx.Colour(0, 255, 255, 100),
            width=2
        ))

        canvas_width, canvas_height = self.GetSize()

        vspace = int(self.bmp_position.h // self.rows)
        hspace = int(self.bmp_position.w // self.cols)

        dc.DrawLineList([
            (0, self.bmp_position.y + y, canvas_width, self.bmp_position.y + y)
            for y in range(0, self.bmp_position.h + 1, vspace)
        ])

        dc.DrawLineList([
            (self.bmp_position.x + x, 0, self.bmp_position.x + x, canvas_height)
            for x in range(0, self.bmp_position.w + 1, hspace)
        ])

    def PaintScale(self, gc):
        """Paints the transformation scaling pins on the selected hitbox."""
        gc.SetPen(wx.Pen(
            colour=wx.Colour(0, 0, 0, 100),
            width=2
        ))
        hitbox = self.sprites[self.select].hitboxes[self.hitbox_select]

        gc.DrawEllipse(
            x=int(self.bmp_position.x + hitbox.centre.x * self.magnify_factor - self.scale_radius),
            y=int(self.bmp_position.y + hitbox.centre.y * self.magnify_factor - self.scale_radius),
            w=int(2 * self.scale_radius),
            h=int(2 * self.scale_radius),
        )

        self.scale_rects.Set(
            rect=hitbox,
            radius=self.scale_radius,
            factor=self.magnify_factor,
        )

        for rectangle in self.scale_rects.rects.values():
            gc.DrawRectangle(
                x=self.bmp_position.x + rectangle.x,
                y=self.bmp_position.y + rectangle.y,
                w=rectangle.w,
                h=rectangle.h,
            )

    def PaintSelect(self, gc):
        """Paints the selection zone.

        If there is no selection zone, then the whole canvas is darkened.
        """
        w, h = self.GetSize()

        if not self.select:
            # Darken entire canvas
            bmp = wx.Bitmap.FromRGBA(
                width=w,
                height=h,
                red=0,
                green=0,
                blue=0,
                alpha=100,
            )

            gc.DrawBitmap(
                bmp=bmp,
                x=0,
                y=0,
                w=w,
                h=h,
            )

        else:
            # Darken everywhere except selection zone
            top_left = Point(
                x=self.bmp_position.x + self.select_position.x * self.magnify_factor, 
                y=self.bmp_position.y + self.select_position.y * self.magnify_factor,
            )
            top_right = Point(
                x=self.bmp_position.x + (self.select_position.x + self.select_position.w) * self.magnify_factor, 
                y=self.bmp_position.y + self.select_position.y * self.magnify_factor,
            )
            bottom_left = Point(
                x=self.bmp_position.x + self.select_position.x * self.magnify_factor, 
                y=self.bmp_position.y + (self.select_position.y + self.select_position.h) * self.magnify_factor,
            )
            bottom_right = Point(
                x=self.bmp_position.x + (self.select_position.x + self.select_position.w) * self.magnify_factor, 
                y=self.bmp_position.y + (self.select_position.y + self.select_position.h) * self.magnify_factor,
            )

            if top_left.x < w and top_left.y > 0:
                bmp = wx.Bitmap.FromRGBA(
                    width=w - top_left.x,
                    height=top_left.y,
                    red=0,
                    green=0,
                    blue=0,
                    alpha=100,
                )

                gc.DrawBitmap(
                    bmp=bmp,
                    x=top_left.x,
                    y=0,
                    w=w - top_left.x,
                    h=top_left.y,
                )

            if top_right.x < w and top_right.y < h:
                bmp = wx.Bitmap.FromRGBA(
                    width=w - top_right.x,
                    height=h - top_right.y,
                    red=0,
                    green=0,
                    blue=0,
                    alpha=100,
                )

                gc.DrawBitmap(
                    bmp=bmp,
                    x=top_right.x,
                    y=top_right.y,
                    w=w - top_right.x,
                    h=h - top_right.y,
                )

            if bottom_left.x > 0 and bottom_left.y < h:
                bmp = wx.Bitmap.FromRGBA(
                    width=top_left.x,
                    height=bottom_left.y,
                    red=0,
                    green=0,
                    blue=0,
                    alpha=100,
                )

                gc.DrawBitmap(
                    bmp=bmp,
                    x=0,
                    y=0,
                    w=bottom_left.x,
                    h=bottom_left.y,
                )

            if bottom_right.x > 0 and bottom_right.y < h:
                bmp = wx.Bitmap.FromRGBA(
                    width=bottom_right.x,
                    height=h - bottom_right.y,
                    red=0,
                    green=0,
                    blue=0,
                    alpha=100,
                )

                gc.DrawBitmap(
                    bmp=bmp,
                    x=0,
                    y=bottom_right.y,
                    w=bottom_right.x,
                    h=h - bottom_right.y,
                )

        if self.select_preview.w > 0 and self.select_preview.h > 0:
            # Redden selection preview
            bmp = wx.Bitmap.FromRGBA(
                width=self.select_preview.w * self.magnify_factor,
                height=self.select_preview.h * self.magnify_factor,
                red=255,
                green=0,
                blue=0,
                alpha=100,
            )

            gc.DrawBitmap(
                bmp=bmp,
                x=self.bmp_position.x + self.select_preview.x * self.magnify_factor,
                y=self.bmp_position.y + self.select_preview.y * self.magnify_factor,
                w=self.select_preview.w * self.magnify_factor,
                h=self.select_preview.h * self.magnify_factor,
            )

    def SavePXT(self, filepath):
        """Saves the current canvas as PXT to disk.

        The PXT file format is really just a `.tar.gz` compressed directory
        that contains the canvas image and JSON data of the hitboxes.

        Parameters
        -----------
        filepath: str
            the filepath should have a `.pxt` file extension.
        """
        temp_dir = filepath + ".temp"
        canvas_filepath = os.path.join(temp_dir, "canvas.bmp")
        data_filepath = os.path.join(temp_dir, "data.json")

        # Construct data storage
        data = {
            "spritesheet_properties": {
                "spritesheet_rows": self.rows,
                "spritesheet_cols": self.cols,
            },
        }

        sprites = dict()

        for sprite_key, sprite in self.sprites.items():
            sprites[sprite.label] = {
                "sprite_key": sprite_key,
                "hitboxes": dict()
            }

            for hitbox_key, hitbox in sprite.hitboxes.items():
                sprites[sprite.label]["hitboxes"][hitbox_key] = {
                    "x": hitbox.x,
                    "y": hitbox.y,
                    "w": hitbox.w,
                    "h": hitbox.h,
                    "label": hitbox.label,
                }

        data["sprite_properties"] = sprites

        # Write all data in temporary directory
        os.mkdir(temp_dir)

        self.bmp.SaveFile(
            name=canvas_filepath,
            type=wx.BITMAP_TYPE_BMP,
        )

        try:
            with open(data_filepath, "w") as file:
                json.dump(data, file)
        except IOError:
            wx.LogError(f"Failed to save file in {filepath}")

        # Compress directory
        archive_filepath = shutil.make_archive(
            base_name=filepath, 
            format="gztar",
            root_dir=temp_dir,
        )

        # Rename archive and remove temporary directory
        shutil.move(src=archive_filepath, dst=filepath)
        shutil.rmtree(temp_dir)

        self.saved = True

    def onKeyDown(self, event):
        """Processes keyboard events.
        
        If the `Move` tool is selected, then
          - the position of the selected hitbox is moved by one pixel in the
            direction of the arrow key.
          - the selected hitbox is deleted if the delete key is pressed.
        """
        if self.state != State.MOVE and self.hitbox_select is None:
            return

        key = event.GetKeyCode()
        hitbox = self.sprites[self.select].hitboxes[self.hitbox_select]

        if key == wx.WXK_DELETE:
            del self.sprites[self.select].hitboxes[self.hitbox_select]

            self.hitbox_select = None

        elif key == wx.WXK_LEFT:
            hitbox.x -= 1

        elif key == wx.WXK_UP:
            hitbox.y -= 1

        elif key == wx.WXK_RIGHT:
            hitbox.x += 1

        elif key == wx.WXK_DOWN:
            hitbox.y += 1

        self.Refresh()

        self.saved = False

    def onLeftDown(self, event):
        """Records the location of the mouse click.

        If the `Move` tool is selected, then a hitbox is selected.
        If the `Draw` tool is selected, then a hitbox is drawn.
        """
        x, y = event.GetPosition()

        self.left_down.Set(x=x, y=y)

        if self.state == State.SELECT:
            self.select_position.Set(*self.FindSelectionZone(x, y))

            if self.select_position.w == 0 and self.select_position.h == 0:
                self.select = None
            else:
                self.select = (self.select_position.x, self.select_position.y)

                if self.sprites.get(self.select) is None:
                    self.sprites[self.select] = Sprite(
                        label=f"x{self.select_position.x}_y{self.select_position.y}"
                    )

            wx.PostEvent(self.Parent, UpdateInspectorSpriteEvent())

            self.Refresh()

        elif self.state == State.MOVE and self.select is not None:
            # Scale selected hitbox
            if self.hitbox_select is not None:
                local_position = Point(
                    x=self.left_down.x - self.bmp_position.x,
                    y=self.left_down.y - self.bmp_position.y,
                )

                self.scale_select = self.scale_rects.SelectScale(local_position)
                self.hitbox_buffer.Set(
                    x=self.left_down.x, 
                    y=self.left_down.y
                )

            # Find a hitbox in the mouse position
            if self.scale_select is None:
                local_position = Point(
                    x=(self.left_down.x - self.bmp_position.x) // self.magnify_factor,
                    y=(self.left_down.y - self.bmp_position.y) // self.magnify_factor,
                )

                for label, hitbox in self.sprites[self.select].hitboxes.items():
                    if hitbox.Contains(local_position):
                        self.hitbox_buffer.Set(x=hitbox.x, y=hitbox.y)
                        self.hitbox_select = label

                        wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())

                        break

            self.Refresh()

        elif self.state == State.DRAW and self.select:
            sprite = (self.select_position.x, self.select_position.y)

            self.hitbox_select = self.n_hitboxes_created
            self.sprites[sprite].hitboxes[self.hitbox_select] = Rect(
                x=(self.left_down.x - self.bmp_position.x) // self.magnify_factor,
                y=(self.left_down.y - self.bmp_position.y) // self.magnify_factor,
                w=0,
                h=0,
                label=f"box{self.hitbox_select}",
            )

            self.n_hitboxes_created += 1

            self.saved = False

    def onLeftUp(self, event):
        """Records the size of the drawn rectangle and renders it."""
        if self.state == State.DRAW and self.hitbox_select is not None:
            hitboxes = self.sprites[self.select].hitboxes
            hitbox = hitboxes[self.hitbox_select]

            if hitbox.w <= 0 or hitbox.h <= 0:
                del hitboxes[self.hitbox_select]

            else:
                self.saved = False

            self.hitbox_select = None

    def onMiddleDown(self, event):
        """Records the location of the mouse click."""
        self.middle_down.Set(*event.GetPosition())

    def onMotion(self, event):
        """The action of motion depends on the button that is held down.

        If the left button is held down and the `Move` tool is selected, then
        the hitbox is moved.
        If the left button is held down and the `Draw` tool is selected, then
        the hitbox is drawn.
        If the middle button is held down, the canvas is panned.
        """
        if self.state == State.SELECT:
            x, y = event.GetPosition()
            self.select_preview.Set(*self.FindSelectionZone(x, y))

            self.Refresh()

        if event.LeftIsDown() and self.hitbox_select is not None:
            x, y = event.GetPosition()

            hitbox = self.sprites[self.select].hitboxes[self.hitbox_select]

            if self.state == State.MOVE:
                if self.scale_select is not None:
                    dx = (x - self.hitbox_buffer.x) // self.magnify_factor
                    dy = (y - self.hitbox_buffer.y) // self.magnify_factor

                    if dx != 0:
                        self.hitbox_buffer.x = x
                    
                    if dy != 0:
                        self.hitbox_buffer.y = y

                    if dx != 0 or dy != 0:
                        hitbox.Scale(
                            scale=self.scale_select,
                            dx=dx,
                            dy=dy,
                        )

                        wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())
                        self.Refresh()

                        self.saved = False

                else:
                    dx = (x - self.left_down.x) // self.magnify_factor
                    dy = (y - self.left_down.y) // self.magnify_factor

                    hitbox.x = self.hitbox_buffer.x + dx
                    hitbox.y = self.hitbox_buffer.y + dy

                    if dx != 0 or dy != 0:
                        wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())
                        self.Refresh()

                        self.saved = False

            elif self.state == State.DRAW:
                dx = x - self.left_down.x
                dy = y - self.left_down.y

                if dx != 0 or dy != 0:
                    hitbox.Set(
                        x=(min(x, self.left_down.x) - self.bmp_position.x) // self.magnify_factor,
                        y=(min(y, self.left_down.y) - self.bmp_position.y) // self.magnify_factor,
                        w=abs(dx) // self.magnify_factor,
                        h=abs(dy) // self.magnify_factor,
                    )

                    self.Refresh()

                    self.saved = False

        elif event.MiddleIsDown():
            x, y = event.GetPosition()

            dx = x - self.middle_down.x
            dy = y - self.middle_down.y

            self.bmp_position.x += dx
            self.bmp_position.y += dy

            self.middle_down.Set(x, y)

            self.Refresh()

    def onMouseWheel(self, event):
        """Zooms in or out of the canvas."""
        if not self.bmp_loaded:
            return

        x, y = event.GetPosition()
        rotation = event.GetWheelRotation()

        if rotation > 0:
            self.magnify += 1
        elif rotation < 0:
            self.magnify -= 1

        old_mag = self.magnify_factor

        if self.magnify < 1:
            self.magnify_factor = 1 / (2 - 2 * self.magnify)
        else:
            self.magnify_factor = self.magnify

        w, h = self.bmp.GetSize()

        self.bmp_position.Set(
            x=x - (self.magnify_factor / old_mag) * (x - self.bmp_position.x),
            y=y - (self.magnify_factor / old_mag) * (y - self.bmp_position.y),
            w=w * self.magnify_factor,
            h=h * self.magnify_factor,
        )

        self.Refresh()

    def onPaintCanvas(self, event):
        """Paints the background image and the hitboxes on the canvas."""
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        w, h = self.GetSize()

        # Paint background
        gc.DrawBitmap(
            bmp=self.bg,
            x=0,
            y=0,
            w=w,
            h=h,
        )

        if self.bmp_loaded:
            self.PaintBMP(gc)
            self.PaintRulers(dc)

        if self.state == State.SELECT or self.select is not None:
            self.PaintSelect(gc)

        self.PaintHitboxes(gc)

        if self.state == State.MOVE and self.hitbox_select is not None:
            self.PaintScale(gc)

    def onSize(self, event):
        """Resizes the background when the windows is resized."""
        w, h = event.GetSize()

        self.bg = wx.Bitmap.FromRGBA(
            width=w,
            height=h,
            red=self.bg_colour.red,
            green=self.bg_colour.green,
            blue=self.bg_colour.blue,
            alpha=self.bg_colour.alpha,
        )
