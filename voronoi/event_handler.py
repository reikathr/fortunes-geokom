from typing import List, Optional, Tuple
from voronoi.datatypes import Point, CircleEvent, Arc, Segment, PriorityQueue
import math

class SiteEventHandler:
    def __init__(self, voronoi_diagram):
        self.voronoi = voronoi_diagram
        self.x0 = voronoi_diagram.x0
        self.segments = voronoi_diagram.segments

    def handle(self, point: Point) -> None:
        """Handle a site event by inserting a new arc into the beachline."""
        if self.voronoi.arc is None:
            self.voronoi.arc = Arc(point)
            return

        self._insert_arc(point)

    def _insert_arc(self, p: Point) -> None:
        """Insert a new arc into the beachline."""
        i = self.voronoi.arc
        while i:
            # Check for intersection with the current arc
            flag, z = self._intersect(p, i, p.x)
            if flag:
                # Handle intersection with i and i.pnext
                if i.pnext and not self._intersect(p, i.pnext, p.x)[0]:
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

                # Check for new circle events
                self.voronoi.circle_handler.check_circle_event(i)
                self.voronoi.circle_handler.check_circle_event(i.pprev)
                self.voronoi.circle_handler.check_circle_event(i.pnext)

                return
            i = i.pnext

        # If there's no intersection, append the new arc
        i = self.voronoi.arc
        while i.pnext:
            i = i.pnext
        i.pnext = Arc(p, i)

        # Insert new segment between point and i
        x = self.x0
        y = (i.pnext.focus.y + i.focus.y) / 2.0
        start = Point(x, y)

        seg = Segment(start)
        i.s1 = i.pnext.s0 = seg
        self.segments.append(seg)

    def _intersect(self, p: Point, arc: Arc, sweep_line_x: float) -> tuple[bool, Optional[Point]]:
        """Check if a new site p intersects with the given arc."""
        if (arc is None) or (arc.focus.x == p.x):
            return False, None

        lower_boundary = None
        upper_boundary = None

        if arc.pprev is not None:
            lower_boundary = arc.pprev.intersection(arc, sweep_line_x).y
        if arc.pnext is not None:
            upper_boundary = arc.intersection(arc.pnext, sweep_line_x).y

        if ((arc.pprev is None or lower_boundary <= p.y) and
            (arc.pnext is None or p.y <= upper_boundary)):
            py = p.y
            px = ((arc.focus.x ** 2) + (arc.focus.y - py) ** 2 - p.x ** 2) / (2 * arc.focus.x - 2 * p.x)
            intersection_point = Point(px, py)
            
            return True, intersection_point

        return False, None

class CircleEventHandler:
    def __init__(self, voronoi_diagram):
        self.voronoi = voronoi_diagram
        self.segments = voronoi_diagram.segments
        self.voronoi_vertices = voronoi_diagram.voronoi_vertices
        self.circle_events = voronoi_diagram.circle_events
        self.x0 = voronoi_diagram.x0

    def handle(self, circle_event: CircleEvent) -> None:
        """Handle a circle event by creating new Voronoi vertex and updating the beachline."""
        if not circle_event.valid:
            return

        # Create a new segment at the circle event point
        segment = Segment(circle_event.point)
        self.segments.append(segment)
        self.voronoi_vertices.append(circle_event.point)

        # Get the arc associated with this circle event
        arc = circle_event.arc
        self._update_neighbors(arc, segment)

        # Finish the edges before and after this arc
        if arc.s0 is not None:
            arc.s0.finish(circle_event.point)
        if arc.s1 is not None:
            arc.s1.finish(circle_event.point)

        # Recheck circle events on either side of the arc
        if arc.pprev:
            self.check_circle_event(arc.pprev)
        if arc.pnext:
            self.check_circle_event(arc.pnext)

    def check_circle_event(self, i: Arc) -> None:
        """Check if there is a circle event for the given arc."""
        if (i.circle_event is not None) and (i.circle_event.x != self.x0):
            i.circle_event.valid = False
        i.circle_event = None

        if (i.pprev is None) or (i.pnext is None):
            return

        flag, o, x = self._circle(i.pprev.focus, i.focus, i.pnext.focus)
        if flag and (x > self.x0):
            i.circle_event = CircleEvent(x, o, i)
            self.circle_events.push(i.circle_event)

    def _circle(self, a: Point, b: Point, c: Point) -> Tuple[bool, Optional[Point], Optional[float]]:
        """Check if there is a circle passing through three points."""
        cross_product = (b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)
        # Check the cross product of ab and ac. If it's positive (left turn), there's no circle
        if (cross_product) > 0:
            return False, None, None

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
        ox = (D*E - B*F) / G
        oy = (A*F - C*E) / G
        o = Point(ox, oy)

        # Rightmost point of circle
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
        return True, o, x

    def _update_neighbors(self, arc: Arc, segment: Segment) -> None:
        """Update the pointers and segment associations for the neighboring arcs."""
        if arc.pprev:
            arc.pprev.pnext = arc.pnext
            arc.pprev.s1 = segment
        if arc.pnext:
            arc.pnext.pprev = arc.pprev
            arc.pnext.s0 = segment