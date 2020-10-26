import os


class Initialize:
  def __init__(self):
    pass

  @staticmethod
  def get_version_number():
    return "0.1.0"

  @staticmethod
  def create_dirs():
    if not os.path.isdir("data"):
      os.mkdir("data")
    if not os.path.isdir("data/left"):
      os.mkdir("data/left")
    if not os.path.isdir("data/keys"):
      os.mkdir("data/keys")
    if not os.path.isdir("data/lists"):
      os.mkdir("data/lists")
