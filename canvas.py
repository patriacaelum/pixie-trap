import wx

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

        self.hitboxes = dict()
        self.n_hitboxes_created = 0
        self.hitbox_colour = wx.Colour(255, 50, 0, 50)
        self.hitbox_select = None

        self.left_down_x = 0
        self.left_down_y = 0

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
        self.left_down_x, self.left_down_y = event.GetPosition()

        if self.state == State.MOVE:
            # Find a rectangle in the mouse position
            for label, hitbox in self.hitboxes.items():
                x_range = hitbox["x"] <= self.left_down_x <= hitbox["x"] + hitbox["w"]
                y_range = hitbox["y"] <= self.left_down_y <= hitbox["y"] + hitbox["h"]

                if x_range and y_range:
                    self.hitbox_select = label
                    self.Refresh()

                    break

        elif self.state == State.DRAW:
            self.hitbox_select = self.n_hitboxes_created
            self.hitboxes[self.hitbox_select] = {
                "x": self.left_down_x,
                "y": self.left_down_y,
                "w": 0,
                "h": 0,
            }

            self.n_hitboxes_created += 1

    def onLeftUp(self, event):
        """Records the size of the drawn rectangle and renders it."""
        if self.state == State.MOVE:
            pass

        elif self.state == State.DRAW and self.hitbox_select is not None:
            hitbox = self.hitboxes[self.hitbox_select]

            if hitbox["w"] <= 0 or hitbox["h"] <= 0:
                del self.hitboxes[self.hitbox_select]

            self.hitbox_select = None

    def onMotion(self, event):
        if not event.LeftIsDown():
            return

        x, y = event.GetPosition()

        if self.state == State.MOVE:
            self.hitboxes[self.hitbox_select]["x"] += x - self.left_down_x
            self.hitboxes[self.hitbox_select]["y"] += y - self.left_down_y

            self.left_down_x = x
            self.left_down_y = y

            self.Refresh()

        elif self.state == State.DRAW:
            self.hitboxes[self.hitbox_select] = {
                "x": min(x, self.left_down_x),
                "y": min(y, self.left_down_y),
                "w": abs(x - self.left_down_x),
                "h": abs(y - self.left_down_y),
            }

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
            if hitbox["w"] <= 0 or hitbox["h"] <= 0:
                continue

            bmp = wx.Bitmap.FromRGBA(
                width=hitbox["w"],
                height=hitbox["h"],
                red=self.hitbox_colour.red,
                green=self.hitbox_colour.green,
                blue=self.hitbox_colour.blue,
                alpha=50,
            )

            gc.DrawBitmap(
                bmp=bmp,
                x=hitbox["x"],
                y=hitbox["y"],
                w=hitbox["w"],
                h=hitbox["h"],
            )

        if self.state == State.MOVE and self.hitbox_select is not None:
            gc.SetPen(wx.BLACK_PEN)
            hitbox = self.hitboxes[self.hitbox_select]

            gc.DrawEllipse(
                x=int(hitbox["x"] + 0.4 * hitbox["w"]),
                y=int(hitbox["y"] + 0.4 * hitbox["h"]),
                w=int(0.2 * hitbox["w"]),
                h=int(0.2 * hitbox["h"]),
            )
