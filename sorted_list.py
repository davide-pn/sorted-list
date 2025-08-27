import bisect as _bisect
import itertools as _itertools
from operator import index as _index
from sys import maxsize as _maxsize


class SortedList(list):
    """
    A list that maintains its items in ascending order.

    Items are expected to be comparable in a consistent way.  The ordering is
    stable and newly inserted items follow existing ones. Only `<` comparison
    is used between items, matching the built-in `sort` behavior.

    Many standard list operations are available, but some have been disabled
    due to their incompatibility with the semantics of a sorted list.

    Example
    -------
    >>> sl = SortedList([5, 1, 3])
    >>> sl
    SortedList([1, 3, 5])
    >>> sl.append(4)
    >>> sl
    SortedList([1, 3, 4, 5])

    Performance notes
    -----------------
    Binary search is used where applicable to improve performance. Note that
    insertion and deletion still require shifting, as with the built-in list.
    """

    def __init__(self, items=()):
        list.__init__(self, items)
        list.sort(self)
    
    def __getitem__(self, index):
        if not isinstance(index, slice):
            return list.__getitem__(self, index)
        result = list.__new__(SortedList)
        result.extend(_itertools.islice(self, *index.indices(len(self))))
        return result
    
    def __contains__(self, item):
        index = _bisect.bisect_left(self, item)
        for other in map(self.__getitem__, range(index, len(self))):
            if item == other:
                return True
            if item < other:
                return False
        return False
    
    __setitem__ = None
    
    def __add__(self, other):
        if not isinstance(other, list):
            return NotImplemented
        result = list.__new__(SortedList)
        list.extend(result, _itertools.chain(self, other))
        n = len(result) - len(self)
        if n == 1:
            item = result.pop()
            index = _bisect.bisect(result, item)
            list.insert(result, index, item)
            return result
        if n:
            list.sort(result)
        return result
    
    def __iadd__(self, items):
        n = len(self)
        list.__iadd__(self, items)
        n -= len(self)
        if n != -1:
            if n:
                list.sort(self)
            return
        item = self.pop()
        index = _bisect.bisect(self, item)
        list.insert(self, index, item)
    
    def __mul__(self, n):
        result = list.__new__(SortedList)
        list.extend(result, _itertools.chain.from_iterable(_itertools.repeat(item, n) for item in self))
        return result
    
    __rmul__ = __mul__
    
    def __imul__(self, n):
        data = list.copy(self)
        list.__init__(self, _itertools.chain.from_iterable(_itertools.repeat(item, n) for item in data))
    
    def index(self, item, start=0, stop=_maxsize):
        stop = min(len(self), _index(stop))
        index = _bisect.bisect_left(self, item, start, stop)
        for index in range(index, stop):
            other = self[index]
            if item == other:
                return index
            if item < other:
                break
        raise ValueError
    
    def count(self, item):
        result = 0
        index = _bisect.bisect_left(self, item)
        for other in map(self.__getitem__, range(index, len(self))):
            if item == other:
                result += 1
            if item < other:
                return result
        return result
    
    def copy(self):
        result = list.__new__(SortedList)
        list.extend(result, self)
        return result
    
    insert = reverse = sort = None
    
    def append(self, item):
        index = _bisect.bisect(self, item)
        list.insert(self, index, item)
    
    def extend(self, items):
        n = len(self)
        list.extend(self, items)
        n -= len(self)
        if n != -1:
            if n:
                list.sort(self)
            return
        item = self.pop()
        index = _bisect.bisect(self, item)
        list.insert(self, index, item)
    
    def remove(self, item):
        index = _bisect.bisect_left(self, item)
        for index in range(index, len(self)):
            other = self[index]
            if item == other:
                del self[index]
                return
            if item < other:
                break
        raise ValueError

