import random
import math
from itertools import combinations, filterfalse
from typing import List, Tuple, Optional
from datatypes import Point, Event, Arc, Segment, PriorityQueue

class Voronoi:
    def __init__(self, points):
        self.output = []  # list of line segments
        self.arc = None  # binary tree for parabola arcs

        self.points = PriorityQueue()  # site events
        self.event = PriorityQueue()  # circle events
        self.points_copy = []  # Store the original points
        self.voronoi_vertices = []  # Store Voronoi vertices

        # bounding box
        self.x0 = -50.0
        self.x1 = -50.0
        self.y0 = 550.0
        self.y1 = 550.0

        # insert points to site event
        for pts in points:
            point = Point(pts[0], pts[1])
            self.points.push(point)
            self.points_copy.append(point)
            
            # Update bounding box
            self.x0 = min(self.x0, point.x)
            self.y0 = min(self.y0, point.y)
            self.x1 = max(self.x1, point.x)
            self.y1 = max(self.y1, point.y)
        
        # Tambahkan margin ke bounding box
        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 -= dx
        self.x1 += dx
        self.y0 -= dy
        self.y1 += dy
        
    def process(self):
        """Proses utama untuk membuat diagram Voronoi."""
        while not self.points.empty():
            if not self.event.empty() and self.event.top().x <= self.points.top().x:
                self.process_event()
            else:
                self.process_point()
        
        # Proses sisa circle events
        while not self.event.empty():
            self.process_event()
            
        self.finish_edges()

    def process_event(self):
        # get next event from circle pq
        e = self.event.pop()

        if e.valid:
            # start new edge
            s = Segment(e.p)
            self.output.append(s)

            # Add the event point (Voronoi vertex) to the list
            self.voronoi_vertices.append(e.p)

            # remove associated arc (parabola)
            a = e.a
            if a.pprev is not None:
                a.pprev.pnext = a.pnext
                a.pprev.s1 = s
            if a.pnext is not None:
                a.pnext.pprev = a.pprev
                a.pnext.s0 = s

            # finish the edges before and after a
            if a.s0 is not None: a.s0.finish(e.p)
            if a.s1 is not None: a.s1.finish(e.p)

            # recheck circle events on either side of p
            if a.pprev is not None: self.check_circle_event(a.pprev, e.x)
            if a.pnext is not None: self.check_circle_event(a.pnext, e.x)

    def get_voronoi_vertices(self):
        return [(v.x, v.y) for v in self.voronoi_vertices]

    def process_point(self):
        # get next event from site pq
        p = self.points.pop()
        # add new arc (parabola)
        self.arc_insert(p)

    def arc_insert(self, p):
        if self.arc is None:
            self.arc = Arc(p)
        else:
            # find the current arcs at p.y
            i = self.arc
            while i != None:
                flag, z = self.intersect(p, i)
                if flag:
                    # new parabola intersects arc i
                    flag, zz = self.intersect(p, i.pnext)
                    if (i.pnext != None) and (not flag):
                        i.pnext.pprev = Arc(i.p, i, i.pnext)
                        i.pnext = i.pnext.pprev
                    else:
                        i.pnext = Arc(i.p, i)
                    i.pnext.s1 = i.s1

                    # add p between i and i.pnext
                    i.pnext.pprev = Arc(p, i, i.pnext)
                    i.pnext = i.pnext.pprev

                    i = i.pnext # now i points to the new arc

                    # add new half-edges connected to i's endpoints
                    seg = Segment(z)
                    self.output.append(seg)
                    i.pprev.s1 = i.s0 = seg

                    seg = Segment(z)
                    self.output.append(seg)
                    i.pnext.s0 = i.s1 = seg

                    # check for new circle events around the new arc
                    self.check_circle_event(i, p.x)
                    self.check_circle_event(i.pprev, p.x)
                    self.check_circle_event(i.pnext, p.x)

                    return
                        
                i = i.pnext

            # if p never intersects an arc, append it to the list
            i = self.arc
            while i.pnext != None:
                i = i.pnext
            i.pnext = Arc(p, i)
            
            # insert new segment between p and i
            x = self.x0
            y = (i.pnext.p.y + i.p.y) / 2.0
            start = Point(x, y)

            seg = Segment(start)
            i.s1 = i.pnext.s0 = seg
            self.output.append(seg)

    def check_circle_event(self, i, x0):
        # look for a new circle event for arc i
        if (i.e != None) and (i.e.x  != self.x0):
            i.e.valid = False
        i.e = None

        if (i.pprev is None) or (i.pnext is None): return

        flag, x, o = self.circle(i.pprev.p, i.p, i.pnext.p)
        if flag and (x > self.x0):
            i.e = Event(x, o, i)
            self.event.push(i.e)

    def circle(self, a, b, c):
        # check if bc is a "right turn" from ab
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0: return False, None, None

        # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*(A*(c.y - b.y) - B*(c.x - b.x))

        if (G == 0): return False, None, None # Points are co-linear

        # point o is the center of the circle
        ox = 1.0 * (D*E - B*F) / G
        oy = 1.0 * (A*F - C*E) / G

        # o.x plus radius equals max x coord
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
        o = Point(ox, oy)
           
        return True, x, o
        
    def intersect(self, p, i):
        # check whether a new parabola at point p intersect with arc i
        if (i is None): return False, None
        if (i.p.x == p.x): return False, None

        a = 0.0
        b = 0.0

        if i.pprev != None:
            a = (self.intersection(i.pprev.p, i.p, 1.0*p.x)).y
        if i.pnext != None:
            b = (self.intersection(i.p, i.pnext.p, 1.0*p.x)).y

        if (((i.pprev is None) or (a <= p.y)) and ((i.pnext is None) or (p.y <= b))):
            py = p.y
            px = 1.0 * ((i.p.x)**2 + (i.p.y-py)**2 - p.x**2) / (2*i.p.x - 2*p.x)
            res = Point(px, py)
            return True, res
        return False, None

    def intersection(self, p0, p1, l):
        # get the intersection of two parabolas
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == l):
            py = p1.y
        elif (p0.x == l):
            py = p0.y
            p = p1
        else:
            # use quadratic formula
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)

            a = 1.0/z0 - 1.0/z1
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = 1.0 * (p0.y**2 + p0.x**2 - l**2) / z0 - 1.0 * (p1.y**2 + p1.x**2 - l**2) / z1

            py = 1.0 * (-b-math.sqrt(b*b - 4*a*c)) / (2*a)
            
        px = 1.0 * (p.x**2 + (p.y-py)**2 - l**2) / (2*p.x-2*l)
        res = Point(px, py)
        return res

    def finish_edges(self):
        l = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        i = self.arc
        while i.pnext != None:
            if i.s1 != None:
                p = self.intersection(i.p, i.pnext.p, l*2.0)
                i.s1.finish(p)
            i = i.pnext

    def get_output(self) -> List[Tuple[float, float, float, float]]:
        return [(o.start.x, o.start.y, o.end.x, o.end.y) if o.end else 
                (o.start.x, o.start.y, o.start.x, o.start.y) 
                for o in self.output if o.start]

    def find_largest_empty_circle(self) -> List[Tuple[float, float, float]]:
        max_radius = 0
        largest_circles = []  # To store all largest circles

        # Iterate over all Voronoi vertices (the ones where three or more edges meet)
        for vertex in self.get_voronoi_vertices():
            ox, oy = vertex[0], vertex[1]
            radius = self.distance_to_closest_site(ox, oy)
            
            # Check if the circle is empty (no points inside)
            is_empty = True
            for p in self.points_copy:
                if self.distance(ox, oy, p.x, p.y) < radius:
                    is_empty = False
                    break
            
            if is_empty and radius > max_radius:
                max_radius = radius
                largest_circles = [(ox, oy, radius)]
            elif is_empty and radius == max_radius:
                largest_circles.append((ox, oy, radius))

        return largest_circles

    def distance_to_closest_site(self, ox, oy):
        # Implement a method to find the closest site point to the given point (ox, oy)
        return min([self.distance(ox, oy, p.x, p.y) for p in self.points_copy])

    def distance(self, x1, y1, x2, y2):
        # Euclidean distance between two points
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
