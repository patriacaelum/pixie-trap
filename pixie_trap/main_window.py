import json
import os
import shutil

import wx

from pixie_trap.canvas import Canvas
from pixie_trap.constants import (
    BASE_DIR,
    IMAGE_WILDCARD,
    JSON_WILDCARD,
    PXT_WILDCARD,
    ALL_EXPAND,
    UpdateHitboxEvent,
    SpriteSelectedEvent,
    EVT_UPDATE_HITBOX,
    EVT_SPRITE_SELECTED,
    Mode,
)
from pixie_trap.inspector import Inspector


class MainWindow(wx.Frame):
    """The main window that houses the application.

    The main window consists of the components::

    - a menubar
    - a toolbar
    - an inspector panel
    - a canvas
    """

    def __init__(self):
        super().__init__(
            parent=None,
            title="pixie-trap",
            size=wx.Size(640, 480),
            style=wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDREN,
        )

        # wxpython settings
        self.SetDoubleBuffered(True)
        self.Maximize()
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.Centre(wx.BOTH)

        # Internal parameters
        self.saved = True
        self.savefile = None

        # Components
        self.canvas = Canvas(parent=self)
        self.inspector = Inspector(parent=self)

        self.__size_components()
        self.__init_menubar()
        self.__init_toolbar()

        self.Bind(wx.EVT_MENU, self.__on_menubar_file_new, id=self.menubar_file_new.GetId())
        self.Bind(wx.EVT_MENU, self.__on_menubar_file_save, id=self.menubar_file_save.GetId())
        self.Bind(wx.EVT_MENU, self.__on_menubar_file_save_as, id=self.menubar_file_save_as.GetId())

        self.Bind(wx.EVT_TOOL, self.__on_tool_draw, id=self.tool_draw.GetId())
        self.Bind(wx.EVT_TOOL, self.__on_tool_move, id=self.tool_move.GetId())
        self.Bind(wx.EVT_TOOL, self.__on_tool_select, id=self.tool_select.GetId())

        self.Bind(
            wx.EVT_TEXT,
            self.__on_spritesheet_properties,
            id=self.inspector.spritesheet_rows.GetId(),
        )
        self.Bind(
            wx.EVT_TEXT,
            self.__on_spritesheet_properties,
            id=self.inspector.spritesheet_cols.GetId(),
        )

        self.Bind(EVT_SPRITE_SELECTED, self.__on_sprite_selected)
        self.Bind(EVT_UPDATE_HITBOX, self.__on_update_hitbox)

    def __continue(self):
        """Checks if the current state is saved and, if not, asks the user if
        they want to continue the operation anyway.

        Returns
        ---------
        continue: bool
            `True` if the user wants to continue, `False` otherwise.
        """

        if not self.saved:
            confirm_continue = wx.MessageBox(
                parent=self,
                message="Current work has not been saved. Continue?",
                caption="Current work not saved",
                style=wx.ICON_QUESTION | wx.YES_NO,
            )

            if confirm_continue == wx.NO:
                return False
        
        return True

    def __init_menubar(self):
        """Initializes the menubar.

        The menubar consists of the items::

        - File

        """

        self.menubar = wx.MenuBar(0)

        self.__init_menubar_file()
        self.menubar.Append(self.menubar_file, "File")

        self.SetMenuBar(self.menubar)

    def __init_menubar_file(self):
        """Initializes the file menu in the menubar.

        The menu consists of the following items::

        - New...
        - Open...
        - Close
        - Save
        - Save As...
        - Export As...
        - Exit

        """

        self.menubar_file = wx.Menu()

        self.menubar_file_new = wx.MenuItem(
            parentMenu=self.menubar_file,
            id=wx.ID_ANY,
            text="New...\tCTRL+N",
            kind=wx.ITEM_NORMAL,
        )
        self.menubar_file_open = wx.MenuItem(
            parentMenu=self.menubar_file,
            id=wx.ID_ANY,
            text="Open...\tCTRL+O",
            kind=wx.ITEM_NORMAL,
        )
        self.menubar_file_close = wx.MenuItem(
            parentMenu=self.menubar_file,
            id=wx.ID_ANY,
            text="Close\tCTRL+W",
            kind=wx.ITEM_NORMAL,
        )
        self.menubar_file_save = wx.MenuItem(
            parentMenu=self.menubar_file,
            id=wx.ID_ANY,
            text="Save\tCTRL+S",
            kind=wx.ITEM_NORMAL,
        )
        self.menubar_file_save_as = wx.MenuItem(
            parentMenu=self.menubar_file,
            id=wx.ID_ANY,
            text="Save As...\tCTRL+SHIFT+S",
            kind=wx.ITEM_NORMAL,
        )
        self.menubar_file_export_as = wx.MenuItem(
            parentMenu=self.menubar_file,
            id=wx.ID_ANY,
            text="Export As...\tCTRL+SHIFT+E",
            kind=wx.ITEM_NORMAL,
        )
        self.menubar_file_exit = wx.MenuItem(
            parentMenu=self.menubar_file,
            id=wx.ID_ANY,
            text="Exit\tCTRL+Q",
            kind=wx.ITEM_NORMAL,
        )

        self.menubar_file.Append(self.menubar_file_new)
        self.menubar_file.AppendSeparator()
        self.menubar_file.Append(self.menubar_file_open)
        self.menubar_file.AppendSeparator()
        self.menubar_file.Append(self.menubar_file_close)
        self.menubar_file.AppendSeparator()
        self.menubar_file.Append(self.menubar_file_save)
        self.menubar_file.Append(self.menubar_file_save_as)
        self.menubar_file.Append(self.menubar_file_export_as)
        self.menubar_file.AppendSeparator()
        self.menubar_file.Append(self.menubar_file_exit)

    def __init_toolbar(self):
        """Initializes the toolbar.

        The toolbar icons are expected to be in the `assets` directory.

        The toolbar consists of the items::

        - Select
        - Move
        - Draw
        - Colour Picker

        """

        self.tool_bar = self.CreateToolBar(
            style=wx.TB_VERTICAL,
            id=wx.ID_ANY,
        )

        self.tool_select = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Select",
            bitmap=wx.Bitmap(name=os.path.join(BASE_DIR, "assets/tool_select.png")),
            kind=wx.ITEM_CHECK,
        )

        self.tool_bar.AddSeparator()

        self.tool_move = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Move",
            bitmap=wx.Bitmap(name=os.path.join(BASE_DIR, "assets/tool_move.png")),
            kind=wx.ITEM_CHECK,
        )

        self.tool_bar.AddSeparator()

        self.tool_draw = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Draw",
            bitmap=wx.Bitmap(name=os.path.join(BASE_DIR, "assets/tool_draw.png")),
            kind=wx.ITEM_CHECK,
        )

        self.tool_bar.AddSeparator()

        self.tool_colour_picker = self.tool_bar.AddTool(
            toolId=wx.ID_ANY,
            label="Colour Picker",
            bitmap=wx.Bitmap(
                name=os.path.join(BASE_DIR, "assets/tool_colour_picker.png")
            ),
            kind=wx.ITEM_NORMAL,
        )

        self.tool_bar.Realize()

    def __on_menubar_file_new(self, event: wx.MenuEvent):
        """Resets the canvas and loads a new spritesheet.

        Parameters
        ------------
        event: wx.MenuEvent
            contains information about the menu event.
        """
        if not self.__continue():
            return

        with wx.FileDialog(
            parent=self,
            message="Select a spritesheet",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=IMAGE_WILDCARD,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            filepath = dialog.GetPath()

        self.canvas.reset()
        self.canvas.load_spritesheet(filepath)

        self.inspector.reset()

        self.saved = False

        self.Refresh()

    def __on_menubar_file_save(self, event: wx.MenuEvent):
        """Saves the current canvas to the current savefile. Only asks to write
        to a new save file if one has not been specified.

        Parameters
        ------------
        event: wx.MenuEvent
            contains information about the menu event.
        """
        if self.savefile is None:
            self.__set_savefile()

        self.__save()

    def __on_menubar_file_save_as(self, event: wx.MenuEvent):
        """Saves the current canvas to the current savefile. Always asks to
        write to a new save file.

        Parameters
        ------------
        event: wx.MenuEvent
            contains information about the menu event.
        """
        self.__set_savefile()
        self.__save()

    def __on_sprite_selected(self, event: SpriteSelectedEvent):
        """Updates the sprite properties in the inspector.

        Parameters
        ------------
        event: SpriteSelectedEvent
            custom event with properties `label`.
        """

        self.inspector.sprite_label.SetValue(event.label)
        self.inspector.enable_sprite_properties()

    def __on_spritesheet_properties(self, event: wx.CommandEvent):
        """Updates the canvas rulers from the spritesheet properties in the
        inspector.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events from controls.
        """
        self.canvas.set_rulers(
            rows=int(self.inspector.spritesheet_rows.GetValue()),
            cols=int(self.inspector.spritesheet_cols.GetValue()),
        )

        self.saved = False

        self.Refresh()

    def __on_tool_draw(self, event: wx.CommandEvent):
        """Toggles the draw tool.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events from controls.
        """
        self.canvas.mode = Mode.DRAW
        self.canvas.hitbox_select = None

        self.inspector.disable_spritesheet_properties()
        self.inspector.disable_sprite_properties()
        self.inspector.disable_hitbox_properties()

        self.tool_bar.ToggleTool(self.tool_select.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_draw.GetId(), True)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), False)

        self.Refresh()

    def __on_tool_move(self, event: wx.CommandEvent):
        """Toggles to move tool.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events from controls.
        """
        self.canvas.mode = Mode.MOVE
        self.canvas.hitbox_select = None

        self.inspector.disable_spritesheet_properties()
        self.inspector.enable_sprite_properties()
        self.inspector.enable_hitbox_properties()

        self.tool_bar.ToggleTool(self.tool_select.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_draw.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), True)

        self.Refresh()

    def __on_tool_select(self, event: wx.CommandEvent):
        """Toggles the select tool.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events from controls.
        """
        self.canvas.mode = Mode.SELECT
        self.canvas.hitbox_select = None

        self.inspector.enable_spritesheet_properties()
        self.inspector.enable_sprite_properties()
        self.inspector.disable_hitbox_properties()

        self.tool_bar.ToggleTool(self.tool_select.GetId(), True)
        self.tool_bar.ToggleTool(self.tool_draw.GetId(), False)
        self.tool_bar.ToggleTool(self.tool_move.GetId(), False)

        self.Refresh()

    def __on_update_hitbox(self, event: UpdateHitboxEvent):
        """Updates the hitbox.

        Parameters
        ------------
        event: UpdateHitboxEvent
            custom event with properties `label`, `global_x`, `global_y`,
            `local_x`, `local_y`, `width`, `height`.
        """
        self.inspector.hitbox_label.SetValue(event.label)
        self.inspector.hitbox_global_x.SetValue(str(event.global_x))
        self.inspector.hitbox_global_y.SetValue(str(event.global_y))
        self.inspector.hitbox_local_x.SetValue(str(event.local_x))
        self.inspector.hitbox_local_y.SetValue(str(event.local_y))
        self.inspector.hitbox_width.SetValue(str(event.width))
        self.inspector.hitbox_height.SetValue(str(event.height))

    def __save(self):
        """Saves the current canvas to disk.

        The PXT file format is really just a `.tar.gz` compressed directory
        that includes the canvas image and the JSON data of the hitboxes.

        The steps for saving a PXT file are:

        - Create temporary directory
        - Save the image file
        - Save the JSON data
        - Compress the temporary directory into a PXT file
        - Remove the temporary directory

        """

        temp_dir = "temp_" + self.savefile
        spritesheet_file = os.path.join(temp_dir, "canvas.bmp")
        data_file = os.path.join(temp_dir, "data.json")

        # Create a temporary directory
        os.mkdir(temp_dir)

        # Save the spritesheet as an image file
        self.canvas.spritesheet.SaveFile(name=spritesheet_file, type=wx.BITMAP_TYPE_BMP)

        # Save the JSON data
        try:
            with open(data_file, "w") as file:
                json.dump(self.canvas.to_dict(), file)
        except IOError as error:
            wx.LogError(f"Failed to save data file in {data_file}")

        # Compress the temporary directory
        archive_file = shutil.make_archive(
            base_name=self.savefile,
            format="gztar",
            root_dir=temp_dir,
        )

        # Rename the compressed file to PXT
        shutil.move(src=archive_file, dst=self.savefile)

        # Remove the temporary directory
        shutil.rmtree(temp_dir)

        self.saved = True

    def __set_savefile(self):
        """Prompts the user to specify a save file."""

        with wx.FileDialog(
            parent=self,
            message="Save current canvas",
            wildcard=PXT_WILDCARD,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            self.savefile = dialog.GetPath()

        if os.path.splitext(self.savefile)[0] == self.savefile:
            self.savefile += ".pxt"

    def __size_components(self):
        """Initializes the components and sizes them in the window."""

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        sizer.Add(
            window=self.canvas,
            proportion=1,
            flag=ALL_EXPAND,
            border=5,
        )
        sizer.Add(
            window=self.inspector,
            proportion=1,
            flag=ALL_EXPAND,
            border=5,
        )

        self.SetSizer(sizer)
        self.Layout()
