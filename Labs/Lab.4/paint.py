#Lab 4 - Q10

PI = 3.14

class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Empty canvas is a matrix with element being the "space" character
        self.data = [[' '] * width for i in range(height)]

    def set_pixel(self, row, col, char='*'):
        # (simple safety check so we don't crash)
        if 0 <= row < self.height and 0 <= col < self.width:
            self.data[row][col] = char

    def get_pixel(self, row, col):
        return self.data[row][col]
    
    def clear_canvas(self):
        self.data = [[' '] * self.width for i in range(self.height)]
    
    def v_line(self, x, y, w, **kargs):
        for i in range(x, x + w):
            self.set_pixel(i, y, **kargs)

    def h_line(self, x, y, h, **kargs):
        for i in range(y, y + h):
            self.set_pixel(x, i, **kargs)
            
    def line(self, x1, y1, x2, y2, **kargs):
        # simple line from lecture (works best for gentle slopes)
        if x2 == x1:
            # vertical
            step = 1
            if y2 < y1:
                step = -1
            for y in range(y1, y2 + step, step):
                self.set_pixel(x1, y, **kargs)
            return

        slope = (y2 - y1) / (x2 - x1)

        step = 1
        if y2 < y1:
            step = -1

        for y in range(y1, y2 + step, step):
            x = int(x1 + (y - y1) / slope) if slope != 0 else x1
            self.set_pixel(x, y, **kargs)
            
    def display(self):
        print("\n".join(["".join(row) for row in self.data]))


class Shape:

    def get_points(self):
        # up to 16 (x,y) perimeter points
        return []

    def contains(self, x, y):
        return False

    def overlaps(self, other):

        for (x, y) in self.get_points():
            if other.contains(x, y):
                return True

        return False

    def paint(self, canvas, char='*'):
        # default paint: just plot the perimeter points
        for (x, y) in self.get_points():
            canvas.set_pixel(x, y, char=char)


class Rectangle(Shape):

    def __init__(self, length, width, x, y):
        self.__length = length
        self.__width = width
        self.__x = x
        self.__y = y

    def get_points(self):

        x = self.__x
        y = self.__y
        L = self.__length
        W = self.__width

        points = []

        # 4 corners
        points.append((x, y))
        points.append((x + L, y))
        points.append((x + L, y + W))
        points.append((x, y + W))

        # add edge midpoints if we still have room to reach up to 16
        if len(points) < 16:
            points.append((x + (L // 2), y))
        if len(points) < 16:
            points.append((x + (L // 2), y + W))
        if len(points) < 16:
            points.append((x, y + (W // 2)))
        if len(points) < 16:
            points.append((x + L, y + (W // 2)))

        return points[:16]

    def contains(self, x, y):

        left = self.__x
        right = self.__x + self.__length
        bottom = self.__y
        top = self.__y + self.__width

        return (left <= x <= right) and (bottom <= y <= top)

    def paint(self, canvas, char='#'):

        x = self.__x
        y = self.__y
        L = self.__length
        W = self.__width

        # top and bottom edges
        for col in range(y, y + W + 1):
            canvas.set_pixel(x, col, char=char)
            canvas.set_pixel(x + L, col, char=char)

        # left and right edges
        for row in range(x, x + L + 1):
            canvas.set_pixel(row, y, char=char)
            canvas.set_pixel(row, y + W, char=char)


class Circle(Shape):

    def __init__(self, radius, x, y):
        self.__radius = radius
        self.__x = x
        self.__y = y

    def __sqrt(self, value):
        # Newton method sqrt (no libraries)
        if value == 0:
            return 0

        guess = value
        for i in range(20):
            guess = 0.5 * (guess + value / guess)
        return guess

    def get_points(self):

        cx = self.__x
        cy = self.__y
        r = self.__radius

        points = []

        if r == 0:
            points.append((cx, cy))
            return points

        # make up to 16 points by sampling x values
        # choose up to 8 x samples, add top/bottom points for each
        samples = 8
        if r < 4:
            samples = 2 * r + 1  # small circles: fewer samples

        if samples < 2:
            samples = 2

        step = (2 * r) / (samples - 1)

        k = 0
        while k < samples and len(points) < 16:
            x_off = int(-r + (k * step))
            inside = (r * r) - (x_off * x_off)

            if inside < 0:
                inside = 0

            y_off = int(self.__sqrt(inside))

            points.append((cx + x_off, cy + y_off))
            if len(points) < 16:
                points.append((cx + x_off, cy - y_off))

            k = k + 1

        return points[:16]

    def contains(self, x, y):

        dx = x - self.__x
        dy = y - self.__y

        return (dx * dx + dy * dy) <= (self.__radius * self.__radius)

    def paint(self, canvas, char='o'):
        # draw perimeter points (up to 16)
        for (x, y) in self.get_points():
            canvas.set_pixel(x, y, char=char)


class Triangle(Shape):

    def __init__(self, base, height, x, y):
        self.__base = base
        self.__height = height
        self.__x = x
        self.__y = y

    def get_points(self):

        x = self.__x
        y = self.__y
        b = self.__base
        h = self.__height

        points = []

        # 3 corners
        points.append((x, y))
        points.append((x + b, y))
        points.append((x, y + h))

        steps = 13
        if steps > 13:
            steps = 13

        i = 1
        while i <= steps and len(points) < 16:
            # move i/steps along the diagonal
            tx = x + b - int((b * i) / steps)
            ty = y + int((h * i) / steps)
            points.append((tx, ty))
            i = i + 1

        return points[:16]

    def contains(self, x, y):

        x0 = self.__x
        y0 = self.__y
        b = self.__base
        h = self.__height

        # bounding box
        if x < x0 or y < y0:
            return False
        if x > x0 + b or y > y0 + h:
            return False

        # right triangle test (no division version)
        dx = x - x0
        dy = y - y0

        return (dx * h) + (dy * b) <= (b * h)

    def paint(self, canvas, char='^'):

        x = self.__x
        y = self.__y
        b = self.__base
        h = self.__height

        # base edge
        for col in range(y, y + b + 1):
            canvas.set_pixel(x, col, char=char)

        # left edge
        for row in range(x, x + h + 1):
            canvas.set_pixel(row, y, char=char)

        # hypotenuse (simple sampled points)
        for (px, py) in self.get_points():
            canvas.set_pixel(px, py, char=char)


class CompoundShape(Shape):

    def __init__(self, shapes):
        self.shapes = shapes

    def get_points(self):
        points = []
        for s in self.shapes:
            for p in s.get_points():
                if len(points) < 16:
                    points.append(p)
        return points

    def contains(self, x, y):
        for s in self.shapes:
            if s.contains(x, y):
                return True
        return False

    def paint(self, canvas, char='*'):
        for s in self.shapes:
            # each shape uses its own default char
            s.paint(canvas)


if __name__ == "__main__":

    c = Canvas(60, 25)

    r = Rectangle(8, 18, 2, 2)      # (length,height-ish), (width)
    cir = Circle(6, 12, 40)         # radius, center (x,y)
    t = Triangle(12, 8, 14, 5)      # base, height, (x,y)

    combo = CompoundShape([r, cir, t])

    combo.paint(c)

    c.display()

    # quick overlap tests
    print("Rectangle overlaps Circle:", r.overlaps(cir))
    print("Circle overlaps Rectangle:", cir.overlaps(r))
    print("Rectangle overlaps Triangle:", r.overlaps(t))




# Question 11 

class RasterDrawing:

    def __init__(self):

        # store shapes in a list
        self.shapes = []


    def add_shape(self, shape):

        # add a shape to the drawing
        self.shapes.append(shape)


    def paint(self, canvas):

        # draw every shape
        for s in self.shapes:
            s.paint(canvas)
