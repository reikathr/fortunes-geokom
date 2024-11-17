import heapq

class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

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