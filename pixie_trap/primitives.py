from constants import Scale


class Point:
    def __init__(self, x=0, y=0):
        self.Set(x, y)

    def Set(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f"x={self.x}, y={self.y}"


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0, label=""):
        self.label = label

        self.Set(x, y, w, h)

    def Contains(self, point):
        """Returns `True` if the point is inside the rectangle, otherwise `False`."""
        x_in = self.x <= point.x <= self.x + self.w
        y_in = self.y <= point.y <= self.y + self.h

        return x_in and y_in

    def Scale(self, scale, dx, dy):
        """Scales the rectangle based on the direction."""
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

    def Set(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @property
    def center(self):
        """The center point of the rectangle."""
        return self.centre

    @property
    def centre(self):
        """The centre point of the rectangle."""
        return Point(x=self.x + self.w / 2, y=self.y + self.h / 2)

    def __str__(self):
        return f"x={self.x}, y={self.y}, w={self.w}, h={self.h}"


class Sprite:
    def __init__(self, label):
        self.label = label

        self.hitboxes = dict()


class ScaleRects:
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

    def SelectScale(self, point):
        """Selects a scaleation based on which rectangle contains the given point."""
        for scale, rect in self.rects.items():
            if rect.Contains(point):
                return scale
        else:
            return None

    def Set(self, rect, radius, factor):
        """Sets the scale rectangles based on the given rectangle and radius."""
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
        return self.rects[Scale.TOP]

    @property
    def left(self):
        return self.rects[Scale.LEFT]

    @property
    def right(self):
        return self.rects[Scale.RIGHT]

    @property
    def bottom(self):
        return self.rects[Scale.BOTTOM]

    @property
    def top_left(self):
        return self.rects[Scale.TOP_LEFT]

    @property
    def top_right(self):
        return self.rects[Scale.TOP_RIGHT]

    @property
    def bottom_left(self):
        return self.rects[Scale.BOTTOM_LEFT]

    @property
    def bottom_right(self):
        return self.rects[Scale.BOTTOM_RIGHT]
