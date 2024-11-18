import math
from typing import List, Tuple
from voronoi.datatypes import Point, CircleEvent, Arc, Segment, PriorityQueue
from voronoi.event_handler import SiteEventHandler, CircleEventHandler

class Voronoi:
    def __init__(self, points):
        self.segments = []
        self.arc = None
        self.site_events = PriorityQueue()
        self.circle_events = PriorityQueue()
        self.original_points = [] 
        self.voronoi_vertices = []

        self.x0, self.x1 = -50.0, -50.0
        self.y0, self.y1 = 600.0, 600.0

        # Insert points into site event PQ
        for x,y in points:
            point = Point(x, y)
            self.site_events.push(point)
            self.original_points.append(point)
            self.x0, self.y0 = min(self.x0, x), min(self.y0, y)
            self.x1, self.y1 = max(self.x1, x), max(self.y1, y)
        
        # Create handlers
        self.site_handler = SiteEventHandler(self)
        self.circle_handler = CircleEventHandler(self)
        
    def process(self):
        """Processing all the points to create the voronoi diagram."""
        while not self.site_events.empty():
            if self.circle_events.empty() or self.circle_events.top().x > self.site_events.top().x:
                self.site_handler.handle(self.site_events.pop())
            else:
                self.circle_handler.handle(self.circle_events.pop())
    
        while not self.circle_events.empty():
            self.circle_handler.handle(self.circle_events.pop())
        
        self.finish_edges()

    def finish_edges(self):
        large_boundary = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)

        current_arc = self.arc
        while current_arc is not None and current_arc.pnext is not None:
            if current_arc.s1 is not None:
                intersection_point = current_arc.intersection(current_arc.pnext, large_boundary * 2.0)
                current_arc.s1.finish(intersection_point)
            current_arc = current_arc.pnext

    def get_segments(self) -> List[Tuple[float, float, float, float]]:
        return [(o.start.x, o.start.y, o.end.x, o.end.y) if o.end else 
                (o.start.x, o.start.y, o.start.x, o.start.y) 
                for o in self.segments if o.start]

    def find_largest_empty_circle(self) -> List[Tuple[float, float, float]]:
        max_radius = 0
        largest_circles = []

        for vertex in self.voronoi_vertices:
            ox, oy = vertex.x, vertex.y
            radius = self.distance_to_closest_site(vertex)
            
            is_empty = True
            # Checks if there are any points from the voronoi vertex that lies within the radius of the circle
            for p in self.original_points:
                if vertex.distance(p) < radius:
                    is_empty = False
                    break
            if is_empty and radius > max_radius:
                max_radius = radius
                largest_circles = [(ox, oy, radius)]
            elif is_empty and radius == max_radius:
                largest_circles.append((ox, oy, radius))

        return largest_circles

    def distance_to_closest_site(self, o):
        return min([o.distance(p) for p in self.original_points])
