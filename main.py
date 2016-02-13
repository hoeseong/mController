'''
Created on Feb 12, 2016

@author: hoeseong
'''

import time
import mController
import mLogger

# ==== main():begin =====
if __name__ == '__main__':

  # record the begin time
  begin_time = time.time()
  
  # declare 'logger' class to send a message to a log file
  logger = mLogger.mLogger()
  logger.debug(str(time.time() - begin_time) + ": " +__name__ + "." + mLogger.func_name(), "started...")
  
  source_dirname = "~/"
  target_dirname = "~/Downloads-copy"
  # declare 
  source_data_dict = {'dir_list':[],
                      'file_list':[],
                      'link_list':[],
                      'other_list':[],
                      'error_list':[],
                      'file_stat_dict':{},
                      'path':source_dirname,
                      'logger':logger
                      }
  
  filestat_controller = mController.mController(source_data_dict)
  filestat_controller.start()
  
  logger.debug(str(time.time() - begin_time) + ": " +__name__ + "." + mLogger.func_name(), " finished with " 
              + str(len(source_data_dict['dir_list'])) + " directories, " 
              + str(len(source_data_dict['file_list'])) + " files, "
              + str(len(source_data_dict['link_list'])) + " links, "
              + str(len(source_data_dict['other_list'])) + " others, "
              + str(len(source_data_dict['error_list'])) + " errors"
              + str(len(source_data_dict['file_stat_dict'].keys())) + "filestat keys"
              )
  
  logger.debug(str(time.time() - begin_time) + ": " +__name__ + "." + mLogger.func_name(), "finished, " + str(time.time() - begin_time) + " seconds...")
# ==== main():end =====
