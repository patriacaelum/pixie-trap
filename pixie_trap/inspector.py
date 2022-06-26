import wx

from pixie_trap.constants import (
    ALL_EXPAND, 
    CENTER_RIGHT, 
    ToggleIsolateEvent,
    UpdateTransparencyEvent,
)


class Inspector(wx.Panel):
    """The inspector panel displays information about objects on the canvas.

    Parameters
    ------------
    parents: wx.Frame
        the parent window of the application.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        # wxpython settings
        self.SetMaxSize(wx.Size(300, -1))

        self.__init_spritesheet_properties()
        self.__init_sprite_properties()
        self.__init_hitbox_properties()

        self.__size_components()

        self.Bind(wx.EVT_CHECKBOX, self.__on_checkbox, id=self.isolate_hitboxes.GetId())
        self.Bind(wx.EVT_SLIDER, self.__on_slider, id=self.transparency.GetId())

    def disable_hitbox_properties(self):
        """Disables the ability to edit the hitbox properties.

        The following items are disabled:

        - Hitbox global x-position
        - Hitbox global y-position
        - Hitbox local x-position
        - Hitbox local y-position
        - Hitbox width
        - Hitbox height
        - Hitbox label
        - Hitbox transparency

        """

        self.hitbox_line_label.Disable()
        self.hitbox_line_widget.Disable()

        self.hitbox_header.Disable()
        self.hitbox_header_blank.Disable()

        self.hitbox_label_label.Disable()
        self.hitbox_label.Disable()

        self.hitbox_global_x_label.Disable()
        self.hitbox_global_x.Disable()

        self.hitbox_global_y_label.Disable()
        self.hitbox_global_y.Disable()

        self.hitbox_local_x_label.Disable()
        self.hitbox_local_x.Disable()

        self.hitbox_local_y_label.Disable()
        self.hitbox_local_y.Disable()

        self.hitbox_width_label.Disable()
        self.hitbox_width.Disable()

        self.hitbox_height_label.Disable()
        self.hitbox_height.Disable()

        self.transparency_label.Disable()
        self.transparency.Disable()

    def disable_sprite_properties(self):
        """Disables the ability to edit sprite properties.

        The following items are disabled:

        - Sprite label
        - Sprite isolation

        """

        self.sprite_line_label.Disable()
        self.sprite_line_widget.Disable()

        self.sprite_header.Disable()
        self.sprite_header_blank.Disable()

        self.sprite_label_label.Disable()
        self.sprite_label.Disable()

        self.isolate_hitboxes_label.Disable()
        self.isolate_hitboxes.Disable()

    def disable_spritesheet_properties(self):
        """Disables the ability to edit spritesheet properties.

        The following items are disabled:

        - Spritesheet rows
        - Spritesheet columns

        """

        self.spritesheet_line_label.Disable()
        self.spritesheet_line_widget.Disable()

        self.spritesheet_header.Disable()
        self.spritesheet_header_blank.Disable()

        self.spritesheet_rows_label.Disable()
        self.spritesheet_rows.Disable()

        self.spritesheet_cols_label.Disable()
        self.spritesheet_cols.Disable()

    def enable_hitbox_properties(self):
        """Enables the ability to edit the hitbox properties.

        The following items are enabled:

        - Hitbox global x-position
        - Hitbox global y-position
        - Hitbox local x-position
        - Hitbox local y-position
        - Hitbox width
        - Hitbox height
        - Hitbox label
        - Hitbox transparency

        """

        self.hitbox_line_label.Enable()
        self.hitbox_line_widget.Enable()

        self.hitbox_header.Enable()
        self.hitbox_header_blank.Enable()

        self.hitbox_label_label.Enable()
        self.hitbox_label.Enable()

        self.hitbox_global_x_label.Enable()
        self.hitbox_global_x.Enable()

        self.hitbox_global_y_label.Enable()
        self.hitbox_global_y.Enable()

        self.hitbox_local_x_label.Enable()
        self.hitbox_local_x.Enable()

        self.hitbox_local_y_label.Enable()
        self.hitbox_local_y.Enable()

        self.hitbox_width_label.Enable()
        self.hitbox_width.Enable()

        self.hitbox_height_label.Enable()
        self.hitbox_height.Enable()

        self.transparency_label.Enable()
        self.transparency.Enable()

    def enable_sprite_properties(self):
        """Enables the ability to edit sprite properties.

        The following items are enabled:

        - Sprite label
        - Sprite isolation

        """

        self.sprite_line_label.Enable()
        self.sprite_line_widget.Enable()

        self.sprite_header.Enable()
        self.sprite_header_blank.Enable()

        self.sprite_label_label.Enable()
        self.sprite_label.Enable()

        self.isolate_hitboxes_label.Enable()
        self.isolate_hitboxes.Enable()

    def enable_spritesheet_properties(self):
        """Enables the ability to edit spritesheet properties.

        The following items are enabled:

        - Spritesheet rows
        - Spritesheet columns

        """

        self.spritesheet_line_label.Enable()
        self.spritesheet_line_widget.Enable()

        self.spritesheet_header.Enable()
        self.spritesheet_header_blank.Enable()

        self.spritesheet_rows_label.Enable()
        self.spritesheet_rows.Enable()

        self.spritesheet_cols_label.Enable()
        self.spritesheet_cols.Enable()

    def reset(self):
        """Resets the inspector to default parameters."""
        self.spritesheet_rows.SetValue("1")
        self.spritesheet_cols.SetValue("1")

        self.isolate_hitboxes.Enable()
        self.transparency.SetValue(127)

    def __init_hitbox_properties(self):
        """Initializes the hitbox properties.

        The following items are initialized:

        - Hitbox global x-position
        - Hitbox global y-position
        - Hitbox local x-position
        - Hitbox local y-position
        - Hitbox width
        - Hitbox height
        - Hitbox label
        - Hitbox transparency

        """

        self.hitbox_line_label = wx.StaticLine(parent=self)
        self.hitbox_line_widget = wx.StaticLine(parent=self)

        self.hitbox_header = wx.StaticText(parent=self, label="Hitbox")
        self.hitbox_header.SetFont(wx.Font(wx.FontInfo().Bold()))
        self.hitbox_header_blank = wx.StaticText(parent=self, label="")

        self.hitbox_label_label = wx.StaticText(parent=self, label="Label")
        self.hitbox_label = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_global_x_label = wx.StaticText(parent=self, label="Global x")
        self.hitbox_global_x = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_global_y_label = wx.StaticText(parent=self, label="Global y")
        self.hitbox_global_y = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_local_x_label = wx.StaticText(parent=self, label="Local x")
        self.hitbox_local_x = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_local_y_label = wx.StaticText(parent=self, label="Local y")
        self.hitbox_local_y = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_width_label = wx.StaticText(parent=self, label="Width")
        self.hitbox_width = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_height_label = wx.StaticText(parent=self, label="Height")
        self.hitbox_height = wx.TextCtrl(parent=self, size=(180, -1))

        self.transparency_label = wx.StaticText(parent=self, label="Transparency")
        self.transparency = wx.Slider(
            parent=self,
            value=127,
            minValue=0,
            maxValue=255,
            size=(180, -1),
            style=wx.SL_HORIZONTAL | wx.SL_MIN_MAX_LABELS,
        )

    def __init_sprite_properties(self):
        """Initializes the sprite properties.

        The following items are initialized:

        - Sprite label
        - Sprite isolation

        """

        self.sprite_line_label = wx.StaticLine(parent=self)
        self.sprite_line_widget = wx.StaticLine(parent=self)

        self.sprite_header = wx.StaticText(parent=self, label="Sprite")
        self.sprite_header.SetFont(wx.Font(wx.FontInfo().Bold()))
        self.sprite_header_blank = wx.StaticText(parent=self, label="")

        self.sprite_label_label = wx.StaticText(parent=self, label="Label")
        self.sprite_label = wx.TextCtrl(parent=self, size=(180, -1))

        self.isolate_hitboxes_label = wx.StaticText(parent=self, label="Isolate")
        self.isolate_hitboxes = wx.CheckBox(parent=self, label="Enable")

    def __init_spritesheet_properties(self):
        """Initialized the spritesheet properties.

        The following items are initialized:

        - Spritesheet rows
        - Spritesheet columns

        """

        self.spritesheet_line_label = wx.StaticLine(parent=self)
        self.spritesheet_line_widget = wx.StaticLine(parent=self)

        self.spritesheet_header = wx.StaticText(parent=self, label="Spritesheet")
        self.spritesheet_header.SetFont(wx.Font(wx.FontInfo().Bold()))
        self.spritesheet_header_blank = wx.StaticText(parent=self, label="")

        self.spritesheet_rows_label = wx.StaticText(parent=self, label="Rows")
        self.spritesheet_rows = wx.TextCtrl(
            parent=self,
            size=(180, -1),
            value="1",
            style=wx.TE_PROCESS_ENTER,
        )

        self.spritesheet_cols_label = wx.StaticText(parent=self, label="Columns")
        self.spritesheet_cols = wx.TextCtrl(
            parent=self,
            size=(180, -1),
            value="1",
            style=wx.TE_PROCESS_ENTER,
        )

    def __on_checkbox(self, event: wx.CommandEvent):
        """Toggles isolating hitboxes for the selected sprite.

        Parameters
        ------------
        event: wx.CommandEvent
            processes when a checkbox is clicked.
        """ 
        wx.PostEvent(self.Parent, ToggleIsolateEvent(isolate=self.isolate_hitboxes.IsChecked()))

    def __on_slider(self, event: wx.CommandEvent):
        """Changes the transparency of the hitboxes.

        Parameters
        ------------
        event: wx.CommandEvent
            generated after any change of the lider position.
        """
        wx.PostEvent(self.Parent, UpdateTransparencyEvent(alpha=self.transparency.GetValue()))

    def __size_components(self):
        """Places all the initialized items in the inspector panel."""

        sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=5)

        ##########################
        # Spritesheet Properties #
        ##########################
        sizer.Add(window=self.spritesheet_line_label, flag=ALL_EXPAND)
        sizer.Add(window=self.spritesheet_line_widget, flag=ALL_EXPAND)
        sizer.Add(window=self.spritesheet_header, flag=ALL_EXPAND)
        sizer.Add(window=self.spritesheet_header_blank, flag=ALL_EXPAND)
        sizer.Add(window=self.spritesheet_rows_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.spritesheet_rows, flag=ALL_EXPAND)
        sizer.Add(window=self.spritesheet_cols_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.spritesheet_cols, flag=ALL_EXPAND)

        #####################
        # Sprite Properties #
        #####################
        sizer.Add(window=self.sprite_line_label, flag=ALL_EXPAND)
        sizer.Add(window=self.sprite_line_widget, flag=ALL_EXPAND)
        sizer.Add(window=self.sprite_header, flag=ALL_EXPAND)
        sizer.Add(window=self.sprite_header_blank, flag=ALL_EXPAND)
        sizer.Add(window=self.sprite_label_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.sprite_label, flag=ALL_EXPAND)
        sizer.Add(window=self.isolate_hitboxes_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.isolate_hitboxes, flag=wx.ALIGN_RIGHT)

        #####################
        # Hitbox Properties #
        #####################
        sizer.Add(window=self.hitbox_line_label, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_line_widget, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_header, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_header_blank, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_label_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_label, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_global_x_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_global_x, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_global_y_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_global_y, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_local_x_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_local_x, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_local_y_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_local_y, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_width_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_width, flag=ALL_EXPAND)
        sizer.Add(window=self.hitbox_height_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_height, flag=ALL_EXPAND)
        sizer.Add(window=self.transparency_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.transparency, flag=ALL_EXPAND)

        self.SetSizer(sizer)
        self.Layout()
