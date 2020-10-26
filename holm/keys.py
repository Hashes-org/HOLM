import logging
import os
import time
import urllib.request


class Keys:
  current_newest = None

  def __init__(self):
    self.get_newest_key()

  def retrieve_keys(self, keys):
    logging.log(logging.INFO, "Retrieving " + str(len(keys)) + " keys...")
    count = 1
    for key in keys:
      logging.log(logging.DEBUG, "Loading key " + key + " (" + str(count) + "/" + str(len(keys)) + ")...")
      if os.path.exists("data/keys/" + key + ".txt"):
        logging.log(logging.DEBUG, "Skipping already existing key file!")
      else:
        urllib.request.urlretrieve("https://hashes.org/api/holm.php?action=getKey&key=" + key, "data/keys/" + key + ".txt")
      self.set_newest_key(key)
      count += 1

  def set_newest_key(self, key):
    with open("data/keys/CURRENT", "w") as f:
      f.write(key)
    f.close()
    self.current_newest = key

  def get_newest_key(self):
    if self.current_newest is not None:
      return self.current_newest
    if not os.path.exists("data/keys/CURRENT"):
      return None
    with open("data/keys/CURRENT", "r") as f:
      self.current_newest = f.read().strip()
    if len(self.current_newest) != 32:
      logging.log(logging.WARN, "Keys CURRENT is invalid!")
      self.current_newest = None
    return self.current_newest
