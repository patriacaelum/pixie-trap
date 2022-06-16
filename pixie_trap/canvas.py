import json
import numpy as np
import os
import shutil
import wx

from .constants import State
from .constants import UpdateInspectorHitboxEvent, UpdateInspectorSpriteEvent
from .primitives import Point, Rect, Rects, ScaleRects


class Canvas(wx.Panel):
    """The canvas is where the image and hitboxes are drawn and edited.

    The canvas consists of the major elements:

    - The background colour (`self.bg`)
    - An image file (`self.sheet`)
    - Rulers defining a sprite atlas (`self.rows`, `self.cols`)
    - A list of hitboxes (`self.hitboxes`, `self.destinations`)

    Parameters
    -----------
    parent: wx.Frame
        The parent window of the application.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.sheet_loaded = False
        self.isolate = False
        self.saved = True
        self.state = None

        self.magnify = 1
        self.magnify_factor = 1

        self.left_down = Point()
        self.middle_down = Point()

        self.bg_red = wx.Bitmap()
        self.bg_gray = wx.Bitmap()
        self.bg_black = wx.Bitmap()
        self.__size_bg(*self.GetSize())

        self.sheet = wx.Bitmap()
        self.sheet_pos = Rect()
        self.rows = 1
        self.cols = 1

        self.select = None # Otherwise a Point
        self.select_position = Rect()
        self.select_preview = Rect()

        # Maps sprite labels to hitbox labels, and each non-unique hitbox label
        # maps to an index in destinations
        self.sprites = dict()
        self.sprite_names = dict()
        self.destinations = Rects()
        self.n_hitboxes_created = 0
        self.hitbox_buffer = Point()
        self.hitbox_colour = wx.Colour(255, 50, 0, 50)
        self.hitbox_select = None

        self.scale_select = None
        self.scale_radius = 5
        self.scale_rects = ScaleRects()

        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)

        self.Bind(wx.EVT_MIDDLE_DOWN, self.onMiddleDown)

        self.Bind(wx.EVT_MOTION, self.onMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)

        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaintCanvas)

    def ExportJSON(self, filepath: str):
        """Exports the current canvas as JSON to disk.

        The JSON data has the structure::

            {
                "sprite_label_0": {
                    "hitbox_label_0": {
                        "x": int,
                        "y": int,
                        "w": int,
                        "h": int,
                    },
                    "hitbox_label_1": {
                        ...
                    },
                    ...
                },
                "sprite_label_1": {
                    ...
                },
                ...
            }

        Parameters
        -----------
        filepath: str
            The path to where the JSON file will be saved.
        """
        data = {
            sprite.label: {
                hitbox.label: {
                    "x": int(hitbox.x - self.select_position.x),
                    "y": int(hitbox.y - self.select_position.y),
                    "w": int(hitbox.w),
                    "h": int(hitbox.h),
                }
                for hitbox in sprite.hitboxes.values()
            }
            for sprite in self.sprites.values()
        }

        try:
            with open(filepath, "w") as file:
                json.dump(data, file, indent=4, sort_keys=True)
        except IOError:
            wx.LogError(f"Failed to save file in {filepath}")

    def FindSelectionZone(self, x: int, y: int):
        """Finds the selection zone on the canvas based on the given mouse
        position.

        The rulers are created based on the number of rows and columns defined
        in the :class:`Inspector`, and then the algorithm looks for which
        rectangle in the grid contains the given point (x, y).

        Note that according to this method, if the given point is outside the
        range of the grid, either the returned width or height will be a value
        of `0`.

        Parameters
        -----------
        x: int
            The x-coodrinate of the mouse position.
        y: int
            The y-coordinate of the mouse position.

        Returns
        -------
        rect: (int, int, int, int)
            The x-coordinate, y-coordinate, width, and height of the rectangle
            defining the selection zone relative to the original size of the
            image file.
        """
        x = (x - self.sheet_pos.x) // self.magnify_factor
        y = (y - self.sheet_pos.y) // self.magnify_factor
        w, h = self.sheet.GetSize()

        # Create rulers
        vrulers = np.arange(
            start=0,
            stop=w + 1,
            step=int(w // self.cols),
        )
        hrulers = np.arange(start=0, stop=h + 1, step=int(h // self.rows))

        # Find which rectangle in the grid contains the point (x, y)
        x_in = np.logical_and(vrulers[:-1] <= x, x < vrulers[1:])
        y_in = np.logical_and(hrulers[:-1] <= y, y < hrulers[1:])

        # Define the rectangle parameters
        rect_x = np.sum(x_in * vrulers[:-1])
        rect_y = np.sum(y_in * hrulers[:-1])
        rect_w = np.sum(x_in * vrulers[1:]) - rect_x
        rect_h = np.sum(y_in * hrulers[1:]) - rect_y

        return rect_x, rect_y, rect_w, rect_h

    def LoadImage(self, filepath: str):
        """Loads an image file to the canvas and resets magnification settings.

        Parameters
        -----------
        filepath: str
            The path to the image file.
        """
        self.sheet.LoadFile(name=filepath)
        self.sheet_pos.Set(x=0, y=0, w=self.sheet.GetWidth(), h=self.sheet.GetHeight())

        # Reset magnification settings
        self.magnify = 1
        self.magnify_factor = 1

        self.sheet_loaded = True
        self.saved = False

    def LoadPXT(self, filepath: str):
        """Loads data from a PXT file into the current canvas.

        The PXT file format is really just a tarballed directory with an image
        file and a JSON file with the hitboxes.

        The steps for loading a PXT file are:

        - Decompress the PXT file into a temporary directory
        - Load the image file
        - Load the JSON data
        - Remove the temporary directory

        The JSON data is expected to be in the format::

            {
                "spritesheet_properties": {
                    "spritesheet_rows": int,
                    "spritesheet_cols": int,
                },
                "sprite_properties": {
                    "sprite_label_0": {
                        "sprite_key": [
                            int,
                            int,
                        ],
                        "hitboxes": {
                            "hitbox_key_0": {
                                "x": int,
                                "y": int,
                                "w": int,
                                "h": int,
                                "label": str,
                            },
                            "hitbox_key_1": {
                                ...
                            },
                            ...
                        }
                    },
                    "sprite_label_1": {
                        ...
                    },
                    ...
                }
            }

        Parameters
        -----------
        filepath: str
            The path to the PXT file.
        """
        temp_dir = filepath + ".temp"
        canvas_filepath = os.path.join(temp_dir, "canvas.bmp")
        data_filepath = os.path.join(temp_dir, "data.json")

        # Decompress data into a temporary directory
        shutil.unpack_archive(
            filename=filepath,
            extract_dir=temp_dir,
            format="gztar",
        )

        with open(data_filepath, "r") as file:
            data = json.load(file)

        # Load image
        self.LoadImage(canvas_filepath)

        spritesheet_properties = data["spritesheet_properties"]
        sprite_properties = data["sprite_properties"]

        self.rows = int(spritesheet_properties["spritesheet_rows"])
        self.cols = int(spritesheet_properties["spritesheet_cols"])

        # Load hitboxes
        self.sprites = dict()

        for sprite_label, sprite in sprite_properties.items():
            sprite_key = tuple(sprite["sprite_key"])

            self.sprites[sprite_key] = Sprite(sprite_label)

            for hitbox_key, hitbox in sprite["hitboxes"].items():
                self.sprites[sprite_key].hitboxes[hitbox_key] = Rect(
                    x=hitbox["x"],
                    y=hitbox["y"],
                    w=hitbox["w"],
                    h=hitbox["h"],
                    label=hitbox["label"],
                )

        # Remove temporary directory
        shutil.rmtree(temp_dir)

        self.sheet_loaded = True
        self.saved = False

    def PaintBMP(self, gc: wx.GraphicsContext):
        """Paints the loaded image to the canvas at the current magnification
        setting.

        Parameters
        -----------
        gc: wx.GraphicsContext
            The object drawn upon.
        """
        w, h = self.sheet.GetSize()

        gc.DrawBitmap(
            bmp=self.sheet,
            x=self.sheet_pos.x,
            y=self.sheet_pos.y,
            w=w * self.magnify_factor,
            h=h * self.magnify_factor,
        )

    def PaintHitboxes(self, gc: wx.GraphicsContext):
        """Paints the drawn hitboxes to the canvas at the current magnification
        setting.

        If the `self.isolate` parameter is set to `True`, then only the hitboxes
        associated with the sprite with a label equal to `self.select` will
        be drawn.

        Parameters
        -----------
        gc: wx.GraphicsContext
            The object drawn upon.
        """
        for sprite_label, sprites in self.sprites.items():
            if self.isolate and sprite_label != self.select:
                continue

            for hitbox_label, dest_index in sprites.items():
                hitbox = self.destinations.Get(dest_index)

                if hitbox.w <= 0 or hitbox.h <= 0:
                    continue

                gc.DrawBitmap(
                    bmp=self.bg_red,
                    x=int(self.sheet_pos.x + hitbox.x * self.magnify_factor),
                    y=int(self.sheet_pos.y + hitbox.y * self.magnify_factor),
                    w=int(hitbox.w * self.magnify_factor),
                    h=int(hitbox.h * self.magnify_factor),
                )

    def PaintRulers(self, dc: wx.DC):
        """Paints the rulers on the canvas.

        The rulers are based on the number of rows and columns defined in the
        :class:`Inspector`.

        Parameters
        -----------
        dc: wx.DC
            The device context where graphics are drawn.
        """
        # Set the colour to cyan
        dc.SetPen(wx.Pen(colour=wx.Colour(0, 255, 255, 100), width=2))

        canvas_width, canvas_height = self.GetSize()

        vspace = int(self.sheet_pos.h // self.rows)
        hspace = int(self.sheet_pos.w // self.cols)

        dc.DrawLineList(
            [
                (0, self.sheet_pos.y + y, canvas_width, self.sheet_pos.y + y)
                for y in range(0, self.sheet_pos.h + 1, vspace)
            ]
        )

        dc.DrawLineList(
            [
                (self.sheet_pos.x + x, 0, self.sheet_pos.x + x, canvas_height)
                for x in range(0, self.sheet_pos.w + 1, hspace)
            ]
        )

    def PaintScale(self, gc: wx.GraphicsContext):
        """Paints the transformation scaling pins on the selected hitbox.

        The scaling pins are always the same size on the canvas, independent of
        the magnification setting. The scaling pins always consist of a circle
        in the middle of the selected hitbox and squares on each corner and
        midpoint around the perimeter.

        Parameters
        -----------
        gc: wx.GraphicsContext
            The object drawn upon.
        """
        # Set the colour to black
        gc.SetPen(wx.Pen(colour=wx.Colour(0, 0, 0, 255), width=2))
        hitbox = self.sprites[self.select].hitboxes[self.hitbox_select]

        # Draw a circle in the centre of the hitbox
        gc.DrawEllipse(
            x=int(
                self.sheet_pos.x
                + hitbox.centre.x * self.magnify_factor
                - self.scale_radius
            ),
            y=int(
                self.sheet_pos.y
                + hitbox.centre.y * self.magnify_factor
                - self.scale_radius
            ),
            w=int(2 * self.scale_radius),
            h=int(2 * self.scale_radius),
        )

        # Draw squares on each corner and midpoint around the perimeter
        self.scale_rects.Set(
            rect=hitbox,
            radius=self.scale_radius,
            factor=self.magnify_factor,
        )

        for rectangle in self.scale_rects.rects.values():
            gc.DrawRectangle(
                x=self.sheet_pos.x + rectangle.x,
                y=self.sheet_pos.y + rectangle.y,
                w=rectangle.w,
                h=rectangle.h,
            )

    def PaintSelect(self, gc: wx.GraphicsContext):
        """Paints the selection zone.

        If there is no selection zone, then the whole canvas is darkened.

        Parameters
        -----------
        gc: wx.GraphicsContext
            The object drawn upon.
        """
        w, h = self.GetSize()

        if not self.select:
            # Darken entire canvas
            gc.DrawBitmap(
                bmp=self.bg_black,
                x=0,
                y=0,
                w=w,
                h=h,
            )

        else:
            # Darken everywhere except selection zone
            top_left = Point(
                x=self.sheet_pos.x + self.select_position.x * self.magnify_factor,
                y=self.sheet_pos.y + self.select_position.y * self.magnify_factor,
            )
            top_right = Point(
                x=self.sheet_pos.x
                + (self.select_position.x + self.select_position.w)
                * self.magnify_factor,
                y=self.sheet_pos.y + self.select_position.y * self.magnify_factor,
            )
            bottom_left = Point(
                x=self.sheet_pos.x + self.select_position.x * self.magnify_factor,
                y=self.sheet_pos.y
                + (self.select_position.y + self.select_position.h)
                * self.magnify_factor,
            )
            bottom_right = Point(
                x=self.sheet_pos.x
                + (self.select_position.x + self.select_position.w)
                * self.magnify_factor,
                y=self.sheet_pos.y
                + (self.select_position.y + self.select_position.h)
                * self.magnify_factor,
            )

            if top_left.x < w and top_left.y > 0:
                gc.DrawBitmap(
                    bmp=self.bg_black,
                    x=top_left.x,
                    y=0,
                    w=w - top_left.x,
                    h=top_left.y,
                )

            if top_right.x < w and top_right.y < h:
                gc.DrawBitmap(
                    bmp=self.bg_black,
                    x=top_right.x,
                    y=top_right.y,
                    w=w - top_right.x,
                    h=h - top_right.y,
                )

            if bottom_left.x > 0 and bottom_left.y < h:
                gc.DrawBitmap(
                    bmp=self.bg_black,
                    x=0,
                    y=0,
                    w=bottom_left.x,
                    h=bottom_left.y,
                )

            if bottom_right.x > 0 and bottom_right.y < h:
                gc.DrawBitmap(
                    bmp=self.bg_black,
                    x=0,
                    y=bottom_right.y,
                    w=bottom_right.x,
                    h=h - bottom_right.y,
                )

        if self.select_preview.w > 0 and self.select_preview.h > 0:
            # Redden selection preview
            gc.DrawBitmap(
                bmp=self.bg_red,
                x=self.sheet_pos.x + self.select_preview.x * self.magnify_factor,
                y=self.sheet_pos.y + self.select_preview.y * self.magnify_factor,
                w=self.select_preview.w * self.magnify_factor,
                h=self.select_preview.h * self.magnify_factor,
            )

    def SavePXT(self, filepath: str):
        """Saves the current canvas as PXT to disk.

        The PXT file format is really just a `.tar.gz` compressed directory
        that contains the canvas image and JSON data of the hitboxes.

        The steps for saving a PXT file are:

        - Create a temporary directory
        - Save the image file
        - Save the JSON data
        - Compress the temporary directory into a PXT file
        - Remove the temporary directory

        The JSON data is written in the format::

            {
                "spritesheet_properties": {
                    "spritesheet_rows": int,
                    "spritesheet_cols": int,
                },
                "sprite_properties": {
                    "sprite_label_0": {
                        "sprite_key": [
                            int,
                            int,
                        ],
                        "hitboxes": {
                            "hitbox_key_0": {
                                "x": int,
                                "y": int,
                                "w": int,
                                "h": int,
                                "label": str,
                            },
                            "hitbox_key_1": {
                                ...
                            },
                            ...
                        }
                    },
                    "sprite_label_1": {
                        ...
                    },
                    ...
                }
            }

        Parameters
        -----------
        filepath: str
            The path of the PXT file.
        """
        temp_dir = filepath + ".temp"
        canvas_filepath = os.path.join(temp_dir, "canvas.bmp")
        data_filepath = os.path.join(temp_dir, "data.json")

        # Construct data storage
        data = {
            "spritesheet_properties": {
                "spritesheet_rows": self.rows,
                "spritesheet_cols": self.cols,
            },
        }

        sprites = dict()

        for sprite_key, sprite in self.sprites.items():
            sprites[sprite.label] = {"sprite_key": sprite_key, "hitboxes": dict()}

            for hitbox_key, hitbox in sprite.hitboxes.items():
                sprites[sprite.label]["hitboxes"][hitbox_key] = {
                    "x": hitbox.x,
                    "y": hitbox.y,
                    "w": hitbox.w,
                    "h": hitbox.h,
                    "label": hitbox.label,
                }

        data["sprite_properties"] = sprites

        # Create a temporary directory
        os.mkdir(temp_dir)

        # Save the image file
        self.sheet.SaveFile(
            name=canvas_filepath,
            type=wx.BITMAP_TYPE_BMP,
        )

        # Save the JSON data
        try:
            with open(data_filepath, "w") as file:
                json.dump(data, file)
        except IOError:
            wx.LogError(f"Failed to save file in {filepath}")

        # Compress temporary directory
        archive_filepath = shutil.make_archive(
            base_name=filepath,
            format="gztar",
            root_dir=temp_dir,
        )

        # Rename archive to PXT and remove temporary directory
        shutil.move(src=archive_filepath, dst=filepath)
        shutil.rmtree(temp_dir)

        self.saved = True

    def onKeyDown(self, event: wx.KeyEvent):
        """Processes keyboard events.

        If the `Move` tool is selected, then:

          - The position of the selected hitbox is moved by one pixel in the
            direction of the arrow key.
          - The selected hitbox is deleted if the delete key is pressed.

        Parameters
        -----------
        event: wx.KeyEvent
            The event containing information about key presses and releases.
        """
        if self.state != State.MOVE and self.hitbox_select is None:
            return

        key = event.GetKeyCode()
        hitbox = self.sprites[self.select].hitboxes[self.hitbox_select]

        if key == wx.WXK_DELETE:
            del self.sprites[self.select].hitboxes[self.hitbox_select]

            self.hitbox_select = None

        elif key == wx.WXK_LEFT:
            hitbox.x -= 1

        elif key == wx.WXK_UP:
            hitbox.y -= 1

        elif key == wx.WXK_RIGHT:
            hitbox.x += 1

        elif key == wx.WXK_DOWN:
            hitbox.y += 1

        self.Refresh()

        self.saved = False

    def onLeftDown(self, event: wx.MouseEvent):
        """Processes mouse left buttom press events.

        If the `Select` tool is selected:

        - set the sprite selected to selection zone.

        If the `Move` tool is selected and a sprite is selected:

        - if a hitbox is already selected and the user clicked on that hitbox
          again, then use that hitbox for scaling.
        - if no hitbox is being used for scaling, then look for a hitbox that
          the user pressed on.

        If the `Draw` tool is selected:
        - create a hitbox with the left corner where the user clicked.

        If any of the above actions take place, then the canvas state changes to
        not saved.

        Parameters
        -----------
        event: wx.MouseEvent
            The event containing information about mouse button presses and
            releases and mouse movements.
        """
        x, y = event.GetPosition()

        self.left_down.Set(x=x, y=y)

        if self.state == State.SELECT:
            self.select_position.Set(*self.FindSelectionZone(x, y))

            # Zero width or height means mouse click was outside of image
            if self.select_position.w == 0 and self.select_position.h == 0:
                self.select = None
            else:
                self.select = (self.select_position.x, self.select_position.y)
                self.sprite_names[self.select] = f"x{self.select[0]}_y{self.select[1]}"

                if self.sprites.get(self.select) is None:
                    self.sprites[self.select] = {}

            wx.PostEvent(self.Parent, UpdateInspectorSpriteEvent())

            self.Refresh()

        elif self.state == State.MOVE and self.select is not None:
            # Scale selected hitbox
            if self.hitbox_select is not None:
                local_position = Point(
                    x=self.left_down.x - self.sheet_pos.x,
                    y=self.left_down.y - self.sheet_pos.y,
                )

                self.scale_select = self.scale_rects.SelectScale(local_position)
                self.hitbox_buffer.Set(x=self.left_down.x, y=self.left_down.y)

            # Find a hitbox in the mouse position
            if self.scale_select is None:
                local_position = Point(
                    x=(self.left_down.x - self.sheet_pos.x) // self.magnify_factor,
                    y=(self.left_down.y - self.sheet_pos.y) // self.magnify_factor,
                )

                for label, hitbox in self.sprites[self.select].hitboxes.items():
                    if hitbox.Contains(local_position):
                        self.hitbox_buffer.Set(x=hitbox.x, y=hitbox.y)
                        self.hitbox_select = label

                        wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())

                        break

            self.Refresh()

        elif self.state == State.DRAW and self.select:
            sprite = (self.select_position.x, self.select_position.y)

            self.destinations.Append(
                Rect(
                    x=(self.left_down.x - self.sheet_pos.x) // self.magnify_factor,
                    y=(self.left_down.y - self.sheet_pos.y) // self.magnify_factor,
                    w=0,
                    h=0,
                )
            )
            self.hitbox_select = self.destinations.Size() - 1
            self.sprites[sprite][self.n_hitboxes_created] = self.hitbox_select

            self.n_hitboxes_created += 1

            self.saved = False

    def onLeftUp(self, event: wx.MouseEvent):
        """Processes mouse left button release events.

        If the `Draw` tool is selected:

        - if the user was drawing a hitbox and has a non-zero width and height,
          then the hitbox is added to the selected sprite. The hitbox is deleted
          if it has a zero width or height.

        If any of the actions above take place, then the canvas state is changed
        to not saved.

        Parameters
        -----------
        event: wx.MouseEvent
            The event containing information about mouse button presses and
            releases and mouse movements.
        """
        if self.state == State.DRAW and self.hitbox_select is not None:
            hitbox = self.destinations[self.hitbox_select]

            if hitbox.w <= 0 or hitbox.h <= 0:
                self.destinations.Delete(self.hitbox_select)

                for sprite in self.sprites.values():
                    for index in sprite.values():
                        if index > self.hitbox_select:
                            index -= 1

            else:
                self.saved = False

            self.hitbox_select = None

    def onMiddleDown(self, event: wx.MouseEvent):
        """Processes mouse middle button press events.

        The location of the mouse press is recorded for panning upon motion.

        Parameters
        -----------
        event: wx.MouseEvent
            The event containing information about mouse button presses and
            releases and mouse movements.
        """
        self.middle_down.Set(*event.GetPosition())

    def onMotion(self, event: wx.MouseEvent):
        """Processes mouse movement events.

        If the `Select` tool is selected:

        - the preview of the sprite selection is set.

        If the left button is held down and the `Move` tool is selected:

        - if the user is scaling a hitbox, then the hitbox is resized depending
          which scaling pin was pressed
        - if the user is not scaling a hitbox, then the hitbox is moved to
          where the user dragged.

        If the left button is held down and the `Draw` tool is selected:

        - draw the hitbox using the current location of the mouse as the
          opposite corner from where they pressed.

        If the middle button is held down:

        - the image, rulers, and hitboxes are moved to where the user dragged.

        Parameters
        -----------
        event: wx.MouseEvent
            The event containing information about mouse button presses and
            releases and mouse movements.
        """
        if self.state == State.SELECT:
            x, y = event.GetPosition()
            self.select_preview.Set(*self.FindSelectionZone(x, y))

            self.Refresh()

        if event.LeftIsDown() and self.hitbox_select is not None:
            x, y = event.GetPosition()

            hitbox = self.destinations[self.hitbox_select]

            if self.state == State.MOVE:
                if self.scale_select is not None:
                    # Scale hitbox
                    dx = (x - self.hitbox_buffer.x) // self.magnify_factor
                    dy = (y - self.hitbox_buffer.y) // self.magnify_factor

                    if dx != 0:
                        self.hitbox_buffer.x = x

                    if dy != 0:
                        self.hitbox_buffer.y = y

                    if dx != 0 or dy != 0:
                        hitbox.Scale(
                            scale=self.scale_select,
                            dx=dx,
                            dy=dy,
                        )

                        wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())
                        self.Refresh()

                        self.saved = False

                else:
                    # Move hitbox
                    dx = (x - self.left_down.x) // self.magnify_factor
                    dy = (y - self.left_down.y) // self.magnify_factor

                    hitbox.x = self.hitbox_buffer.x + dx
                    hitbox.y = self.hitbox_buffer.y + dy

                    if dx != 0 or dy != 0:
                        wx.PostEvent(self.Parent, UpdateInspectorHitboxEvent())
                        self.Refresh()

                        self.saved = False

            elif self.state == State.DRAW:
                dx = x - self.left_down.x
                dy = y - self.left_down.y

                if dx != 0 or dy != 0:
                    self.destinations.Set(
                        index=self.hitbox_select,
                        rect=Rect(
                            x=(min(x, self.left_down.x) - self.sheet_pos.x)
                                // self.magnify_factor,
                            y=(min(y, self.left_down.y) - self.sheet_pos.y)
                                // self.magnify_factor,
                            w=abs(dx) // self.magnify_factor,
                            h=abs(dy) // self.magnify_factor,
                        )
                    )

                    self.Refresh()

                    self.saved = False

        elif event.MiddleIsDown():
            x, y = event.GetPosition()

            dx = x - self.middle_down.x
            dy = y - self.middle_down.y

            self.sheet_pos.x += dx
            self.sheet_pos.y += dy

            self.middle_down.Set(x, y)

            self.Refresh()

    def onMouseWheel(self, event: wx.MouseEvent):
        """Processes mouse wheel events.

        Mouse wheel events are interpreted as zooming in or out, which changes
        the magnification settings.

        The magnification has a base setting of `1`, where each pixel of the
        image is one pixel on the canvas.

        If the user zooms in from the base setting, the magnification is
        increased by an integer value. Thus, one pixel of the image is rendered
        as two pixels on the canvas, or one pixel of the image is rendered as
        three pixels on the canvas, and so on.

        If the user zooms out from the base value, the magnification is
        decreased by a fraction where the denominator is increased by an
        integer value. Thus, two pixels of the image is rendered as one pixel
        on the canvas, or four pixels of the image is rendered as one pixel on
        the canvas, and so on.

        Parameters
        -----------
        event: wx.MouseEvent
            The event containing information about mouse button presses and
            releases and mouse movements.
        """
        if not self.sheet_loaded:
            return

        x, y = event.GetPosition()
        rotation = event.GetWheelRotation()

        if rotation > 0:
            self.magnify += 1

            if self.magnify == -1:
                self.magnify += 2

        elif rotation < 0:
            self.magnify -= 1

            if self.magnify == 0:
                self.magnify -= 2

        old_mag = self.magnify_factor
        self.magnify_factor = np.power(float(abs(self.magnify)), np.sign(self.magnify))

        w, h = self.sheet.GetSize()

        self.sheet_pos.Set(
            x=x - (self.magnify_factor / old_mag) * (x - self.sheet_pos.x),
            y=y - (self.magnify_factor / old_mag) * (y - self.sheet_pos.y),
            w=w * self.magnify_factor,
            h=h * self.magnify_factor,
        )

        self.Refresh()

    def onPaintCanvas(self, event: wx.PaintEvent):
        """Processes repainting events.

        This method calls the other paint methods depending on the state of the
        canvas.

        Parameters
        -----------
        event: wx.PaintEvent
            A paint event is sent when the canvas's contents need to be
            repainted.
        """
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        w, h = self.GetSize()

        # Paint background
        gc.DrawBitmap(
            bmp=self.bg_gray,
            x=0,
            y=0,
            w=w,
            h=h,
        )

        if self.sheet_loaded:
            self.PaintBMP(gc)
            self.PaintRulers(dc)

        if self.state == State.SELECT or self.select is not None:
            self.PaintSelect(gc)

        self.PaintHitboxes(gc)

        if self.state == State.MOVE and self.hitbox_select is not None:
            self.PaintScale(gc)

    def onSize(self, event: wx.SizeEvent):
        """Processes window resizing events.

        When the window is resized, the background is resized.

        Parameters
        -----------
        event: wx.SizeEvent
            The event containing information about the size change of the
            window.
        """
        self.__size_bg(*event.GetSize())

    def __size_bg(self, w: int, h: int):
        """Sets the background of the canvas as a neutral gray and black."""

        self.bg_red = wx.Bitmap.FromRGBA(
            width=1000,
            height=1000,
            red=255,
            green=0,
            blue=0,
            alpha=127,
        )
        self.bg_gray = wx.Bitmap.FromRGBA(
            width=w,
            height=h,
            red=128,
            green=128,
            blue=128,
            alpha=255,
        )
        self.bg_black = wx.Bitmap.FromRGBA(
            width=w,
            height=h,
            red=0,
            green=0,
            blue=0,
            alpha=127,
        )
