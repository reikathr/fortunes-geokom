import heapq
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

class Event:
    __slots__ = ['x', 'p', 'a', 'valid']
    
    def __init__(self, x=0.0, p=None, a=None):
        self.x = x
        self.p = p
        self.a = a
        self.valid = True
    
    def __lt__(self, other):
        return self.x < other.x

class Arc:
    __slots__ = ['p', 'pprev', 'pnext', 'e', 's0', 's1']
    
    def __init__(self, p=None, a=None, b=None):
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
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