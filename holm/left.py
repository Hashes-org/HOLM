import logging
import os

from holm.download import Download
from holm.file_build import FileBuild
from holm.helpers import file_sha1
from pyunpack import Archive

from holm.json_request import JsonRequest
from holm.keys import Keys


class Left:
  type = None

  def __init__(self, type):
    self.type = type

  def update(self, output):
    keys = Keys()

    # check if there is already one of this type cached -> if not download 7z and extract it
    left_path = "data/left/" + self.type + ".txt"
    if not os.path.exists(left_path):
      logging.log(logging.DEBUG, "Left does not exist, downloading...")
      self.download_left()
      self.update(output)

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
    left_time = res['time']

    # if latest key is newer than left list -> get diff from key   else -> get diff from left
    res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromLeftEst&checksum=" + checksum)
    if not 'estimate' in res.keys():
      logging.log(logging.ERROR, "Failed to estimate keys to download from left diff!")
      return
    update_type = "left"
    est = res['estimate']

    if keys.get_newest_key() is not None:
      res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromKeyEst&key=" + keys.get_newest_key())
      if not 'estimate' in res.keys():
        logging.log(logging.ERROR, "Failed to estimate keys to download from key diff!")
        return
      if res['estimate']['keys'] < est['keys']:
        update_type = "key"
        est = res['estimate']

    logging.log(logging.INFO, "Estimated to download: " + str(est['keys']) + " keys with " + str(est['entries']) + " entries ")
    logging.log(logging.DEBUG, "Retrieve keys to download...")

    # retrieve list of keys
    if update_type == 'left':
      res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromLeft&checksum=" + checksum)
    else:
      res = req.execute("https://hashes.org/api/holm.php?action=getDiffFromKey&key=" + keys.get_newest_key())
    if not 'keys' in res.keys():
      logging.log(logging.ERROR, "Failed get keys to download!")
      return

    # download remaining keys
    keys.retrieve_keys(res['keys'])

    fb = FileBuild("data/left/" + self.type + ".txt", res['keys'], output, self.type)
    fb.generate()

  def download_left(self):
    Download.download("https://hashes.org/download.php?leftId=true&type=" + self.type, "data/left/" + self.type + ".7z")
    Archive("data/left/" + self.type + ".7z").extractall("data/left")
    os.remove("data/left/" + self.type + ".7z")
