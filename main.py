import enum
import os
import wx


IMAGE_WILDCARD = "JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
JSON_WILDCARD = "JSON files (*.json)|*.json"


class State(enum.Enum):
    MOVE = enum.auto()
    DRAW = enum.auto()


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


class MainFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            id=wx.ID_ANY,
            title="sprite-hitbox-generator",
            pos=wx.DefaultPosition,
            size=wx.Size(640, 480),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        # Internal variables
        self.saved = True

        # Main panel
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.canvas = Canvas(parent=self)
        sizer.Add(
            window=self.canvas,
            proportion=1,
            flag=wx.ALL | wx.EXPAND,
            border=5,
        )

        self.SetSizer(sizer)
        self.Layout()

        # Main menu bar
        self.main_menu_bar = wx.MenuBar(0)
        self.file_menu = wx.Menu()
        self.file_menu_new = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="New\tCTRL+N",
            helpString=wx.EmptyString,
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_new)

        self.file_menu.AppendSeparator()

        self.file_menu_open = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Open\tCTRL+O",
            helpString=wx.EmptyString,
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_open)

        self.file_menu.AppendSeparator()

        self.file_menu_close = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Close\tCTRL+W",
            helpString=wx.EmptyString,
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_close)
        
        self.file_menu.AppendSeparator()

        self.file_menu_save = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Save\tCTRL+S",
            helpString=wx.EmptyString,
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_save)

        self.file_menu.AppendSeparator()

        self.file_menu_exit = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Exit\tCTRL+Q",
            helpString=wx.EmptyString,
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_exit)

        self.main_menu_bar.Append(self.file_menu, "File")

        self.SetMenuBar(self.main_menu_bar)

        self.tool_bar = self.CreateToolBar(
            wx.TB_VERTICAL,
            wx.ID_ANY,
        )

        self.tool_move = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Move",
            bitmap=wx.Bitmap(name="assets/tool_move.png"),
            bmpDisabled=wx.NullBitmap,
            kind=wx.ITEM_CHECK,
            shortHelp=wx.EmptyString,
            longHelp=wx.EmptyString,
            clientData=None,
        )

        self.tool_bar.AddSeparator()

        self.tool_draw = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Draw",
            bitmap=wx.Bitmap(name="assets/tool_draw.png"),
            bmpDisabled=wx.NullBitmap,
            kind=wx.ITEM_CHECK,
            shortHelp=wx.EmptyString,
            longHelp=wx.EmptyString,
            clientData=None,
        )

        self.tool_bar.AddSeparator()

        self.tool_colour_picker = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Colour Picker",
            bitmap=wx.Bitmap(name="assets/tool_colour_picker.png"),
            bmpDisabled=wx.NullBitmap,
            kind=wx.ITEM_NORMAL,
            shortHelp=wx.EmptyString,
            longHelp=wx.EmptyString,
            clientData=None,
        )

        self.tool_bar.Realize()

        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_MENU, self.onFileMenuOpen, id=self.file_menu_open.GetId())
        self.Bind(wx.EVT_MENU, self.onFileMenuSave, id=self.file_menu_save.GetId())

        self.Bind(wx.EVT_TOOL, self.onToolMove, id=self.tool_move.GetId())
        self.Bind(wx.EVT_TOOL, self.onToolDraw, id=self.tool_draw.GetId())
        self.Bind(wx.EVT_TOOL, self.onToolColourPicker, id=self.tool_colour_picker.GetId())

        self.tool_bar.ToggleTool(self.tool_move.GetId(), True)

    def onFileMenuOpen(self, event):
        """Create and show the `wx.FileDialog` to open a file."""
        if not self.saved:
            confirm_continue = wx.MessageBox(
                "Current file has not been saved. Continue?",
                wx.ICON_QUESTION | wx.YES_NO,
                self
            )

            if confirm_continue == wx.NO:
                return

        with wx.FileDialog(
                    parent=self,
                    message="Select a file to open",
                    defaultDir=os.getcwd(),
                    defaultFile="",
                    wildcard=IMAGE_WILDCARD,
                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                ) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            self.canvas.LoadImage(dialog.GetPath())

        self.Refresh()

    def onFileMenuSave(self, event):
        """Create and show the `wx.FileDialog` to save a file."""
        with wx.FileDialog(
                    parent=self,
                    message="Save hitbox data",
                    wildcard=JSON_WILDCARD,
                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
                ) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            self.canvas.Save(dialog.GetPath())

    def onToolColourPicker(self, event):
        """Opens the colour dialog and sets the draw colour."""
        with wx.ColourDialog(parent=self) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            colour = dialog.GetColourData().GetColour()

            self.canvas.hitbox_colour.Set(
                red=colour.red,
                green=colour.green,
                blue=colour.blue,
            )

        self.Refresh()

    def onToolDraw(self, event):
        self.canvas.state = State.DRAW
        self.canvas.hitbox_select = None

        self.tool_bar.ToggleTool(self.tool_draw.GetId(), True)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), False)

        self.Refresh()

    def onToolMove(self, event):
        self.canvas.state = State.MOVE

        self.tool_bar.ToggleTool(self.tool_draw.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), True)

        self.Refresh()

    def __del__(self):
        pass



def main():
    app = wx.App()

    frame = MainFrame(None)
    frame.Show(True)

    app.MainLoop()


if __name__ == "__main__":
    main()
