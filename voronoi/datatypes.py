import heapq
import math

class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

class CircleEvent:
    __slots__ = ['x', 'point', 'arc', 'valid']
    
    def __init__(self, x=0.0, point=None, arc=None):
        self.x = x
        self.point = point
        self.arc = arc
        self.valid = True
    
    def __lt__(self, other):
        return self.x < other.x

class Arc:
    __slots__ = ['focus', 'pprev', 'pnext', 'circle_event', 's0', 's1']
    
    def __init__(self, focus=None, a=None, b=None):
        self.focus = focus
        self.pprev = a
        self.pnext = b
        self.circle_event = None
        self.s0 = None
        self.s1 = None

    def intersection(self, other, l: float) -> Point:
        """Get the intersection between this parabola and the given parabola at sweep line l."""
        p0 = self.focus
        p1 = other.focus

        p = p0
        
        if p0.x == p1.x:  # If the foci are the same
            py = (p0.y + p1.y) / 2.0
        # If one of the foci lie on the sweep line
        elif p1.x == l:
            py = p1.y 
        elif p0.x == l:
            py = p0.y
            p = p1
        else:  # Otherwise, use quadratic formula
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)

            a = 1.0/z0 - 1.0/z1
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = 1.0 * (p0.y**2 + p0.x**2 - l**2) / z0 - 1.0 * (p1.y**2 + p1.x**2 - l**2) / z1

            py = 1.0 * (-b-math.sqrt(b*b - 4*a*c)) / (2*a)
            
        px = 1.0 * (p.x**2 + (p.y-py)**2 - l**2) / (2*p.x-2*l)
        return Point(px, py)

class Segment:
    __slots__ = ['start', 'end', 'done']
    
    def __init__(self, p):
        self.start = p
        self.end = None
        self.done = False

    def finish(self, p):
        if not self.done:
            self.end = p
            self.done = True

class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.REMOVED = '<removed-task>'
        self.counter = 0

    def push(self, item):
        if item in self.entry_finder:
            self.remove_entry(item)

        entry = [item.x, self.counter, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)
        self.counter += 1

    def remove_entry(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED

    def pop(self):
        while self.pq:
            _, _, item = heapq.heappop(self.pq)
            if item is not self.REMOVED:
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            _, _, item = self.pq[0]
            if item is not self.REMOVED:
                return item
            heapq.heappop(self.pq)
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.entry_finder