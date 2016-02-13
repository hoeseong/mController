'''
Created on Feb 12, 2016

@author: hoeseong
'''

import os
import traceback
import logging
from objc._convenience import __call__

def func_name():
    return traceback.extract_stack(None, 2)[0][2]

class mLogger:
  def __init__(self, logname="get_file_list"):
    # create logger with 'spam_application'
    self.logger = logging.getLogger(logname)
    self.logger.setLevel(logging.DEBUG)
    
    # create file handler which logs even debug messages
    self.fh = logging.FileHandler(logname + ".log")
    
    # create formatter and add it to the handlers
    self.formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    self.fh.setFormatter(self.formatter)
    
    # add the handlers to the logger
    self.logger.addHandler(self.fh)

  def info(self, function, log_message="INFO"):
    self.logger.info("(pid=%d), %s(): %s", os.getpid(), function, log_message)
    print "(pid=%d), INFO: %s(): %s" % (os.getpid(), function, log_message)

  def warning(self, function, log_message="WARNING"):
    self.logger.warning("(pid=%d), %s(): %s", os.getpid(), function, log_message)
    print "(pid=%d), WARNING: %s" % (os.getpid(), function, log_message)
  
  def error(self, function, log_message="ERROR", error_message="FATAL"):
    self.logger.error("(pid=%d), %s(): %s / %s", os.getpid(), function, log_message, str(error_message))
    print "(pid=%d), ERROR: %s / %s" % (os.getpid(), function, log_message, str(error_message))
  
  def debug(self, function, log_message="DEBUG"):
    self.logger.debug("(pid=%d), %s(): %s", os.getpid(), function, log_message)
    print "(pid=%d), DEBUG: %s(): %s" % (os.getpid(), function, log_message)
