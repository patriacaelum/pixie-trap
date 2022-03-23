import wx
import os


IMAGE_WILDCARD = "JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
JSON_WILDCARD = "JSON files (*.json)|*.json"


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self, 
            parent,
            id=wx.ID_ANY,
            title="sprite-hitbox-generator",
            pos=wx.DefaultPosition,
            size=wx.Size(500, 300),
            style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL,
        )

        # Internal variables
        self.saved = True

        # Main panel
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        main_panel = wx.BoxSizer(orient=wx.VERTICAL)

        self.main_bmp = wx.StaticBitmap(
            parent=self,
            id=wx.ID_ANY,
            bitmap=wx.NullBitmap,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0
        )
        main_panel.Add(
            window=self.main_bmp, 
            proportion=0, 
            flag=wx.ALL, 
            border=5
        )

        self.SetSizer(main_panel)
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
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.onFileMenuOpen,
            id=self.file_menu_open.GetId()
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
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.onFileMenuSave,
            id=self.file_menu_save.GetId()
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
        self.tool_move = self.main_tool_bar.AddTool(
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
