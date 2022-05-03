import numpy as np
import random
import pygame

class Point:
    """A point located at (x,y) in 2D space.

    Each Point object may be associated with a payload object.

    """

    def __init__(self, x, y, payload=None):
        self.x, self.y = x, y
        self.payload = payload

    def __repr__(self):
        return "{}: {}".format(str((self.x, self.y)), repr(self.payload))

    def __str__(self):
        return "P({:.2f}, {:.2f})".format(self.x, self.y)

    def distance_to(self, other):
        try:
            other_x, other_y = other.x, other.y
        except AttributeError:
            other_x, other_y = other
        return np.hypot(self.x - other_x, self.y - other_y)
    def get_xy(self):
        return self.x,self.y,self.payload

class Rect:
    """A rectangle centred at (cx, cy) with width w and height h."""

    def __init__(self, cx, cy, w, h):
        self.cx, self.cy = cx, cy
        self.w, self.h = w, h
        self.west_edge, self.east_edge = cx - w / 2, cx + w / 2
        self.north_edge, self.south_edge = cy - h / 2, cy + h / 2

    def __repr__(self):
        return str((self.west_edge, self.east_edge, self.north_edge, self.south_edge))

    def __str__(self):
        return "({:.2f}, {:.2f}, {:.2f}, {:.2f})".format(
            self.west_edge, self.north_edge, self.east_edge, self.south_edge
        )

    def contains(self, point):
        """Is point (a Point object or (x,y) tuple) inside this Rect?"""

        try:
            point_x, point_y = point.x, point.y
        except AttributeError:
            point_x, point_y = point

        return (
            point_x >= self.west_edge
            and point_x < self.east_edge
            and point_y >= self.north_edge
            and point_y < self.south_edge
        )

    def intersects(self, other):
        """Does Rect object other interesect this Rect?"""
        return not (
            other.west_edge > self.east_edge
            or other.east_edge < self.west_edge
            or other.north_edge > self.south_edge
            or other.south_edge < self.north_edge
        )

    def draw(self, ax, c="k", lw=1, **kwargs):
        x1, y1 = self.west_edge, self.north_edge
        x2, y2 = self.east_edge, self.south_edge
        ax.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], c=c, lw=lw, **kwargs)


class QuadTree:
    """A class implementing a quadtree."""

    def __init__(self, bbox, max_points=4, depth=0):
        """Initialize this node of the quadtree.

        bbox is a Rect object defining the region from which points are
        placed into this node; max_points is the maximum number of points the
        node can hold before it must divide (branch into four more nodes);
        depth keeps track of how deep into the quadtree this node lies.

        """

        self.bbox = bbox
        self.max_points = max_points
        self.points = []
        self.depth = depth
        # A flag to indicate whether this node has divided (branched) or not.
        self.divided = False

    def __str__(self):
        """Return a string representation of this node, suitably formatted."""
        sp = " " * self.depth * 2
        s = str(self.bbox) + "\n"
        s += sp + ", ".join(str(point) for point in self.points)
        if not self.divided:
            return s
        return (
            s
            + "\n"
            + "\n".join(
                [
                    sp + "nw: " + str(self.nw),
                    sp + "ne: " + str(self.ne),
                    sp + "se: " + str(self.se),
                    sp + "sw: " + str(self.sw),
                ]
            )
        )

    def divide(self):
        """Divide (branch) this node by spawning four children nodes."""

        cx, cy = self.bbox.cx, self.bbox.cy
        w, h = self.bbox.w / 2, self.bbox.h / 2
        # The boundaries of the four children nodes are "northwest",
        # "northeast", "southeast" and "southwest" quadrants within the
        # bbox of the current node.
        self.nw = QuadTree(
            Rect(cx - w / 2, cy - h / 2, w, h), self.max_points, self.depth + 1
        )
        self.ne = QuadTree(
            Rect(cx + w / 2, cy - h / 2, w, h), self.max_points, self.depth + 1
        )
        self.se = QuadTree(
            Rect(cx + w / 2, cy + h / 2, w, h), self.max_points, self.depth + 1
        )
        self.sw = QuadTree(
            Rect(cx - w / 2, cy + h / 2, w, h), self.max_points, self.depth + 1
        )
        self.divided = True

    def insert(self, point):
        """Try to insert Point point into this QuadTree."""

        if not self.bbox.contains(point):
            # The point does not lie inside bbox: bail.
            return False
        if len(self.points) < self.max_points:
            # There's room for our point without dividing the QuadTree.
            self.points.append(point)
            return True

        # No room: divide if necessary, then try the sub-quads.
        if not self.divided:
            self.divide()

        return (
            self.ne.insert(point)
            or self.nw.insert(point)
            or self.se.insert(point)
            or self.sw.insert(point)
        )

    def query(self, bbox, found_points):
        """Find the points in the quadtree that lie within bbox."""

        if not self.bbox.intersects(bbox):
            # If the domain of this node does not intersect the search
            # region, we don't need to look in it for points.
            return False

        # Search this node's points to see if they lie within bbox ...
        for point in self.points:
            if bbox.contains(point):
                found_points.append(point)
        # ... and if this node has children, search them too.
        if self.divided:
            self.nw.query(bbox, found_points)
            self.ne.query(bbox, found_points)
            self.se.query(bbox, found_points)
            self.sw.query(bbox, found_points)
        return found_points

    def query_circle(self, bbox, centre, radius, found_points):
        """Find the points in the quadtree that lie within radius of centre.

        bbox is a Rect object (a square) that bounds the search circle.
        There is no need to call this method directly: use query_radius.

        """

        if not self.bbox.intersects(bbox):
            # If the domain of this node does not intersect the search
            # region, we don't need to look in it for points.
            return False

        # Search this node's points to see if they lie within bbox
        # and also lie within a circle of given radius around the centre point.
        for point in self.points:
            if bbox.contains(point) and point.distance_to(centre) <= radius:
                found_points.append(point)

        # Recurse the search into this node's children.
        if self.divided:
            self.nw.query_circle(bbox, centre, radius, found_points)
            self.ne.query_circle(bbox, centre, radius, found_points)
            self.se.query_circle(bbox, centre, radius, found_points)
            self.sw.query_circle(bbox, centre, radius, found_points)
        return found_points

    def query_radius(self, centre, radius, found_points):
        """Find the points in the quadtree that lie within radius of centre."""

        # First find the square that bounds the search circle as a Rect object.
        bbox = Rect(*centre, 2 * radius, 2 * radius)
        return self.query_circle(bbox, centre, radius, found_points)

    def __len__(self):
        """Return the number of points in the quadtree."""

        npoints = len(self.points)
        if self.divided:
            npoints += len(self.nw) + len(self.ne) + len(self.se) + len(self.sw)
        return npoints

    def draw(self, ax):
        """Draw a representation of the quadtree on Matplotlib Axes ax."""

        self.bbox.draw(ax)
        if self.divided:
            self.nw.draw(ax)
            self.ne.draw(ax)
            self.se.draw(ax)
            self.sw.draw(ax)
    def get_points(self):
        return self.points

def select( qt, points):
    found_points = []
    total_points = len(qt)
    display_width = 1000
    display_height = 1000
    # colors    
    white = (255,255,255) 
    blue = (50,50,160)
    black = (0,0,0)
    gray = (119,136,153)
    red = (100,0,0)
    mouseRect = False
    mouseDownCount = 0
    mousePos1 = ""
    mousePos2 = ""

    screen = pygame.display.set_mode((display_width, display_height))
    clock = pygame.time.Clock()
    rectangle_main = ""
    #   screen.fill((0,0,0,))
    screen.fill(white)

    pygame.display.update()
    running = True
    inCircle = False
    toChange = ''
    color = (255,0,0)

    circle_list = []
    #draw all points
    for circle in points:
        
        circ = [pygame.draw.circle(screen,blue,(int(circle.get_xy()[0]),int(circle.get_xy()[1])),2),circle.get_xy()[2]]
        circle_list.append(circ)
        pygame.display.flip()
    while running:  # wait for stop
        clock.tick(60)

        for event in pygame.event.get():
            pygame.display.set_caption('Found = '+str(len(found_points))+'  Total = '+str(total_points))
            if event.type == pygame.MOUSEBUTTONUP:
                
                
 

                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouseDownCount !=1:
                    print("M down ",event.pos)
                    xs,ys = pygame.mouse.get_pos()
            
                    print("1:  ",xs," ",ys)
                    mousePos1 =  pygame.mouse.get_pos()
                    mouseDownCount+=1
                elif mouseDownCount == 1 and not mouseRect :
                    mousePos2 =  pygame.mouse.get_pos()
                    xs,ys = pygame.mouse.get_pos()
            
                    print("2:  ",xs," ",ys)
                    x1 = int(mousePos1[0])
                    y1 = int(mousePos1[1])
                    x2 = int(mousePos2[0])
                    y2 = int(mousePos2[1])
                    cx = abs((x1+x2)/2)
                    cy = abs((y1+y2)/2)
                    rectangle_main = pygame.draw.rect(screen, color, pygame.Rect(x1, y1, x2-x1, y2-y1),  2)
                    print(rectangle_main[0])
                    print(cx, cy, x1-x2, y1-y2)
                    qt.query(Rect(cx, cy, abs(x1-x2), abs(y1-y2)), found_points)
                    pygame.display.set_caption('Found = '+str(len(found_points))+'  Total = '+str(total_points))
                    for point in found_points:
                        for circ in points:
                            if point.get_xy()[2] == circ.get_xy()[2]:
                                pygame.draw.circle(screen,red,(int(point.get_xy()[0]),int(point.get_xy()[1])),5)
                    #mouseRect = True
                    pygame.display.flip()
                    mouseDownCount = 0

            
            if event.type == pygame.QUIT:
                running = False
                print("Quit")

                break
def draw_circles(screen, circle_list,points):
    blue = (50,50,160)
    circle_list = []
    #draw all points
    for circle in points:
        
        circ = pygame.draw.circle(screen,blue,(int(circle.get_xy()[0]),int(circle.get_xy()[1])),2)
        circle_list.append(circ)
         
def rect( qt, points):
    found_points = []
    total_points = len(qt)
    display_width = 1000
    display_height = 1000
    # colors    
    white = (255,255,255) 
    blue = (50,50,160)
    black = (0,0,0)
    gray = (119,136,153)
    red = (100,0,0)
    mouseRect = False
    mouseDownCount = 0
    mousePos1 = ""
    mousePos2 = ""

    screen = pygame.display.set_mode((display_width, display_height))
    clock = pygame.time.Clock()
    rectangle_main = ""
    #   screen.fill((0,0,0,))
    screen.fill(white)

    pygame.display.update()
    running = True
    inCircle = False
    toChange = ''
    color = (255,0,0)

    circle_list = []
    #draw all points
    for circle in points:
        
        circ = pygame.draw.circle(screen,blue,(int(circle.get_xy()[0]),int(circle.get_xy()[1])),2)
        circle_list.append(circ)
        pygame.display.flip()
    x_init = 0
    y_init = 0
    x2_init = 100
    y2_init = 100
    #rectangle_main = pygame.draw.rect(screen, color, pygame.Rect(x_init, y_init, x2_init, y2_init),  2)
    pygame.display.flip()

    while running:  # wait for stop
        
        for event in pygame.event.get():

            pygame.display.flip()
            if event.type == pygame.QUIT:
                running = False
                print("Quit")

                break
        for y_off in range(0,1000,100):
            for x_off in range(0,1000,100):
                pygame.display.set_caption('Found = '+str(len(found_points))+'  Total = '+str(total_points))
                circle_list = []
                #draw all points
                               
                screen.fill(white)
               #x_init-=100
                x_init = x_off
                y_init = y_off
                draw_circles(circle_list=circle_list, points=points, screen=screen)
                rectangle_main = pygame.draw.rect(screen, color, pygame.Rect(x_init, y_init, 100, 100),  2)
                cx = abs((x_init+x_init+100)/2)
                cy = abs((y_init+y_init+100)/2)
                found_points = []
                qt.query(Rect(cx, cy, abs(x_init-x_init+100), abs(y_init-y_init+100)), found_points)
                pygame.display.set_caption('Found = '+str(len(found_points))+'  Total = '+str(total_points))
                for point in found_points:
                    for circ in points:
                        if point.get_xy()[2] == circ.get_xy()[2]:
                            pygame.draw.circle(screen,red,(int(point.get_xy()[0]),int(point.get_xy()[1])),5)
                pygame.display.flip()
                pygame.time.wait(200)
                clock.tick(60)

if __name__ == "__main__":
    
    bbox = Rect(500, 500, 1000, 1000)
    print(bbox)
    qt = QuadTree(bbox, 1)
    found_points = [[], [], [], []]
    temp_points = []
    for i in range(100):
        x = random.randint(1, 999)
        y = random.randint(1, 999)
        payload = {"id": i}
        p = Point(x, y, payload)
        #print(p)
        temp_points.append(p)
        qt.insert(p)


        
    select(qt,temp_points)
    rect(qt,temp_points)
    # qt.query(Rect(250, 250, 500, 500), found_points[0])
    # qt.query(Rect(750, 250, 500, 500), found_points[1])
    # qt.query(Rect(250, 750, 500, 500), found_points[2])
    # qt.query(Rect(750, 750, 500, 500), found_points[3])

    # sum = 0
    # for p in found_points:
    #     sum += len(p)
    #     print(len(p))
    # print(sum)
