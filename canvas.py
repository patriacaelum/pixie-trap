import numpy as np
import wx

from constants import State
from constants import UpdateInspectorHitboxEvent
from primitives import Point, Rect, ScaleRects


class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.bmp_loaded = False
        self.state = State.MOVE
        self.saved = True

        self.magnify = 1
        self.magnify_factor = 1

        self.left_down = Point()
        self.middle_down = Point()

        self.bmp = wx.Bitmap()
        self.bmp_position = Rect()
        self.rows = 1
        self.cols = 1

        self.select = Rect()
        self.select_preview = Rect()

        self.hitboxes = dict()
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

        self.Bind(wx.EVT_PAINT, self.onPaintCanvas)

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

    def PaintBMP(self, gc):
        """Paints the loaded image to the canvas."""
        gc.DrawBitmap(
            bmp=self.bmp,
            x=self.bmp_position.x,
            y=self.bmp_position.y,
            w=self.bmp_position.w,
            h=self.bmp_position.h,
        )

    def PaintHitboxes(self, gc):
        """Paints the drawn hitboxes to the canvas."""
        for hitbox in self.hitboxes.values():
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

        position = self.bmp_position

        vspace = int(position.h // self.rows)
        hspace = int(position.w // self.cols)

        dc.DrawLineList([
            (0, position.y + y, canvas_width, position.y + y)
            for y in range(0, position.h + 1, vspace)
        ])

        dc.DrawLineList([
            (position.x + x, 0, position.x + x, canvas_height)
            for x in range(0, position.w + 1, hspace)
        ])

    def PaintScale(self, gc):
        """Paints the transformation scaling pins on the selected hitbox."""
        gc.SetPen(wx.Pen(
            colour=wx.Colour(0, 0, 0, 100),
            width=2)
        )
        hitbox = self.hitboxes[self.hitbox_select]

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

        select = (self.select.w > 0 and self.select.h > 0)
        preview = (self.select_preview.w > 0 and self.select_preview.h > 0)

        if not select and not preview:
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
            if preview:
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

            # Darken everywhere except selection zone
            top_left = Point(
                x=self.bmp_position.x + self.select.x * self.magnify_factor, 
                y=self.bmp_position.y + self.select.y * self.magnify_factor,
            )
            top_right = Point(
                x=self.bmp_position.x + (self.select.x + self.select.w) * self.magnify_factor, 
                y=self.bmp_position.y + self.select.y * self.magnify_factor,
            )
            bottom_left = Point(
                x=self.bmp_position.x + self.select.x * self.magnify_factor, 
                y=self.bmp_position.y + (self.select.y + self.select.h) * self.magnify_factor,
            )
            bottom_right = Point(
                x=self.bmp_position.x + (self.select.x + self.select.w) * self.magnify_factor, 
                y=self.bmp_position.y + (self.select.y + self.select.h) * self.magnify_factor,
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

    def Save(self, path):
        try:
            with open(path, "w") as file:
                pass
        except IOError:
            wx.LogError(f"Failed to save file in {path}")

    def onLeftDown(self, event):
        """Records the location of the mouse click.

        If the `Move` tool is selected, then a hitbox is selected.
        If the `Draw` tool is selected, then a hitbox is drawn.
        """
        x, y = event.GetPosition()

        self.left_down.Set(x=x, y=y)

        if self.state == State.SELECT:
            self.select.Set(*self.FindSelectionZone(x, y))

            self.Refresh()

        elif self.state == State.MOVE:
            local_position = Point(
                x=(self.left_down.x - self.bmp_position.x) // self.magnify_factor,
                y=(self.left_down.y - self.bmp_position.y) // self.magnify_factor,
            )

            # Scale selected hitbox
            if self.hitbox_select is not None:
                self.scale_select = self.scale_rects.SelectScale(self.left_down)

            # Find a hitbox in the mouse position
            if self.scale_select is None:
                for label, hitbox in self.hitboxes.items():
                    if hitbox.Contains(local_position):
                        self.hitbox_buffer.Set(x=hitbox.x, y=hitbox.y)
                        self.hitbox_select = label

                        wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())

                        break

            self.Refresh()

        elif self.state == State.DRAW:
            self.hitbox_select = self.n_hitboxes_created
            self.hitboxes[self.hitbox_select] = Rect(
                x=(self.left_down.x - self.bmp_position.x) // self.magnify_factor,
                y=(self.left_down.y - self.bmp_position.y) // self.magnify_factor,
                w=0,
                h=0,
                label=f"box{self.hitbox_select}",
            )

            self.n_hitboxes_created += 1

    def onLeftUp(self, event):
        """Records the size of the drawn rectangle and renders it."""
        if self.state == State.MOVE:
            pass

        elif self.state == State.DRAW and self.hitbox_select is not None:
            hitbox = self.hitboxes[self.hitbox_select]

            if hitbox.w <= 0 or hitbox.h <= 0:
                del self.hitboxes[self.hitbox_select]

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

            hitbox = self.hitboxes[self.hitbox_select]

            if self.state == State.MOVE:
                if self.scale_select is not None:
                    dx = (x - self.left_down_buffer.x) // self.magnify_factor
                    dy = (y - self.left_down_buffer.y) // self.magnify_factor

                    self.left_down_buffer.Set(x=x, y=y)

                    hitbox.Scale(
                        scale=self.scale_select,
                        dx=dx,
                        dy=dy,
                    )

                else:
                    dx = (x - self.left_down.x) // self.magnify_factor
                    dy = (y - self.left_down.y) // self.magnify_factor

                    print(x, self.left_down.x, dx)

                    hitbox.x = self.hitbox_buffer.x + dx
                    hitbox.y = self.hitbox_buffer.y + dy

                wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())

            elif self.state == State.DRAW:
                dx = x - self.left_down.x
                dy = y - self.left_down.y

                hitbox.Set(
                    x=(min(x, self.left_down.x) - self.bmp_position.x) // self.magnify_factor,
                    y=(min(y, self.left_down.y) - self.bmp_position.y) // self.magnify_factor,
                    w=abs(dx) // self.magnify_factor,
                    h=abs(dy) // self.magnify_factor,
                )

            self.Refresh()

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
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if self.bmp_loaded:
            self.PaintBMP(gc)
            self.PaintRulers(dc)

        if self.state == State.SELECT or (self.select.w != 0 and self.select.h != 0):
            self.PaintSelect(gc)

        self.PaintHitboxes(gc)

        if self.state == State.MOVE and self.hitbox_select is not None:
            self.PaintScale(gc)

        self.saved = False
