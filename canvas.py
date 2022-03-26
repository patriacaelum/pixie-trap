import wx

from enums import State
from primitives import Point, Rect, ScaleRects


class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.HSCROLL | wx.VSCROLL,
        )

        self.bmp_loaded = False
        self.state = State.MOVE
        self.saved = True

        self.hitboxes = dict()
        self.n_hitboxes_created = 0
        self.hitbox_colour = wx.Colour(255, 50, 0, 50)
        self.hitbox_select = None

        self.scale_select = None
        self.scale_radius = 5
        self.scale_rects = ScaleRects()

        self.left_down = Point()

        self.bmp = wx.Bitmap()
        
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.Bind(wx.EVT_MOTION, self.onMotion)

        self.Bind(wx.EVT_PAINT, self.onPaintCanvas)

    def LoadImage(self, path):
        """Reads and loads an image file to the canvas."""
        self.bmp.LoadFile(name=path)

        self.bmp_loaded = True

    def Save(self, path):
        try:
            with open(path, "w") as file:
                pass
        except IOError:
            wx.LogError(f"Failed to save file in {path}")

    def onLeftDown(self, event):
        """Records the location of the mouse click."""
        self.left_down.Set(*event.GetPosition())

        if self.state == State.MOVE:
            if self.hitbox_select is not None:
                self.scale_select = self.scale_rects.SelectScale(self.left_down)

            if self.scale_select is None:
                # Find a hitbox in the mouse position
                for label, hitbox in self.hitboxes.items():
                    if hitbox.Contains(self.left_down):
                        self.hitbox_select = label

                        break

            self.Refresh()

        elif self.state == State.DRAW:
            self.hitbox_select = self.n_hitboxes_created
            self.hitboxes[self.hitbox_select] = Rect(
                x=self.left_down.x,
                y=self.left_down.y,
                w=0,
                h=0
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

    def onMotion(self, event):
        if not event.LeftIsDown():
            return

        x, y = event.GetPosition()

        dx = x - self.left_down.x
        dy = y - self.left_down.y

        if self.state == State.MOVE:
            if self.scale_select is not None:
                self.hitboxes[self.hitbox_select].Scale(
                    scale=self.scale_select,
                    dx=dx,
                    dy=dy,
                )

            else:
                self.hitboxes[self.hitbox_select].x += dx
                self.hitboxes[self.hitbox_select].y += dy

            self.left_down.Set(x=x, y=y)

            self.Refresh()

        elif self.state == State.DRAW:
            self.hitboxes[self.hitbox_select].Set(
                x=min(x, self.left_down.x),
                y= min(y, self.left_down.y),
                w=abs(x - self.left_down.x),
                h=abs(y - self.left_down.y),
            )

            self.Refresh()

    def onToolDrawDoubleClick(self, event):
        """Selects the shape for resizing."""
        pass

    def onPaintCanvas(self, event):
        """Paints the background image and the hitboxes on the canvas."""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if self.bmp_loaded:
            gc.DrawBitmap(
                bmp=self.bmp,
                x=0,
                y=0,
                w=self.bmp.GetWidth(),
                h=self.bmp.GetHeight(),
            )

        for hitbox in self.hitboxes.values():
            if hitbox.w <= 0 or hitbox.h <= 0:
                continue

            bmp = wx.Bitmap.FromRGBA(
                width=hitbox.w,
                height=hitbox.h,
                red=self.hitbox_colour.red,
                green=self.hitbox_colour.green,
                blue=self.hitbox_colour.blue,
                alpha=50,
            )

            gc.DrawBitmap(
                bmp=bmp,
                x=hitbox.x,
                y=hitbox.y,
                w=hitbox.w,
                h=hitbox.h,
            )

        if self.state == State.MOVE and self.hitbox_select is not None:
            gc.SetPen(wx.Pen(
                colour=wx.Colour(0, 0, 0, 100),
                width=2)
            )
            hitbox = self.hitboxes[self.hitbox_select]

            gc.DrawEllipse(
                x=int(hitbox.centre.x - self.scale_radius),
                y=int(hitbox.centre.y - self.scale_radius),
                w=int(2 * self.scale_radius),
                h=int(2 * self.scale_radius),
            )

            self.scale_rects.Set(
                rect=hitbox,
                radius=self.scale_radius,
            )

            for rectangle in self.scale_rects.rects.values():
                gc.DrawRectangle(
                    x=rectangle.x,
                    y=rectangle.y,
                    w=rectangle.w,
                    h=rectangle.h,
                )

        self.saved = False
