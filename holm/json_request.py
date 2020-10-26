import logging

from holm.session import *
from requests.sessions import Session

from holm.config import Config


class JsonRequest:
  def __init__(self):
    self.config = Config()
    self.session = Session().s

  def execute(self, url):
    try:
      logging.log(logging.DEBUG, "Requesting: " + url)
      r = self.session.get(url, timeout=30)
      if r.status_code != 200:
        logging.log(logging.ERROR, "Status code from server: " + str(r.status_code))
        return None
      logging.log(logging.DEBUG, r.content)
      return r.json()
    except Exception as e:
      logging.log(logging.ERROR, "Error occurred: " + str(e))
      return None
