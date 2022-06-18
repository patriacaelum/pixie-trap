import numpy as np

from pixie_trap.constants import Scale


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
        self.set(x=x, y=y)

    def move(self, dx: int = 0, dy: int = 0):
        self.x += int(dx)
        self.y += int(dy)

    def set(self, x: int = None, y: int = None):
        """Sets the point position.

        Parameters
        -----------
        x: int
            The x-coordinate.
        y: int
            The y-coordinate.
        """
        if x is not None:
            self.x = int(x)

        if y is not None:
            self.y = int(y)

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
        }

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

    def __init__(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0):
        self.set(x=x, y=y, w=w, h=h)

    def contains(self, point: Point):
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

    def move(self, dx: int = 0, dy: int = 0):
        self.x += int(dx)
        self.y += int(dy)

    def scale(self, scale: Scale, dx: int, dy: int):
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
        dx = int(dx)
        dy = int(dy)

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

    def set(self, x: int = None, y: int = None, w: int = None, h: int = None):
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
        if x is not None:
            self.x = int(x)

        if y is not None:
            self.y = int(y)

        if w is not None:
            self.w = int(w)

        if h is not None:
            self.h = int(h)

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
        }

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


class Rects:
    """Represents a group of rectangles.

    This class uses numpy arrays for faster calculations.
    """

    def __init__(self, rects: list = None):
        if rects is None:
            rects = []

        x = []
        y = []
        w = []
        h = []

        for rect in rects:
            x.append(rect.x)
            y.append(rect.y)
            w.append(rect.w)
            h.append(rect.h)

        self.rects = np.array([x, y, w, h])

    def append(self, rect: Rect):
        self.rects = np.append(self.rects, [[rect.x], [rect.y], [rect.w], [rect.h]], axis=1) 

    def delete(self, index: int):
        self.rects = np.delete(self.rects, index, axis=1)

    def get(self, index: int):
        return self[index]

    def insert(self, index: int, rect: Rect):
        self.rects = np.insert(self.rects, index, [rect.x, rect.y, rect.w, rect.h], axis=1)

    def move(self, dx: int = 0, dy: int = 0):
        """Moves all rectangles."""
        self.x += dx
        self.y += dy

    def move_rect(self, index: int, dx: int = 0, dy: int = 0):
        """Moves a single rectangle."""
        self.x[index] += dx
        self.y[index] += dy

    def set(self, index: int, rect: Rect):
        self[index] = rect

    def size(self):
        return len(self)

    @property
    def x(self):
        return self.rects[0]

    @x.setter
    def x(self, value):
        self.rects[0] = value

    @property 
    def y(self):
        return self.rects[1]

    @y.setter 
    def y(self, value):
        self.rects[1] = value

    @property 
    def w(self):
        return self.rects[2]

    @w.setter 
    def w(self, value):
        self.rects[2] = value

    @property 
    def h(self):
        return self.rects[3]

    @h.setter 
    def h(self, value):
        self.rects[3] = value

    def __len__(self):
        return self.rects.shape[1]

    def __getitem__(self, key: int):
        return Rect(*self.rects[:, key])

    def __setitem__(self, key: int, value: Rect):
        self.rects[:, key] = [value.x, value.y, value.w, value.h]


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
        self.rects = Rects()
        self.rects.append(top)
        self.rects.append(left)
        self.rects.append(right)
        self.rects.append(bottom)
        self.rects.append(top_left)
        self.rects.append(top_right)
        self.rects.append(bottom_left)
        self.rects.append(bottom_left)

        self.keys = {
            Scale.TOP: 0,
            Scale.LEFT: 1,
            Scale.RIGHT: 2,
            Scale.BOTTOM: 3,
            Scale.TOP_LEFT: 4,
            Scale.TOP_RIGHT: 5,
            Scale.BOTTOM_LEFT: 6,
            Scale.BOTTOM_RIGHT: 7,
        }

    def move(self, dx: int = 0, dy: int = 0):
        self.rects.move(dx=dx, dy=dy)

    def select_scale(self, point: Point):
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
        for scale, index in self.keys.items():
            if self.rects.get(index).contains(point):
                return scale

        return None

    def set(self, rect: Rect, radius: int = 10):
        """Sets the scaling pins based on the given rectangle.

        Parameters
        -----------
        rect: Rect
            The rectangle on which the scaling pins are set.
        radius: int
            Half of the width and height of the scaling pins. This affects the
            size of the scaling pins.
        """
        diametre = 2 * radius

        self.rects.set(
            index=0,
            rect=Rect(
                x=rect.centre.x - radius,
                y=rect.y - radius,
                w=diametre,
                h=diametre,
            ),
        )

        self.rects.set(
            index=1,
            rect=Rect(
                x=rect.x - radius,
                y=rect.centre.y - radius,
                w=diametre,
                h=diametre,
            ),
        )

        self.rects.set(
            index=2,
            rect=Rect(
                x=rect.x + rect.w - radius,
                y=rect.centre.y - radius,
                w=diametre,
                h=diametre,
            ),
        )

        self.rects.set(
            index=3,
            rect=Rect(
                x=rect.centre.x - radius,
                y=rect.y + rect.h - radius,
                w=diametre,
                h=diametre,
            ),
        )

        self.rects.set(
            index=4,
            rect=Rect(
                x=rect.x - radius,
                y=rect.y - radius,
                w=diametre,
                h=diametre,
            ),
        )

        self.rects.set(
            index=5,
            rect=Rect(
                x=rect.x + rect.w - radius,
                y=rect.y - radius,
                w=diametre,
                h=diametre,
            ),
        )

        self.rects.set(
            index=6,
            rect=Rect(
                x=rect.x - radius,
                y=rect.y + rect.h - radius,
                w=diametre,
                h=diametre,
            ),
        )

        self.rects.set(
            index=7,
            rect=Rect(
                x=rect.x + rect.w - radius,
                y=rect.y + rect.h - radius,
                w=diametre,
                h=diametre,
            ),
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
