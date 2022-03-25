import wx
import os


IMAGE_WILDCARD = "JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
JSON_WILDCARD = "JSON files (*.json)|*.json"


class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.HSCROLL | wx.VSCROLL,
        )

        self.n_hitboxes_created = 0
        self.hitboxes = dict()

        self.tool_draw_left_down_x = 0
        self.tool_draw_left_down_y = 0

        self.Bind(wx.EVT_LEFT_DOWN, self.onToolDrawLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onToolDrawLeftUp)

        self.Bind(wx.EVT_PAINT, self.onDrawRectangle)

    def onDrawRectangle(self, event):
        """Draws a rectangle on the canvas."""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        for hitbox in self.hitboxes.values():
            bmp = wx.Bitmap.FromRGBA(
                width=hitbox["w"],
                height=hitbox["h"],
                red=256,
                green=50,
                blue=0,
                alpha=50,
            )

            gc.DrawBitmap(
                bmp=bmp,
                x=hitbox["x"],
                y=hitbox["y"],
                w=hitbox["w"],
                h=hitbox["h"],
            )

    def onToolDrawLeftDown(self, event):
        """Records the location of the mouse click."""
        self.tool_draw_left_down_x, self.tool_draw_left_down_y = event.GetPosition()

    def onToolDrawLeftUp(self, event):
        """Records the size of the drawn rectangle and renders it."""
        x, y = event.GetPosition()

        w = abs(x - self.tool_draw_left_down_x)
        h = abs(y - self.tool_draw_left_down_y)

        self.hitboxes[self.n_hitboxes_created] = {
            "x": min(x, self.tool_draw_left_down_x),
            "y": min(y, self.tool_draw_left_down_y),
            "w": w,
            "h": h,
        }

        self.n_hitboxes_created += 1

        self.Refresh()

    def onToolDrawDoubleClick(self, event):
        """Selects the shape for resizing."""
        pass


class MainFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            id=wx.ID_ANY,
            title="sprite-hitbox-generator",
            pos=wx.DefaultPosition,
            size=wx.Size(640, 480),
            style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL,
        )

        # Internal variables
        self.saved = True

        # Main panel
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)

        # self.main_bmp = wx.StaticBitmap(
        #     parent=self,
        #     id=wx.ID_ANY,
        #     bitmap=wx.NullBitmap,
        #     pos=wx.DefaultPosition,
        #     size=wx.DefaultSize,
        #     style=0,
        # )
        # sizer.Add(
        #     window=self.main_bmp, 
        #     proportion=0, 
        #     flag=wx.ALL, 
        #     border=5,
        # )

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

        # Main tool bar
        self.main_tool_bar = self.CreateToolBar(
            wx.TB_VERTICAL,
            wx.ID_ANY,
        )

        self.tool_move_bmp = wx.Bitmap(name="assets/tool_move.png")
        self.tool_move = self.main_tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Move",
            bitmap=self.tool_move_bmp,
            bmpDisabled=wx.NullBitmap,
            kind=wx.ITEM_NORMAL,
            shortHelp=wx.EmptyString,
            longHelp=wx.EmptyString,
            clientData=None,
        )

        self.main_tool_bar.AddSeparator()

        self.tool_draw_bmp = wx.Bitmap(name="assets/tool_draw.png")
        self.tool_draw = self.main_tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Draw",
            bitmap=self.tool_draw_bmp,
            bmpDisabled=wx.NullBitmap,
            kind=wx.ITEM_NORMAL,
            shortHelp=wx.EmptyString,
            longHelp=wx.EmptyString,
            clientData=None,
        )

        self.main_tool_bar.Realize()

        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_MENU, self.onFileMenuOpen, id=self.file_menu_open.GetId())
        self.Bind(wx.EVT_MENU, self.onFileMenuSave, id=self.file_menu_save.GetId())

        print("Window:", self.GetSize())
        print("Canvas:", self.canvas.GetSize())

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

            self.read(dialog.GetPath())

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

            self.write(dialog.GetPath())

    def read(self, path):
        """Reads and loads an image file to the main panel."""
        bmp = wx.Bitmap(name=path)
        self.main_bmp.SetBitmap(label=bmp)


    def write(self, path):
        try:
            with open(path, "w") as file:
                pass
        except IOError:
            wx.LogError(f"Failed to save file in {path}")

    def __del__(self):
        pass



def main():
    app = wx.App()

    frame = MainFrame(None)
    frame.Show(True)

    app.MainLoop()


if __name__ == "__main__":
    main()
