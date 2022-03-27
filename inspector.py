import wx


class Inspector(wx.Panel):
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
        )

        side_sizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        
        self.sprite_width_label = wx.StaticText(
            parent=self,
            id=wx.ID_ANY,
            label="Sprite Width",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
        )
        side_sizer.Add(
            window=self.sprite_width_label,
            flag=wx.ALL,
        )

        self.sprite_width = wx.TextCtrl(
            parent=self,
            id=wx.ID_ANY,
            value=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_DEFAULT,
        )
        side_sizer.Add(
            window=self.sprite_width,
            flag=wx.ALL,
        )

        self.sprite_height_label = wx.StaticText(
            parent=self,
            id=wx.ID_ANY,
            label="Sprite Height",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
        )
        side_sizer.Add(
            window=self.sprite_height_label,
            flag=wx.ALL,
        )

        self.sprite_height = wx.TextCtrl(
            parent=self,
            id=wx.ID_ANY,
            value=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_DEFAULT,
        )
        side_sizer.Add(
            window=self.sprite_height,
            flag=wx.ALL,
        )

        self.transparency_label = wx.StaticText(
            parent=self,
            id=wx.ID_ANY,
            label="Transparency",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
        )
        side_sizer.Add(
            window=self.transparency_label,
            flag=wx.ALL,
        )

        self.transparency = wx.Slider(
            parent=self,
            id=wx.ID_ANY,
            value=50,
            minValue=0,
            maxValue=100,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.SL_HORIZONTAL,
        )
        side_sizer.Add(
            window=self.transparency,
            flag=wx.ALL,
        )

        self.SetSizer(side_sizer)
