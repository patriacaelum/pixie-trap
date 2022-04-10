import wx

from frame import Frame


def main():
    app = wx.App()

    pixie_trap = Frame()
    pixie_trap.Show()

    app.MainLoop()


if __name__ == "__main__":
    main()
