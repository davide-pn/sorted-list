import bisect as _bisect
import itertools as _itertools
from operator import index as _index
from sys import maxsize as _maxsize
from collections.abc import Iterator as _Iterator, Sized as _Sized


class SortedList(list):
    """
    A list that maintains its items in ascending order.
    
    All stored items must be mutually comparable; if this requirement is not met,
    the behavior is undefined. Most operations rely solely on the `<` comparison,
    mirroring the behavior of the built-in `sort`.

    The full range of standard list operations is supported, save for the
    `insert`, `sort` and `reverse` methods, which have been intentionally
    disabled due to their incompatibility with the semantics of a sorted list.

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
    Binary search is employed where applicable to improve performance. Note that
    insertion and deletion still requires shifting, as with the built-in list.
    """

    def __init__(self, items=None):
        if items:
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
        return index != len(self) and not item < self[index]
    
    def __setitem__(self, index, item):
        if isinstance(index, slice):
            if isinstance(item, _Iterator) or not isinstance(item, _Sized):
                item = [*item]
            list.__setitem__(self, index, item)
            n = len(item)
            if n != 1:
                if n:
                    list.sort(self)
                return
            [item] = item
            n = len(self)
            index = index.indices(n)[0]
        else:
            index = _index(index)
            list.__setitem__(self, index, item)
            n = len(self)
            index %= n
        if index and item < self[index - 1]:
            del self[index]
            index = _bisect.bisect_right(self, item, 0, index)
            list.insert(self, index, item)
        elif index + 1 != n and self[index + 1] < item:
            del self[index]
            index = _bisect.bisect_left(self, item, index, n - 1)
            list.insert(self, index, item)
    
    def __add__(self, other):
        if not isinstance(other, list):
            return NotImplemented
        result = list.__new__(SortedList)
        list.extend(result, self)
        list.extend(result, other)
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
        index = _bisect.bisect_left(self, item, start, min(len(self), _index(stop)))
        if index == len(self) or item < self[index]:
            raise ValueError
        return index
    
    def count(self, item):
        index = _bisect.bisect_left(self, item)
        if index == len(self) or item < self[index]:
            return 0
        return _bisect.bisect_right(self, item) - index
    
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
        if index == len(self) or item < self[index]:
            raise ValueError
        del self[index]
