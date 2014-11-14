__all__ = ["InitLogging", \
           "VLOG", \
           "DEBUG", \
           "INFO", \
           "WARNING", \
           "ERROR", \
           "CRITICAL"]

import time
import sys
import logging

DEFAULT_LOGGER_NAME = "Log"
DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4

""" InitLogging should only be invoked on main thread, aka before the http handler, 
and we only use one true logger whose name is set by "DEFAULT_LOGGER_NAME", wherever
need a log you just call VLOG(), the only logger is global scoped """
def InitLogging(opts):
  g_level = logging.DEBUG
  if '--verbose' in sys.argv:
    g_level = logging.DEBUG
  if '--silent' in sys.argv:
    g_level = logging.NOTSET
  logger = logging.getLogger(DEFAULT_LOGGER_NAME)
  logger.setLevel(g_level)
  g_start_time = time.asctime()
  g_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  if opts.log_path:
    try:
      log_file = open(opts.log_path, "w")
    except:
      print "Failed to redirect stderr to log file"
      return False
    sys.stderr = log_file
    # create a handler to write the log to a given file
    fh = logging.FileHandler(log_path)
    fh.setLevel(g_level)
    fh.setFormatter(g_formatter)
    logger.addHandler(fh)
    print "file in log"
  ch = logging.StreamHandler(sys.__stdout__)
  ch.setLevel(g_level)
  ch.setFormatter(g_formatter)
  logger.addHandler(ch)
  return True

def VLOG(level, msg):
  logger = logging.getLogger(DEFAULT_LOGGER_NAME)
  print "\n"
  if level == DEBUG:
    logger.debug(msg)
  elif level == INFO:
    logger.info(msg)
  elif level == WARNING: 
    logger.warning(msg)
  elif level == ERROR: 
    logger.error(msg)
  elif level == CRITICAL: 
    logger.critical(msg)
  else:
    logger.debug(msg)
  return

