import wx

from sprite_hitbox_generator import SpriteHitboxGenerator


def main():
    app = wx.App()

    shg = SpriteHitboxGenerator()
    shg.Show()

    app.MainLoop()


if __name__ == "__main__":
    main()
