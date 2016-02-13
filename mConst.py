'''
Created on Feb 12, 2016

@author: hoeseong
'''

import multiprocessing

def constant(f):
  def fset(self, value):
    raise TypeError
  def fget(self):
    return f() 
  return property(fget, fset)

class _Const(object):
  @constant
  def MAX_ERROR_COUNT_DEFAULT():
    return 5

  @constant
  def SLEEP_TIME_DEFAULT():
    return 0.05

  @constant
  def SLEEP_TIME_WORKER():
    return 0.05

  @constant
  def SLEEP_TIME_TASK():
    return 0.05

  @constant
  def SLEEP_TIME_JOB():
    return 0.05

  @constant
  def MAX_CONTROLLER_PROCESS():
    return multiprocessing.cpu_count() * 1.5

  @constant
  def MAX_WORKER_PROCESS():
    return multiprocessing.cpu_count() * 3 

  @constant
  def MAX_TASK_THREAD():
    return 32
