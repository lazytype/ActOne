import sys
from functools import partial


_magic_methods = ' '.join([
    'getitem',
    'divmod neg pos abs invert',
    'call',
])

_numerics = 'add sub mul div floordiv mod lshift rshift and xor or pow'
_inplace = ' '.join('i%s' % n for n in _numerics.split())
_right = ' '.join('r%s' % n for n in _numerics.split())

if sys.version_info[0] == 3:
    _extra = ''
else:
    _extra = 'truediv rtruediv '

_comparisons = set(
   '__%s__' % method for method in 'lt le gt ge eq ne'.split(' ')
)

_non_defaults = set('__%s__' % method for method in [
    'cmp', 'getslice', 'get', 'set', 'delete',
    'missing', 'reduce', 'reduce_ex', 'getinitargs',
    'getnewargs', 'getstate', 'setstate', 'getformat',
    'setformat'
])

_magics = set(
    '__%s__' % method for method in
    ' '.join([
        _magic_methods, _numerics, _inplace, _right, _extra
    ]).split()
)

_unsupported_magics = set([
    '__getattr__', '__setattr__',
    '__init__', '__new__', '__prepare__'
    '__instancecheck__', '__subclasscheck__',
    '__del__'
])

_all_magics = _magics | _comparisons | _non_defaults

def _get_magics(cls):
    def closure(magic):
        def method(self, *args, **kwargs):
            return _A(self, magic, True, args, kwargs, True)
        return method

    return dict((magic, closure(magic)) for magic in _all_magics)

def _act(a, obj):
    stack = []
    while True:
        _getattr = partial(object.__getattribute__, a)
        a, attr, call, args, kwargs, magic = map(
            _getattr, ('a', 'attr', 'call', 'args', 'kwargs', 'magic')
        )

        if a is None:
            for attr, call, args, kwargs, magic in reversed(stack):
                try:
                    obj = getattr(obj, attr)
                except AttributeError as e:
                    if attr in _comparisons and magic:
                        def closure(obj, attr):
                            def comparison(other):
                                return getattr(0.0, attr)(-obj.__cmp__(other))
                            return comparison
                        obj = closure(obj, attr)
                    else:
                        raise e

                if call:
                    obj = obj(*args, **kwargs)

            return obj
                    
        stack.append((attr, call, args, kwargs, magic))

def act(*args, **kwargs):
    if not kwargs and len(args) == 1:
        return partial(_act, args[0])

    if args:        
        return _act(*args, **kwargs)

    return partial(_act, **kwargs)


class _Meta(type):

    def __new__(self, name, bases, attrs):
        attrs.update(_get_magics(self))
        return type.__new__(self, name, bases, attrs)


class _A(object):
    __metaclass__ = _Meta

    def __init__(self, a=None, attr=None, call=None, args=None, kwargs=None, magic=False):
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'attr', attr)
        object.__setattr__(self, 'call', call)
        object.__setattr__(self, 'args', args)
        object.__setattr__(self, 'kwargs', kwargs)
        object.__setattr__(self, 'magic', magic)

    def __getattribute__(self, attr, *args, **kwargs):
        return _A(self, attr, False, args, kwargs)


A = _A()

