import wx

from constants import CENTER_RIGHT, EXPAND


class Inspector(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.SetMaxSize(wx.Size(300, -1))

        self.InitSpritesheetProperties()
        self.InitSpriteProperties()
        self.InitHitboxProperties()

        self.SizeWidgets()

    def DisableHitboxProperties(self):
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

    def DisableSpriteProperties(self):
        self.sprite_line_label.Disable()
        self.sprite_line_widget.Disable()

        self.sprite_header.Disable()
        self.sprite_header_blank.Disable()

        self.sprite_label_label.Disable()
        self.sprite_label.Disable()

        self.transparency_label.Disable()
        self.transparency.Disable()

        self.Enable_hitboxes_label.Disable()
        self.Enable_hitboxes.Disable()

    def DisableSpritesheetProperties(self):
        self.spritesheet_line_label.Disable()
        self.spritesheet_line_widget.Disable()

        self.spritesheet_header.Disable()
        self.spritesheet_header_blank.Disable()

        self.spritesheet_width_label.Disable()
        self.spritesheet_width.Disable()

        self.spritesheet_height_label.Disable()
        self.spritesheet_height.Disable()

    def EnableHitboxProperties(self):
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

    def EnableSpriteProperties(self):
        self.sprite_line_label.Enable()
        self.sprite_line_widget.Enable()

        self.sprite_header.Enable()
        self.sprite_header_blank.Enable()

        self.sprite_label_label.Enable()
        self.sprite_label.Enable()

        self.transparency_label.Enable()
        self.transparency.Enable()

        self.Enable_hitboxes_label.Enable()
        self.Enable_hitboxes.Enable()

    def EnableSpritesheetProperties(self):
        self.spritesheet_line_label.Enable()
        self.spritesheet_line_widget.Enable()

        self.spritesheet_header.Enable()
        self.spritesheet_header_blank.Enable()

        self.spritesheet_width_label.Enable()
        self.spritesheet_width.Enable()

        self.spritesheet_height_label.Enable()
        self.spritesheet_height.Enable()

    def InitHitboxProperties(self):
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

    def InitSpriteProperties(self):
        self.sprite_line_label = wx.StaticLine(parent=self)
        self.sprite_line_widget = wx.StaticLine(parent=self)

        self.sprite_header = wx.StaticText(parent=self, label="Sprite")
        self.sprite_header.SetFont(wx.Font(wx.FontInfo().Bold()))
        self.sprite_header_blank = wx.StaticText(parent=self, label="")

        self.sprite_label_label = wx.StaticText(parent=self, label="Label")
        self.sprite_label = wx.TextCtrl(parent=self, size=(180, -1))

        self.transparency_label = wx.StaticText(parent=self, label="Transparency")
        self.transparency = wx.Slider(
            parent=self,
            value=50,
            minValue=0,
            maxValue=100,
            size=(180, -1),
            style=wx.SL_HORIZONTAL,
        )

        self.Enable_hitboxes_label = wx.StaticText(parent=self, label="Isolate")
        self.Enable_hitboxes = wx.CheckBox(parent=self, label="Enable All")

    def InitSpritesheetProperties(self):
        self.spritesheet_line_label = wx.StaticLine(parent=self)
        self.spritesheet_line_widget = wx.StaticLine(parent=self)

        self.spritesheet_header = wx.StaticText(parent=self, label="Spritesheet")
        self.spritesheet_header.SetFont(wx.Font(wx.FontInfo().Bold()))
        self.spritesheet_header_blank = wx.StaticText(parent=self, label="")

        self.spritesheet_width_label = wx.StaticText(parent=self, label="Width")
        self.spritesheet_width = wx.TextCtrl(parent=self, size=(180, -1))

        self.spritesheet_height_label = wx.StaticText(parent=self, label="Height")
        self.spritesheet_height = wx.TextCtrl(parent=self, size=(180, -1))

    def SizeWidgets(self):
        sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=5)

        ##########################
        # Spritesheet Properties #
        ##########################
        sizer.Add(window=self.spritesheet_line_label, flag=EXPAND)
        sizer.Add(window=self.spritesheet_line_widget, flag=EXPAND)
        sizer.Add(window=self.spritesheet_header, flag=EXPAND)
        sizer.Add(window=self.spritesheet_header_blank, flag=EXPAND)
        sizer.Add(window=self.spritesheet_width_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.spritesheet_width, flag=EXPAND)
        sizer.Add(window=self.spritesheet_height_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.spritesheet_height, flag=EXPAND)

        #####################
        # Sprite Properties #
        #####################
        sizer.Add(window=self.sprite_line_label, flag=EXPAND)
        sizer.Add(window=self.sprite_line_widget, flag=EXPAND)
        sizer.Add(window=self.sprite_header, flag=EXPAND)
        sizer.Add(window=self.sprite_header_blank, flag=EXPAND)
        sizer.Add(window=self.sprite_label_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.sprite_label, flag=EXPAND)
        sizer.Add(window=self.transparency_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.transparency, flag=EXPAND)
        sizer.Add(window=self.Enable_hitboxes_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.Enable_hitboxes, flag=wx.ALIGN_RIGHT)

        #####################
        # Hitbox Properties #
        #####################
        sizer.Add(window=self.hitbox_line_label, flag=EXPAND)
        sizer.Add(window=self.hitbox_line_widget, flag=EXPAND)
        sizer.Add(window=self.hitbox_header, flag=EXPAND)
        sizer.Add(window=self.hitbox_header_blank, flag=EXPAND)
        sizer.Add(window=self.hitbox_label_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_label, flag=EXPAND)
        sizer.Add(window=self.hitbox_global_x_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_global_x, flag=EXPAND)
        sizer.Add(window=self.hitbox_global_y_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_global_y, flag=EXPAND)
        sizer.Add(window=self.hitbox_local_x_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_local_x, flag=EXPAND)
        sizer.Add(window=self.hitbox_local_y_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_local_y, flag=EXPAND)
        sizer.Add(window=self.hitbox_width_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_width, flag=EXPAND)
        sizer.Add(window=self.hitbox_height_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_height, flag=EXPAND)

        self.SetSizer(sizer)
        self.Layout()
