import wx

from constants import CENTER_RIGHT, EXPAND


class Inspector(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.SetMaxSize(wx.Size(300, -1))

        self.InitSpritesheetProperties()
        self.InitSpriteProperties()
        self.InitHitboxProperties()

        sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=5)

        ##########################
        # Spritesheet Properties #
        ##########################
        sizer.Add(window=self.spritesheet_top_line_label, flag=EXPAND)
        sizer.Add(window=self.spritesheet_top_line_widget, flag=EXPAND)
        sizer.Add(window=self.spritesheet_header, flag=EXPAND)
        sizer.Add(window=self.spritesheet_header_blank, flag=EXPAND)
        sizer.Add(window=self.spritesheet_bottom_line_label, flag=EXPAND)
        sizer.Add(window=self.spritesheet_bottom_line_widget, flag=EXPAND)
        sizer.Add(window=self.spritesheet_width_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.spritesheet_width, flag=EXPAND)
        sizer.Add(window=self.spritesheet_height_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.spritesheet_height, flag=EXPAND)

        #####################
        # Sprite Properties #
        #####################
        sizer.Add(window=self.sprite_top_line_label, flag=EXPAND)
        sizer.Add(window=self.sprite_top_line_widget, flag=EXPAND)
        sizer.Add(window=self.sprite_header, flag=EXPAND)
        sizer.Add(window=self.sprite_header_blank, flag=EXPAND)
        sizer.Add(window=self.sprite_bottom_line_label, flag=EXPAND)
        sizer.Add(window=self.sprite_bottom_line_widget, flag=EXPAND)
        sizer.Add(window=self.sprite_label_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.sprite_label, flag=EXPAND)
        sizer.Add(window=self.transparency_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.transparency, flag=EXPAND)
        sizer.Add(window=self.show_hitboxes_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.show_hitboxes, flag=wx.ALIGN_RIGHT)

        #####################
        # Hitbox Properties #
        #####################
        sizer.Add(window=self.hitbox_top_line_label, flag=EXPAND)
        sizer.Add(window=self.hitbox_top_line_widget, flag=EXPAND)
        sizer.Add(window=self.hitbox_header, flag=EXPAND)
        sizer.Add(window=self.hitbox_header_blank, flag=EXPAND)
        sizer.Add(window=self.hitbox_bottom_line_label, flag=EXPAND)
        sizer.Add(window=self.hitbox_bottom_line_widget, flag=EXPAND)
        sizer.Add(window=self.hitbox_x_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_x, flag=EXPAND)
        sizer.Add(window=self.hitbox_y_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_y, flag=EXPAND)
        sizer.Add(window=self.hitbox_w_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_w, flag=EXPAND)
        sizer.Add(window=self.hitbox_h_label, flag=CENTER_RIGHT)
        sizer.Add(window=self.hitbox_h, flag=EXPAND)

        self.SetSizer(sizer)

    def InitHitboxProperties(self):
        self.hitbox_top_line_label = wx.StaticLine(parent=self)
        self.hitbox_top_line_widget = wx.StaticLine(parent=self)

        self.hitbox_header = wx.StaticText(parent=self, label="Hitbox")
        self.hitbox_header_blank = wx.StaticText(parent=self, label="")

        self.hitbox_bottom_line_label = wx.StaticLine(parent=self)
        self.hitbox_bottom_line_widget = wx.StaticLine(parent=self)

        self.hitbox_x_label = wx.StaticText(parent=self, label="x")
        self.hitbox_x = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_y_label = wx.StaticText(parent=self, label="y")
        self.hitbox_y = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_w_label = wx.StaticText(parent=self, label="w")
        self.hitbox_w = wx.TextCtrl(parent=self, size=(180, -1))

        self.hitbox_h_label = wx.StaticText(parent=self, label="h")
        self.hitbox_h = wx.TextCtrl(parent=self, size=(180, -1))

    def InitSpriteProperties(self):
        self.sprite_top_line_label = wx.StaticLine(parent=self)
        self.sprite_top_line_widget = wx.StaticLine(parent=self)

        self.sprite_header = wx.StaticText(parent=self, label="Sprite")
        self.sprite_header_blank = wx.StaticText(parent=self, label="")

        self.sprite_bottom_line_label = wx.StaticLine(parent=self)
        self.sprite_bottom_line_widget = wx.StaticLine(parent=self)

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

        self.show_hitboxes_label = wx.StaticText(parent=self, label="Isolate")
        self.show_hitboxes = wx.CheckBox(parent=self, label="Show All")

    def InitSpritesheetProperties(self):
        self.spritesheet_top_line_label = wx.StaticLine(parent=self)
        self.spritesheet_top_line_widget = wx.StaticLine(parent=self)

        self.spritesheet_header = wx.StaticText(parent=self, label="Spritesheet")
        self.spritesheet_header_blank = wx.StaticText(parent=self, label="")

        self.spritesheet_bottom_line_label = wx.StaticLine(parent=self)
        self.spritesheet_bottom_line_widget = wx.StaticLine(parent=self)

        self.spritesheet_width_label = wx.StaticText(parent=self, label="Width")
        self.spritesheet_width = wx.TextCtrl(parent=self, size=(180, -1))

        self.spritesheet_height_label = wx.StaticText(parent=self, label="Height")
        self.spritesheet_height = wx.TextCtrl(parent=self, size=(180, -1))
