import heapq
import itertools

class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Event:
    def __init__(self, x=0.0, p=None, a=None):
        self.x = x
        self.p = p
        self.a = a
        self.valid = True

class Arc:
    def __init__(self, p=None, a=None, b=None):
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
        self.s0 = None
        self.s1 = None

class Segment:
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
        self.counter = itertools.count()

    def push(self, item):
        if item in self.entry_finder:
            return
        count = next(self.counter)
        entry = [item.x, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)

    def remove_entry(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = 'Removed'

    def pop(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                self.push(item)
                return item
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.pq
