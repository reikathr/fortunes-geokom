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
    
    def get_voronoi_vertices(self):
        return [(v.x, v.y) for v in self.voronoi_vertices]
        
    def process(self):
        """Processing all the points to create the voronoi diagram."""
        while not self.site_events.empty():
            if self.circle_events.empty() or self.circle_events.top().x > self.site_events.top().x:
                self.handle_site_event()
            else:
                self.handle_circle_event()
        
        while not self.circle_events.empty():
            self.handle_circle_event()
            
        self.finish_edges()

    def handle_site_event(self):
        point = self.site_events.pop()
        self.insert_arc(point)

    def handle_circle_event(self):
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


    def insert_arc(self, p):
        if self.arc is None:
            self.arc = Arc(p)
            return

        i = self.arc
        while i:
            # Check for intersection with the current arc
            flag, z = self.intersect(p, i)
            if flag:
                # Handle intersection with i and i.pnext
                if i.pnext and not self.intersect(p, i.pnext)[0]:
                    i.pnext.pprev = Arc(i.focus, i, i.pnext)
                    i.pnext = i.pnext.pprev
                else:
                    i.pnext = Arc(i.focus, i)

                # Insert new arc and update segments
                i.pnext.s1 = i.s1
                i.pnext.pprev = Arc(p, i, i.pnext)
                i.pnext = i.pnext.pprev
                i = i.pnext

                seg = Segment(z)
                self.segments.append(seg)
                i.pprev.s1 = i.s0 = seg

                seg = Segment(z)
                self.segments.append(seg)
                i.pnext.s0 = i.s1 = seg

                # Check for new circle events after new arc has been added
                self.check_circle_event(i, p.x)
                self.check_circle_event(i.pprev, p.x)
                self.check_circle_event(i.pnext, p.x)

                return
            i = i.pnext

        # If there's no intersection, append the new arc
        i = self.arc
        while i.pnext:
            i = i.pnext
        i.pnext = Arc(p, i)

        # Insert new segment between p and i
        x = self.x0
        y = (i.pnext.focus.y + i.focus.y) / 2.0
        start = Point(x, y)

        seg = Segment(start)
        i.s1 = i.pnext.s0 = seg
        self.segments.append(seg)


    def check_circle_event(self, i, x0):
        """
        Checks if there is a circle event.

        Parameters
        ----------
        i : Arc
            The arc that is being checked for a circle event
        x0 : Float
            The x-coordinate of the current sweep line position
        """
        if (i.circle_event != None) and (i.circle_event.x != self.x0):
            i.circle_event.valid = False
        i.circle_event = None

        if (i.pprev is None) or (i.pnext is None): return

        flag, o, x = self.circle(i.pprev.focus, i.focus, i.pnext.focus)
        if flag and (x > self.x0):
            i.circle_event = CircleEvent(x, o, i)
            self.circle_events.push(i.circle_event)

    def circle(self, a, b, c):
        """
        Checks if there is a circle that passes through the points a, b, and c which are the foci of three parabolas.

        Parameters
        ----------
        a, b, c : Point
                  The focus of each parabola.
        Returns
        -------
        (bool, Point, Point)
            - True, the center of the circle, and the rightmost point of the circle if such circle exists.
            - False, None, and None otherwise.
        """

        cross_product = (b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)
        # Check the cross product of ab and ac. If it's positive (left turn), there's no circle
        if (cross_product) > 0: return False, None, None

        # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
        # x and y components for the vector ab
        A = b.x - a.x
        B = b.y - a.y

        # x and y components for the vector ac
        C = c.x - a.x
        D = c.y - a.y

        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*cross_product

        # Points are colinear, so there's no circle
        if (G == 0):
            return False, None, None

        # Point o is the circumcenter of the points a, b, c
        ox = 1.0 * (D*E - B*F) / G
        oy = 1.0 * (A*F - C*E) / G
        o = Point(ox, oy)

        # Calculating the rightmost point of the circumcircle
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
           
        return True, o, x
        
    def intersect(self, p, i):
        """
        Check if a new site p intersects the arc represented by i.

        Parameters
        ----------
        p : Point
            The new site being inserted.
        i : Arc
            The arc on the beachline to check for intersection.

        Returns
        -------
        (bool, Point)
            - True and the intersection point if an intersection exists.
            - False and None otherwise.
        """

        if (i is None): return False, None
        if (i.focus.x == p.x): return False, None

        lower_boundary = None
        upper_boundary = None

        # Compute the lower boundary using the previous arc, if it exists
        if i.pprev is not None:
            lower_boundary = self.intersection(i.pprev.focus, i.focus, p.x).y

        # Compute the upper boundary using the next arc, if it exists
        if i.pnext is not None:
            upper_boundary = self.intersection(i.focus, i.pnext.focus, p.x).y

        # Check if the point p lies within the vertical range of the arc
        if ((i.pprev is None or lower_boundary <= p.y) and
            (i.pnext is None or p.y <= upper_boundary)):
            
            # Calculate the intersection point
            py = p.y
            px = ((i.focus.x ** 2) + (i.focus.y - py) ** 2 - p.x ** 2) / (2 * i.focus.x - 2 * p.x)
            intersection_point = Point(px, py)
            
            return True, intersection_point

        # If no intersection, return False
        return False, None

    def intersection(self, p0, p1, l):
        """
        Gets the intersection between two parabola below the sweep line

        Parameter
        ----------
        p0 : Point
            Focus of the first parabola
        p1 : Point
            Focus of the second parabola
        l : Point
            Position of the vertical sweeplinee
            
        Returns
        -------
        res: the point of intersection between the two parabola
        """

        p = p0
        
        if (p0.x == p1.x): # If the foci are the same
            py = (p0.y + p1.y) / 2.0
        # If one of the foci lie on the sweep line
        elif (p1.x == l):
            py = p1.y 
        elif (p0.x == l):
            py = p0.y
            p = p1
        else: # Otherwise, the intersection can be found with the quadratic formula
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

    def get_segments(self) -> List[Tuple[float, float, float, float]]:
        return [(o.start.x, o.start.y, o.end.x, o.end.y) if o.end else 
                (o.start.x, o.start.y, o.start.x, o.start.y) 
                for o in self.segments if o.start]

    def find_largest_empty_circle(self) -> List[Tuple[float, float, float]]:
        """
        Finds the largest empty circle from the voronoi vertices
        Returns
        -------
        largest_circles: List[Tuple[float, float, float]]
                        A list of the largest empty circles that goes through 3 points in the Voronoi Diagram
        """
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
