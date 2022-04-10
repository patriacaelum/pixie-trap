import os
import wx

from canvas import Canvas
from constants import State
from constants import EXPAND
from constants import IMAGE_WILDCARD, JSON_WILDCARD, SHG_WILDCARD
from constants import EVT_UPDATE_INSPECTOR_HITBOX, EVT_UPDATE_INSPECTOR_SPRITE
from inspector import Inspector


class SpriteHitboxGenerator(wx.Frame):
    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="sprite-hitbox-generator",
            size=wx.Size(640, 480),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.filepath = None

        self.Maximize()

        # Main panel
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        main_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.canvas = Canvas(parent=self)
        main_sizer.Add(
            window=self.canvas,
            proportion=1,
            flag=EXPAND,
            border=5,
        )

        self.inspector = Inspector(parent=self)
        main_sizer.Add(
            window=self.inspector,
            proportion=1,
            flag=EXPAND,
            border=5,
        )

        self.SetSizer(main_sizer)
        self.Layout()

        self.InitMenuBar()
        self.InitToolBar()

        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_MENU, self.onFileMenuNew, id=self.file_menu_new.GetId())
        self.Bind(wx.EVT_MENU, self.onFileMenuOpen, id=self.file_menu_open.GetId())
        self.Bind(wx.EVT_MENU, self.onFileMenuSave, id=self.file_menu_save.GetId())
        self.Bind(wx.EVT_MENU, self.onFileMenuSaveAs, id=self.file_menu_save_as.GetId())
        self.Bind(wx.EVT_MENU, self.onFileMenuExportAs, id=self.file_menu_export_as.GetId())
        self.Bind(wx.EVT_MENU, self.onFileMenuExit, id=self.file_menu_exit.GetId())

        self.Bind(wx.EVT_TOOL, self.onToolSelect, id=self.tool_select.GetId())
        self.Bind(wx.EVT_TOOL, self.onToolMove, id=self.tool_move.GetId())
        self.Bind(wx.EVT_TOOL, self.onToolDraw, id=self.tool_draw.GetId())
        self.Bind(wx.EVT_TOOL, self.onToolColourPicker, id=self.tool_colour_picker.GetId())

        self.Bind(wx.EVT_TEXT, self.onSpritesheetProperties, id=self.inspector.spritesheet_rows.GetId())
        self.Bind(wx.EVT_TEXT, self.onSpritesheetProperties, id=self.inspector.spritesheet_cols.GetId())
        self.Bind(wx.EVT_TEXT, self.onSpriteProperties, id=self.inspector.sprite_label.GetId())

        self.Bind(wx.EVT_TEXT_ENTER, self.onSpritesheetProperties, id=self.inspector.spritesheet_rows.GetId())
        self.Bind(wx.EVT_TEXT_ENTER, self.onSpritesheetProperties, id=self.inspector.spritesheet_cols.GetId())
        self.Bind(wx.EVT_TEXT_ENTER, self.onSpriteProperties, id=self.inspector.sprite_label.GetId())

        self.Bind(wx.EVT_CHECKBOX, self.onIsolateHitboxes, id=self.inspector.isolate_hitboxes.GetId())

        self.Bind(wx.EVT_SLIDER, self.onTransparency, id=self.inspector.transparency.GetId())

        self.Bind(EVT_UPDATE_INSPECTOR_HITBOX, self.onHitboxSelected)
        self.Bind(EVT_UPDATE_INSPECTOR_SPRITE, self.onSpriteSelected)

        self.inspector.DisableHitboxProperties()
        self.inspector.DisableSpriteProperties()
        self.inspector.DisableSpritesheetProperties()

    def ContinueDialog(self):
        """Checks if the current canvas is saved and if not, asks the user if
        they want to continue.

        Returns
        -------
        bool
            `True` if the user wants to continue, `False` otherwise.
        """
        if not self.canvas.saved:
            confirm_continue = wx.MessageBox(
                message="Current file has not been saved. Continue?",
                caption="Current canvas not saved",
                style=wx.ICON_QUESTION | wx.YES_NO,
                parent=self
            )

            if confirm_continue == wx.YES:
                return True

        return False

    def InitFileMenu(self):
        self.file_menu = wx.Menu()

        self.file_menu_new = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="New\tCTRL+N",
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_new)

        self.file_menu.AppendSeparator()

        self.file_menu_open = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Open\tCTRL+O",
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_open)

        self.file_menu.AppendSeparator()

        self.file_menu_close = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Close\tCTRL+W",
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_close)
        
        self.file_menu.AppendSeparator()

        self.file_menu_save = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Save\tCTRL+S",
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_save)

        self.file_menu_save_as = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Save As...\tCTRL+SHIFT+S",
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_save_as)

        self.file_menu_export_as = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Export As...\tCTRL+SHIFT+E",
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_export_as)

        self.file_menu.AppendSeparator()

        self.file_menu_exit = wx.MenuItem(
            parentMenu=self.file_menu,
            id=wx.ID_ANY,
            text="Exit\tCTRL+Q",
            kind=wx.ITEM_NORMAL,
        )
        self.file_menu.Append(self.file_menu_exit)

    def InitMenuBar(self):
        self.menu_bar = wx.MenuBar(0)

        self.InitFileMenu()
        self.menu_bar.Append(self.file_menu, "File")

        self.SetMenuBar(self.menu_bar)

    def InitToolBar(self):
        self.tool_bar = self.CreateToolBar(
            style=wx.TB_VERTICAL,
            id=wx.ID_ANY,
        )

        self.tool_select = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Select",
            bitmap=wx.Bitmap(name="assets/tool_select.png"),
            kind=wx.ITEM_CHECK,
        )

        self.tool_bar.AddSeparator()

        self.tool_move = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Move",
            bitmap=wx.Bitmap(name="assets/tool_move.png"),
            kind=wx.ITEM_CHECK,
        )

        self.tool_bar.AddSeparator()

        self.tool_draw = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Draw",
            bitmap=wx.Bitmap(name="assets/tool_draw.png"),
            kind=wx.ITEM_CHECK,
        )

        self.tool_bar.AddSeparator()

        self.tool_colour_picker = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Colour Picker",
            bitmap=wx.Bitmap(name="assets/tool_colour_picker.png"),
            kind=wx.ITEM_NORMAL,
        )

        self.tool_bar.Realize()

    def Open(self):
        """Create and show the `wx.FileDialog` to open an image."""
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

        self.inspector.spritesheet_rows.SetValue(str(1))
        self.inspector.spritesheet_cols.SetValue(str(1))

        self.inspector.EnableSpritesheetProperties()

        self.Refresh()

    def Save(self, show_dialog=False):
        """Show the `wx.FileDialog` if there is no filepath and save the 
        current canvas.
        """
        if self.filepath is None or show_dialog:
            with wx.FileDialog(
                        parent=self,
                        message="Save current canvas",
                        wildcard=SHG_WILDCARD,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                    ) as dialog:
                if dialog.ShowModal() == wx.ID_CANCEL:
                    return

                self.filepath = dialog.GetPath()

        self.canvas.Save(self.filepath)

        self.canvas.saved = True

    def onFileMenuExit(self, event):
        """Asks to save the current canvas and exits the program."""
        if self.ContinueDialog():
            self.Close()

    def onFileMenuNew(self, event):
        """Asks to save the current canvas and opens a new file."""
        if self.ContinueDialog():
            self.Open()

    def onFileMenuOpen(self, event):
        """Create and show the `wx.FileDialog` to open a file."""
        if self.ContinueDialog():
            self.Open()

    def onFileMenuSave(self, event):
        """Save the current canvas."""
        self.Save()

    def onFileMenuSaveAs(self, event):
        """Create a new file and save the current canvas."""
        self.Save(show_dialog=True)

    def onFileMenuExportAs(self, event):
        """Creates a new file and exports the current canvas."""
        with wx.FileDialog(
                    parent=self,
                    message="Export current canvas",
                    wildcard=JSON_WILDCARD,
                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                ) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            filepath = dialog.GetPath()

        self.canvas.Export(filepath)

    def onHitboxSelected(self, event):
        """Updates the hitbox properties in the inspector."""
        hitbox = self.canvas.sprites[self.canvas.select].hitboxes[self.canvas.hitbox_select]
        select = self.canvas.select_position

        self.inspector.hitbox_label.SetValue(hitbox.label)
        self.inspector.hitbox_global_x.SetValue(str(hitbox.x))
        self.inspector.hitbox_global_y.SetValue(str(hitbox.y))
        self.inspector.hitbox_local_x.SetValue(str(hitbox.x - select.x))
        self.inspector.hitbox_local_y.SetValue(str(hitbox.y - select.y))
        self.inspector.hitbox_width.SetValue(str(hitbox.w))
        self.inspector.hitbox_height.SetValue(str(hitbox.h))

        self.inspector.EnableHitboxProperties()

    def onIsolateHitboxes(self, event):
        """Updates the displayed hitboxes on the canvas."""
        self.canvas.isolate = self.inspector.isolate_hitboxes.GetValue()

        self.Refresh()

    def onSpriteProperties(self, event):
        """Updates the canvas sprite from the inspector."""
        self.canvas.sprites[self.canvas.select].label = self.inspector.sprite_label.GetValue()

    def onSpriteSelected(self, event):
        """Updates the sprite properties in the inspector."""
        select = self.canvas.select

        if select is None:
            self.inspector.DisableSpriteProperties()
        else:
            self.inspector.sprite_label.SetValue(self.canvas.sprites[select].label)

            self.inspector.EnableSpriteProperties()

    def onSpritesheetProperties(self, event):
        """Updates the canvas rulers from the inspector."""
        self.canvas.rows = int(self.inspector.spritesheet_rows.GetValue())
        self.canvas.cols = int(self.inspector.spritesheet_cols.GetValue())

        self.Refresh()

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
        """Toggles the draw tool on."""
        self.canvas.state = State.DRAW
        self.canvas.hitbox_select = None

        self.tool_bar.ToggleTool(self.tool_select.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_draw.GetId(), True)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), False)

        self.Refresh()

    def onToolMove(self, event):
        """Toggles the move tool on."""
        self.canvas.state = State.MOVE

        self.tool_bar.ToggleTool(self.tool_select.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_draw.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), True)

        self.Refresh()

    def onToolSelect(self, event):
        """Toggles the select tool on."""
        self.canvas.state = State.SELECT

        self.tool_bar.ToggleTool(self.tool_select.GetId(), True)
        self.tool_bar.ToggleTool(self.tool_draw.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), False)

        self.Refresh()

    def onTransparency(self, event):
        """Updates the hitbox transparency."""
        colour = self.canvas.hitbox_colour
        self.canvas.hitbox_colour.Set(
            colour.red,
            colour.green,
            colour.blue,
            self.inspector.transparency.GetValue()
        )

        self.Refresh()
