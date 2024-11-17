import math
from typing import List, Tuple
from datatypes import Point, CircleEvent, Arc, Segment, PriorityQueue

class Voronoi:
    def __init__(self, points):
        self.segments = []
        self.arc = None
        self.site_events = PriorityQueue()
        self.circle_events = PriorityQueue()
        self.original_points = [] 
        self.voronoi_vertices = []

        # Bounding box
        self.x0, self.x1 = -50.0, -50.0
        self.y0, self.y1 = 550.0, 550.0

        # Insert points into site event PQ
        for x,y in points:
            point = Point(x, y)
            self.site_events.push(point)
            self.original_points.append(point)
            self.x0, self.y0 = min(self.x0, x), min(self.y0, y)
            self.x1, self.y1 = max(self.x1, x), max(self.y1, y)
        
        # Add margins to the bounding box
        dx, dy = (self.x1 - self.x0 + 1) / 5.0, (self.y1 - self.y0 + 1) / 5.0
        self.x0 -= dx
        self.x1 += dx
        self.y0 -= dy
        self.y1 += dy
        
    def process(self):
        """Processing all the points to create the voronoi diagram."""
        while not self.site_events.empty():
            if not self.circle_events.empty() and self.circle_events.top().x <= self.site_events.top().x:
                self.process_circle_event()
            else:
                self.process_site_event()
        
        while not self.circle_events.empty():
            self.process_circle_event()
            
        self.finish_edges()

    def process_site_event(self):
        point = self.site_events.pop()
        self.arc_insert(point)

    def process_circle_event(self):
        circle_event = self.circle_events.pop()

        if circle_event.valid:
            segment = Segment(circle_event.point)
            self.segments.append(segment)
            self.voronoi_vertices.append(circle_event.point)

            arc = circle_event.arc
            if arc.pprev is not None:
                arc.pprev.pnext = arc.pnext
                arc.pprev.s1 = segment
            if arc.pnext is not None:
                arc.pnext.pprev = arc.pprev
                arc.pnext.s0 = segment

            # Finish the edges before and after this arc
            if arc.s0 is not None:
                arc.s0.finish(circle_event.point)
            if arc.s1 is not None:
                arc.s1.finish(circle_event.point)

            # Recheck circle events on either side of the associated point
            if arc.pprev is not None:
                self.check_circle_event(arc.pprev, circle_event.x)
            if arc.pnext is not None:
                self.check_circle_event(arc.pnext, circle_event.x)

    def get_voronoi_vertices(self):
        return [(v.x, v.y) for v in self.voronoi_vertices]

    def arc_insert(self, p):
        if self.arc is None:
            self.arc = Arc(p)
        else:
            # Find the current arcs at p.y
            i = self.arc
            while i != None:
                flag, z = self.intersect(p, i)
                if flag:
                    # new parabola intersects arc i
                    flag, zz = self.intersect(p, i.pnext)
                    if (i.pnext != None) and (not flag):
                        i.pnext.pprev = Arc(i.focus, i, i.pnext)
                        i.pnext = i.pnext.pprev
                    else:
                        i.pnext = Arc(i.focus, i)
                    i.pnext.s1 = i.s1

                    # add p between i and i.pnext
                    i.pnext.pprev = Arc(p, i, i.pnext)
                    i.pnext = i.pnext.pprev

                    i = i.pnext # now i points to the new arc

                    # add new half-edges connected to i's endpoints
                    seg = Segment(z)
                    self.segments.append(seg)
                    i.pprev.s1 = i.s0 = seg

                    seg = Segment(z)
                    self.segments.append(seg)
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
            y = (i.pnext.focus.y + i.focus.y) / 2.0
            start = Point(x, y)

            seg = Segment(start)
            i.s1 = i.pnext.s0 = seg
            self.segments.append(seg)

    def check_circle_event(self, i, x0):
        # look for a new circle event for arc i
        if (i.circle_event != None) and (i.circle_event.x != self.x0):
            i.circle_event.valid = False
        i.circle_event = None

        if (i.pprev is None) or (i.pnext is None): return

        flag, x, o = self.circle(i.pprev.focus, i.focus, i.pnext.focus)
        if flag and (x > self.x0):
            i.circle_event = CircleEvent(x, o, i)
            self.circle_events.push(i.circle_event)

    def circle(self, a, b, c):
        # Check if bc is a "right turn" from ab
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
        if (i.focus.x == p.x): return False, None

        a = 0.0
        b = 0.0

        if i.pprev != None:
            a = (self.intersection(i.pprev.focus, i.focus, 1.0*p.x)).y
        if i.pnext != None:
            b = (self.intersection(i.focus, i.pnext.focus, 1.0*p.x)).y

        if (((i.pprev is None) or (a <= p.y)) and ((i.pnext is None) or (p.y <= b))):
            py = p.y
            px = 1.0 * ((i.focus.x)**2 + (i.focus.y-py)**2 - p.x**2) / (2*i.focus.x - 2*p.x)
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
                p = self.intersection(i.focus, i.pnext.focus, l*2.0)
                i.s1.finish(p)
            i = i.pnext

    def get_output(self) -> List[Tuple[float, float, float, float]]:
        return [(o.start.x, o.start.y, o.end.x, o.end.y) if o.end else 
                (o.start.x, o.start.y, o.start.x, o.start.y) 
                for o in self.segments if o.start]

    def find_largest_empty_circle(self) -> List[Tuple[float, float, float]]:
        max_radius = 0
        largest_circles = []

        for vertex in self.get_voronoi_vertices():
            ox, oy = vertex[0], vertex[1]
            radius = self.distance_to_closest_site(ox, oy)
            
            is_empty = True
            for p in self.original_points:
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
        return min([self.distance(ox, oy, p.x, p.y) for p in self.original_points])

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
