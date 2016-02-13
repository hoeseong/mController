'''
Created on Feb 12, 2016

@author: hoeseong
'''
import multiprocessing

class mQueue:
  def __init__(self):
    self.manager = multiprocessing.Manager()
    self.mQueue_list = self.manager.list()
    self.mQueue_size = multiprocessing.Value('L', 0)
    self.mQueue_index = multiprocessing.Value('L', 0)
    self.mQueue_lock = multiprocessing.Lock()
  
  def put(self, object):
    self.mQueue_lock.acquire()   
    self.mQueue_list.append(object)
    self.mQueue_size.value += 1
    self.mQueue_lock.release()
    
    return self.mQueue_size.value
  
  def get(self):
    self.mQueue_lock.acquire()
    if self.mQueue_size.value > 0:
      result = self.mQueue_list[int(self.mQueue_index.value)]
      self.mQueue_index.value += 1
      self.mQueue_size.value -= 1
    else:
      result = False
    self.mQueue_lock.release()  
    
    return result  
  
  def empty(self):
    self.mQueue_lock.acquire()
    if self.mQueue_size.value > 0:
      result = False
    else:
      result = True
    self.mQueue_lock.release()  
    
    return result  

  def index(self, q_list_index):
    self.mQueue_lock.acquire()
    result = self.mQueue_list[int(q_list_index)]
    self.mQueue_index.value += 1
    self.mQueue_lock.release() 
    
    return result
  
  def lock_acquire(self):
    self.mQueue_lock.acquire()
  
  def lock_release(self):
    self.mQueue_lock.release()
