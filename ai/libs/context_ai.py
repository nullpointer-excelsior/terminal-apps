
__context__ = dict()

def get_context_ai_value(key):
    return __context__.get(key)

def set_context_ai_value(key, value):
    __context__[key] = value