import json


class Setting:
  data = {}

  def __init__(self, path):
    self.data = json.load(open(path))

  def get_left(self):
    if 'left' in self.data.keys():
      return self.data['left']
    return None
