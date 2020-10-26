class Latest:
  def __init__(self):
    module = __import__('foo')
    func = getattr(module, 'bar')
    func()