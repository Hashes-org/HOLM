import argparse
import logging
import os
import sys

import psutil as psutil
import requests

from holm.config import Config
from holm.file_build import FileBuild
from holm.helpers import file_get_contents
from holm.initialize import Initialize
from holm.left import Left
from holm.session import Session
from holm.setting import Setting


def init_logging():
  log_format = '[%(asctime)s] [%(levelname)-5s] %(message)s'
  print_format = '%(message)s'
  date_format = '%Y-%m-%d %H:%M:%S'
  log_level = logging.INFO
  logfile = open('holm.log', "a", encoding="utf-8")

  logging.getLogger("requests").setLevel(logging.WARNING)

  if config.get_value('debug'):
    log_level = logging.DEBUG
    logging.getLogger("requests").setLevel(logging.DEBUG)
  logging.basicConfig(level=log_level, format=print_format, datefmt=date_format)
  file_handler = logging.StreamHandler(logfile)
  file_handler.setFormatter(logging.Formatter(log_format))
  logging.getLogger().addHandler(file_handler)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='HOLM Client v' + Initialize.get_version_number(), prog='python3 holm.zip')

  parser.add_argument('--version', '-v', action='store_true', help='show version information')
  parser.add_argument('--setting', '-s', type=str, required=True, help='set settings file to configure actions')
  parser.add_argument('--reset', action='store_true', help='reset completely (deletes all cached information)')
  parser.add_argument('--clear', action='store_true', help='clears all key files which are cached (but no lists and lefts)')

  parser.add_argument('--daemon', '-d', action='store_true', help='run in daemon mode')
  args = parser.parse_args()

  if args.version:
    print(Initialize.get_version_number())
    sys.exit(0)

  try:
    config = Config()
    init_logging()

    session = Session(requests.Session()).s
    session.headers.update({'User-Agent': 'HOLM v' + Initialize.get_version_number(), 'referer': 'https://hashes.org'})

    # check if there is a lock file and check if this pid is still running
    if os.path.exists("lock.pid") and os.path.isfile("lock.pid"):
      pid = file_get_contents("lock.pid")
      logging.info("Found existing lock.pid, checking if python process is running...")
      if psutil.pid_exists(int(pid)):
        try:
          command = psutil.Process(int(pid)).cmdline()[0].replace('\\', '/').split('/')
          print(command)
          if str.startswith(command[-1], "python"):
            logging.fatal("There is already a holm instance running in this directory!")
            sys.exit(-1)
        except Exception:
          pass
      logging.info("Ignoring lock.pid file because PID is not existent anymore or not running python!")

    # create lock file
    with open("lock.pid", 'w') as f:
      f.write(str(os.getpid()))
      f.close()

    Initialize.create_dirs()

    pass  # TODO: here we can start with whatever we want to do

    # this part is testing
    setting = Setting(args.setting)
    lefts = setting.get_left()
    for left in lefts:
      l = Left(left)
      l.update(left + ".txt")

  except KeyboardInterrupt:
    logging.info("Exiting...")
    # if lock file exists, remove
    if os.path.exists("lock.pid"):
      os.unlink("lock.pid")
    sys.exit()
