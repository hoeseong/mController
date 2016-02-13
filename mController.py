'''
Created on Feb 12, 2016

@author: hoeseong
'''

import os
import time
import hashlib
import multiprocessing
import threading
import mQueue
import mConst
import mLogger

  
class mController:
  def __init__(self, data_dict):
    self.path = data_dict['path']
    self.rootpath = os.path.expanduser(self.path)
    self.dir_list = data_dict['dir_list']
    self.file_list = data_dict['file_list']
    self.link_list = data_dict['link_list']
    self.other_list = data_dict['other_list']
    self.error_list = data_dict['error_list']
    self.file_stat_dict = data_dict['file_stat_dict']
    self.file_stat_count = multiprocessing.Value('L', 0)

    self.m_lock = multiprocessing.Lock()
    self.logger = data_dict['logger']
        
    self.file_queue = mQueue.mQueue()
    self.dir_queue = mQueue.mQueue()
    self.link_queue = mQueue.mQueue()
    self.other_queue = mQueue.mQueue()
    self.error_queue = mQueue.mQueue()
    
    self.mController_queue_dict = {'file_queue':self.file_queue,
                                   'dir_queue':self.dir_queue,
                                   'link_queue':self.link_queue,
                                   'other_queue':self.other_queue,
                                   'error_queue':self.error_queue
                                   }

    self.CONST = mConst._Const()
    self.max_controller = self.CONST.MAX_CONTROLLER_PROCESS
    self.max_worker = self.CONST.MAX_WORKER_PROCESS
    self.max_threads = self.CONST.MAX_TASK_THREAD
    self.max_retrials = self.CONST.MAX_ERROR_COUNT_DEFAULT
    self.sleep_time = self.CONST.SLEEP_TIME_DEFAULT
    
    self.begin_time = time.time()
    self.time_end = self.begin_time
    

  def hashfileSHA256(self, filename, blocksize=2*1024*1024):
    #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "called:[" + filename + "]")
  
    try:
      f = open(filename, 'rb')
      buf = [1]
      shasum = hashlib.sha256()
      while len(buf)>0:
        buf = f.read(blocksize)
        shasum.update(buf)
    except Exception, e:
      self.logger.error(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "can't be hashed with SHA256:[" + filename + "]", e)
      return "oops"
  
    # hashlib.sha256('foo').hexdigest()
    #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "finished:[" + filename +"]")
    return str(shasum.hexdigest())
        
  def get_File_Stat(self, filename, hashmode=False):
    self.m_lock.acquire()
    self.file_stat_count.value += 1
    self.m_lock.release()
    
    self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "called(" + str(self.file_stat_count.value) + "/" + str(len(self.file_queue.mQueue_list)) + "):[" + filename + "]")
  
    filepath = os.path.join(self.rootpath, filename)
    try:
      path, f = os.path.split(filepath)
      realpath=os.path.realpath(filepath)
      relpath=os.path.relpath(self.rootpath, filepath)
      mode = os.stat(filepath).st_mode
      dev = os.stat(filepath).st_dev
      hardlink = os.stat(filepath).st_nlink
      uid = os.stat(filepath).st_uid
      gid = os.stat(filepath).st_gid
      size = os.stat(filepath).st_size
      atime = os.stat(filepath).st_atime
      mtime = os.stat(filepath).st_mtime
      ctime = os.stat(filepath).st_ctime
      backup = "backup"
  
      #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "acquired stat of file:[" + filepath + "]")
    except Exception, e:
      self.logger.error(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "ailed to acquire stat of file:[" + filepath + "]", e)
      return False
  
    if hashmode==True:
      sha256 = self.hashfileSHA256(filepath)
    else:
      sha256 = '-'
  
    try:
      item_dict={ 'f':relpath,
                  'r':realpath,
                  'm':mode,
                  'd':dev,
                  'h':hardlink,
                  'u':uid,
                  'g':gid,
                  's':size,
                  'a':atime,
                  't':mtime,
                  'c':ctime,
                  'h':sha256,
                  'b':backup
                  }
      #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "add file stats:[" + filepath + "]")
    except Exception, e:
      item_dict={}
      self.logger.error(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "failed to add file stats:[" + filepath + "]", e)
  
    self.file_stat_dict[filename] = item_dict
    self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "SHA256:["+ self.file_stat_dict[filename].get('h') + "]:" + filename)
    return
    
  def inject_Queues_From_a_Directory(self, dirname):
    #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "called:[" + dirname + "]")
    
    if os.path.exists(dirname):
      if os.path.isdir(dirname)==True:
        #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "path:[" + dirname + "] is a directory")
        pass
      else:
        #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "path:[" + dirname + "] isn't a directory")
        raise Exception("IOError", "path:[" + self.path + "] isn't directory")
    else:
      #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), " path:[" + dirname + "] isn't existed on the filesystem")
      raise Exception("IOError", "path:[" + dirname + "] isn't existed on the filesystem")

    # the 'dirname' is confirmed as a directory.
    # It will be walked into the sub directories.
    try:
      for f in os.listdir(dirname):
        filepath = os.path.join(dirname, f)
        relpath = os.path.relpath(filepath, self.rootpath)
        # FILE?
        if os.path.isfile(filepath)==True:
          self.file_queue.put(relpath)
          #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "found and added to file_list:[" + relpath + "], file_queue.size=" + str(self.file_queue.mQueue_size.value))
        # SYMBOLIC LINK?
        elif os.path.islink(filepath)==True:
          self.link_queue.put(relpath)
          #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "found and added to link_list:[" + relpath + "], link_queue.size=" + str(self.link_queue.mQueue_size.value))
        # DIRECTORY?
        elif os.path.isdir(filepath)==True:
          self.dir_queue.put(relpath)
          #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "found and added to dir_list:[" + relpath + "], dir_queue.size=" + str(self.dir_queue.mQueue_size.value))
        # OTHER?
        else:
          self.other_queue.put(relpath)
          #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "found and added to other_list:[" + relpath + "], other_queue.size=" + str(self.other_queue.mQueue_size.value))
    except Exception, e:
      self.error_queue.put(relpath)
      #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "can't list the files in the directory:[" + self.path + "], error_queue.size=" + str(self.error_queue.mQueue_size.value, e))
      raise Exception("IOError", "path:[" + self.path + "] can't be listed with the files")
    
    #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "finished in [" + dirname + "]")

  def task(self):
    #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "called")
    
    while not self.dir_queue.empty():
      dirpath = os.path.join(self.rootpath, self.dir_queue.get())
      self.inject_Queues_From_a_Directory(dirpath)
    
    while not self.file_queue.empty():
      filepath = os.path.join(self.rootpath, self.file_queue.get())
      self.get_File_Stat(filepath)
    
    #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "finished")
    return True
  
  def worker(self):
    #self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "called")
    
    task_list = []
    while not self.dir_queue.empty():
      if threading.active_count() <= self.CONST.MAX_TASK_THREAD:
        t = threading.Thread(target=self.task, args=())
        task_list.append(t)
        t.start()
      else:
        self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "waiting for " + str(self.CONST.SLEEP_TIME_WORKER) + " seconds to start new task thread.")
        time.sleep(self.CONST.SLEEP_TIME_TASK)
      
    for job in task_list:
      job.join()
      self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "waiting for children threads being completed: " + str(job.name))
    
    return True

  def start(self):
    self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "called")
    
    self.inject_Queues_From_a_Directory(self.rootpath)
    
    worker_list = []
    while not self.dir_queue.empty():
      if len(multiprocessing.active_children()) <= self.CONST.MAX_WORKER_PROCESS:
        p = multiprocessing.Process(target=self.worker, args=())
        worker_list.append(p)
        p.start()
      else:
        self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "waiting for " + str(self.CONST.SLEEP_TIME_WORKER) + " seconds to start new worker process.")
        time.sleep(self.CONST.SLEEP_TIME_WORKER)
      
    for job in worker_list:
      job.join()
      self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "waiting for children processes being completed: cpid=[" + str(job.pid) + "]")
    
    self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), " finished with " 
              + str(len(self.dir_list)) + " directories, " 
              + str(len(self.file_list)) + " files, "
              + str(len(self.link_list)) + " links, "
              + str(len(self.other_list)) + " others, "
              + str(len(self.error_list)) + " errors"
              + str(len(self.file_stat_dict.keys())) + "filestat keys"
              )
    
    
    self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "finished:" + str(time.time() - self.begin_time) + " seconds were elapsed..")
    
    return True
    
  
          
  def unit_test(self):
    self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "called")
    
    self.inject_Queues_From_a_Directory(self.rootpath)
    
    for filename in self.file_queue.mQueue_list:
      self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "filename:[" + filename + "]")
    
    for dirname in self.dir_queue.mQueue_list:
      self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "dirname:[" + dirname + "]")
          
    for link in self.link_queue.mQueue_list:
      self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "link:[" + link + "]")   
       
    for other in self.other_queue.mQueue_list:
      self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "other:[" + other + "]")
          
    for error in self.error_queue.mQueue_list:
      self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "error:[" + error + "]")
    
    self.logger.debug(str(time.time() - self.begin_time) + ": " +__name__ + "." + mLogger.func_name(), "finished")
    return True
    
    
    
    
    
    
