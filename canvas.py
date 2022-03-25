import wx

from primitives import Point, Rect
from state import State


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
            # Find a rectangle in the mouse position
            for label, hitbox in self.hitboxes.items():
                if hitbox.Contains(self.left_down):
                    self.hitbox_select = label

                    break

            # if hitbox selected and clicked on corner, extend

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

        if self.state == State.MOVE:
            self.hitboxes[self.hitbox_select].x += x - self.left_down.x
            self.hitboxes[self.hitbox_select].y += y - self.left_down.y

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

            r = 0.1 * min(hitbox.w, hitbox.h)

            gc.DrawEllipse(
                x=int(hitbox.x + 0.5 * hitbox.w - r),
                y=int(hitbox.y + 0.5 * hitbox.h - r),
                w=int(2 * r),
                h=int(2 * r),
            )

        self.saved = False
