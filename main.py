import wx

from pixie_trap.frame import Frame


def main():
    """The main loop of the application."""
    app = wx.App()

    pixie_trap = Frame()
    pixie_trap.Show()

    app.MainLoop()


if __name__ == "__main__":
    main()
