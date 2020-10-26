import logging
import os

from holm.download import Download
from holm.helpers import file_sha1
from pyunpack import Archive

from holm.json_request import JsonRequest
from holm.keys import Keys


class Left:
  type = None

  def __init__(self, type):
    self.type = type

  def update(self):
    keys = Keys()

    # check if there is already one of this type cached -> if not download 7z and extract it
    left_path = "data/left/" + self.type + ".txt"
    if not os.path.exists(left_path):
      logging.log(logging.DEBUG, "Left does not exist, downloading...")
      self.download_left()
      self.update()

    # if file is there, get checksum
    checksum = file_sha1(left_path)

    # check if the file checksum is valid
    req = JsonRequest()
    res = req.execute("https://hashes.org/api/holm.php?action=checkLeft&checksum=" + checksum)
    if 'status' not in res or res['status'] != 'success':
      logging.log(logging.ERROR, "Failed to check checksum of left file " + self.type)
      os.remove("data/left/" + self.type + ".txt")
      return

    # load which key was retrieved latest and get left update time
    keys_time = keys.get_newest_time()
    left_time = res['time']

    # if latest key is newer than left list -> get diff from key   else -> get diff from left
    req = JsonRequest()
    if left_time > keys_time or keys.get_newest_key() is None:
      res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromLeftEst&checksum=" + checksum)
    else:
      res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromKeyEst&key=" + keys.get_newest_key())
    if not 'estimate' in res.keys():
      logging.log(logging.ERROR, "Failed to estimate keys to download!")
      return

    logging.log(logging.INFO, "Estimated to download: " + str(res['estimate']['keys']) + " keys with " + str(res['estimate']['entries']) + " entries ")
    logging.log(logging.DEBUG, "Retrieve keys to download...")

    # retrieve list of keys
    req = JsonRequest()
    if left_time > keys_time or keys.get_newest_key() is None:
      res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromLeft&checksum=" + checksum)
    else:
      res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromKey&key=" + keys.get_newest_key())
    if not 'keys' in res.keys():
      logging.log(logging.ERROR, "Failed get keys to download!")
      return

    # download remaining keys
    keys.retrieve_keys(res['keys'])

    # TODO: build new left list

  def download_left(self):
    Download.download("https://hashes.org/download.php?leftId=true&type=" + self.type, "data/left/" + self.type + ".7z")
    Archive("data/left/" + self.type + ".7z").extractall("data/left")
    os.remove("data/left/" + self.type + ".7z")
