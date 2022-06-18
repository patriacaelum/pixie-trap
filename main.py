import wx

from pixie_trap.main_window import MainWindow


def main():
    """The main loop of the application."""
    app = wx.App()

    pixie_trap = MainWindow()
    pixie_trap.Show()

    app.MainLoop()


if __name__ == "__main__":
    main()
