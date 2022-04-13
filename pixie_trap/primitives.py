from constants import Scale


class Point:
    """A point in space.

    Parameters
    -----------
    x: int
        The x-coordinate.
    y: int
        The y-coordinate.
    """
    def __init__(self, x: int = 0, y: int = 0):
        self.Set(x, y)

    def Set(self, x: int, y: int):
        """Sets the point position.

        Parameters
        -----------
        x: int
            The x-coordinate.
        y: int
            The y-coordinate.
        """
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f"x={self.x}, y={self.y}"


class Rect:
    """A rectangle is defined by its position and size.

    Parameters
    -----------
    x: int
        The x-coordinate of the top left corner of the rectangle.
    y: int
        The y-coordinate of the top left corner of the rectangle.
    w: int
        The width of the rectangle extending to the right.
    h: int
        The height of the rectangle extending downward.
    label: str
        The name of the rectangle.
    """
    def __init__(
                self, 
                x: int = 0, 
                y: int = 0, 
                w: int = 0, 
                h: int = 0, 
                label: str = ""
            ):
        self.label = label

        self.Set(x, y, w, h)

    def Contains(self, point: Point):
        """Checks if the given :class:`Point` is inside of the rectangle.
        
        Parameters
        -----------
        point: Point
            A point in space.

        Returns
        -------
        bool
            `True` if the point is inside the rectangle, `False` otherwise.
        """
        x_in = self.x <= point.x <= self.x + self.w
        y_in = self.y <= point.y <= self.y + self.h

        return x_in and y_in

    def Scale(self, scale: Scale, dx: int, dy: int):
        """Scales the rectangle based on the direction.
        
        Parameters
        -----------
        scale: Scale
            Determines which scaling operation is being applied.
        dx: int
            The magnitude of the scaling operation in the x-direction.
        dy: int
            The magnitude of the scaling operation in the y-direction.
        """
        if scale == Scale.TOP:
            self.y += dy
            self.h -= dy

        elif scale == Scale.LEFT:
            self.x += dx
            self.w -= dx

        elif scale == Scale.RIGHT:
            self.w += dx

        elif scale == Scale.BOTTOM:
            self.h += dy

        elif scale == Scale.TOP_LEFT:
            self.x += dx
            self.y += dy
            self.w -= dx
            self.h -= dy

        elif scale == Scale.TOP_RIGHT:
            self.y += dy
            self.w += dx
            self.h -= dy

        elif scale == Scale.BOTTOM_LEFT:
            self.x += dx
            self.w -= dx
            self.h += dy

        elif scale == Scale.BOTTOM_RIGHT:
            self.w += dx
            self.h += dy

    def Set(self, x: int, y: int, w: int, h: int):
        """Sets the rectangle position and size.

        Parameters
        -----------
        x: int
            The x-coordinate of the top left corner of the rectangle.
        y: int
            The y-coordinate of the top left corner of the rectangle.
        w: int
            The width of the rectangle, extending to the right.
        h: int
            The height of the rectangle, extending downwards.
        """
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @property
    def center(self):
        """The center point of the rectangle.

        Returns
        -------
        Point
            The position of the centre of the rectangle, rounded to the nearest
            whole number.
        """
        return self.centre

    @property
    def centre(self):
        """The centre point of the rectangle.
        
        Returns
        -------
        Point
            The position of the centre of the rectnagle, rounded to the nearest
            whole number.
        """
        return Point(x=self.x + self.w / 2, y=self.y + self.h / 2)

    def __str__(self):
        return f"x={self.x}, y={self.y}, w={self.w}, h={self.h}"


class Sprite:
    """A collection of rectangles.

    The hitboxes are a dictionary mapping a key to a :class:`Rect`.

    Parameters
    -----------
    label: str
        The name of the sprite.
    """
    def __init__(self, label: str):
        self.label = label

        self.hitboxes = dict()


class ScaleRects:
    """The scaling pins to indicate the scaling operations.

    Parameters
    -----------
    top: Rect
        The scaling pin along the top border.
    left: Rect
        The scaling pin along the left border.
    right: Rect
        The scaling pin along the right border.
    bottom: Rect
        The scaling pin along the bottom border.
    top_left: Rect
        The scaling pin at the top left corner.
    top_right: Rect
        The scaling pin at the top right corner.
    bottom_left: Rect
        The scaling pin at the bottom left corner.
    bottom_right: Rect
        The scaling pin at the bottom right corner.
    """
    def __init__(
                self, 
                top=Rect(), 
                left=Rect(),
                right=Rect(),
                bottom=Rect(),
                top_left=Rect(), 
                top_right=Rect(),
                bottom_left=Rect(),
                bottom_right=Rect(),
            ):
        self.rects = {
            Scale.TOP: top,
            Scale.LEFT: left,
            Scale.RIGHT: right,
            Scale.BOTTOM: bottom,
            Scale.TOP_LEFT: top_left,
            Scale.TOP_RIGHT: top_right,
            Scale.BOTTOM_LEFT: bottom_left,
            Scale.BOTTOM_RIGHT: bottom_right,
        }

    def SelectScale(self, point: Point):
        """Selects a scale operation based on which scaling pin contains the 
        given point.
        
        Parameters
        -----------
        point: Point
            The position of the input.

        Returns
        -------
        Scale or None
            A :class:`Scale` direction if the given point is inside one of the
            scaling pins, `None` otherwise.
        """
        for scale, rect in self.rects.items():
            if rect.Contains(point):
                return scale
        else:
            return None

    def Set(self, rect: Rect, radius: int, factor: float):
        """Sets the scaling pins based on the given rectangle.

        Parameters
        -----------
        rect: Rect
            The rectangle on which the scaling pins are set.
        radius: int
            Half of the width and height of the scaling pins. This affects the
            size of the scaling pins.
        factor: float
            The magnification factor of the rectangle. This mostly affects the
            positions of the scaling pins.
        """
        diametre = 2 * radius

        self.top.Set(
            x=rect.centre.x * factor - radius,
            y=rect.y * factor - radius,
            w=diametre,
            h=diametre,
        )

        self.left.Set(
            x=rect.x * factor - radius,
            y=rect.centre.y * factor - radius,
            w=diametre,
            h=diametre,
        )

        self.right.Set(
            x=(rect.x + rect.w) * factor - radius,
            y=rect.centre.y * factor - radius,
            w=diametre,
            h=diametre,
        )

        self.bottom.Set(
            x=rect.centre.x * factor - radius,
            y=(rect.y + rect.h) * factor - radius,
            w=diametre,
            h=diametre,
        )

        self.top_left.Set(
            x=rect.x * factor - radius,
            y=rect.y * factor - radius,
            w=diametre,
            h=diametre,
        )

        self.top_right.Set(
            x=(rect.x + rect.w) * factor - radius,
            y=rect.y * factor - radius,
            w=diametre,
            h=diametre,
        )

        self.bottom_left.Set(
            x=rect.x * factor - radius,
            y=(rect.y + rect.h) * factor - radius,
            w=diametre,
            h=diametre,
        )

        self.bottom_right.Set(
            x=(rect.x + rect.w) * factor - radius,
            y=(rect.y + rect.h) * factor - radius,
            w=diametre,
            h=diametre,
        )

    @property
    def top(self):
        """The scaling pin along the top border.

        Returns
        -------
        Rect
            The scaling pin along the top border.
        """
        return self.rects[Scale.TOP]

    @property
    def left(self):
        """The scaling pin along the left border.

        Returns
        -------
        Rect
            The scaling pin along the left border.
        """
        return self.rects[Scale.LEFT]

    @property
    def right(self):
        """The scaling pin along the right border.

        Returns
        -------
        Rect
            The scaling pin along the right border.
        """
        return self.rects[Scale.RIGHT]

    @property
    def bottom(self):
        """The scaling pin along the bottom border.

        Returns
        -------
        Rect
            The scaling pin along the bottom border.
        """
        return self.rects[Scale.BOTTOM]

    @property
    def top_left(self):
        """The scaling pin at the top left corner.

        Returns
        -------
        Rect
            The scaling pin at the top left corner.
        """
        return self.rects[Scale.TOP_LEFT]

    @property
    def top_right(self):
        """The scaling pin at the top right corner.

        Returns
        -------
        Rect
            The scaling pin at the top right corner.
        """
        return self.rects[Scale.TOP_RIGHT]

    @property
    def bottom_left(self):
        """The scaling pin at the bottom left corner.

        Returns
        -------
        Rect
            The scaling pin at the bottom left corner.
        """
        return self.rects[Scale.BOTTOM_LEFT]

    @property
    def bottom_right(self):
        """The scaling pin at the bottom right corner.

        Returns
        -------
        Rect
            The scaling pin at the bottom right corner.
        """
        return self.rects[Scale.BOTTOM_RIGHT]

