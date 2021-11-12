from brem import AsyncCopyOverSSH
import os
from PySide2 import QtCore
from eqt.threading import Worker
import pysnooper
import brem
from brem.brem import BasicRemoteExecutionManager

from time import sleep
import posixpath

class RemoteAsyncCopyFromSSHSignals(QtCore.QObject):
    status = QtCore.Signal(tuple)
    job_id = QtCore.Signal(int)
class AsyncCopyFromSSH(object):
    def __init__(self, parent=None):

        self.internalsignals = RemoteAsyncCopyFromSSHSignals()
        self.threadpool = QtCore.QThreadPool()
        self.logfile = 'AsyncCopyFromSSH.log'
        self._worker = None
        
    def SetRemoteFileName(self, dirname, filename):
        self.remotefile = filename
        self.remotedir = dirname
    def SetDestinationDir(self, dirname):
        self.localdir = dirname

    @property
    def signals(self):
        return self.worker.signals

    @property
    def worker(self):
        if self._worker is None:
            print("creating worker")
            username = self.connection_details['username']
            port = self.connection_details['port']
            host = self.connection_details['host']
            private_key = self.connection_details['private_key']
            localdir = self.localdir

            self._worker = Worker(self.copy_worker, 
                                  remotedir=self.remotedir, 
                                  remotefile = self.remotefile,
                                  host=host, 
                                  username=username, 
                                  port=port, 
                                  private_key=private_key, 
                                  logfile=self.logfile, 
                                  update_delay=10, 
                                  localdir=localdir)
        return self._worker

    def setRemoteConnectionSettings(self, username=None, 
                                    port= None, host=None, private_key=None, localdir=None):
        self.connection_details = {'username': username, 
                                   'port': port,
                                   'host': host, 
                                   'private_key': private_key,
                                   'localdir': localdir}
    def copy_worker(self, **kwargs):
        # retrieve the appropriate parameters from the kwargs
        host         = kwargs.get('host', None)
        username     = kwargs.get('username', None)
        port         = kwargs.get('port', None)
        private_key  = kwargs.get('private_key', None)
        logfile      = kwargs.get('logfile', None)
        update_delay = kwargs.get('update_delay', None)
        remotefile   = kwargs.get('remotefile', None)
        remotedir    = kwargs.get('remotedir', None)
        localdir     = kwargs.get('localdir', None)
        # get the callbacks
        message_callback  = kwargs.get('message_callback', None)
        progress_callback = kwargs.get('progress_callback', None)
        status_callback   = kwargs.get('status_callback', None)
        for k,v in kwargs.items():
            print (k,v)

        if remotefile is not None:

            
            
            
            a=BasicRemoteExecutionManager(host=host,username=username,port=22,private_key=private_key)

            a.login(passphrase=False)
            
            # if message_callback is not None:
            #     message_callback.emit("{}".format(tail.decode('utf-8')))
            # set the progress to 100
            if progress_callback is not None:
                progress_callback.emit(0)

            a.changedir(remotedir)
            cwd = os.getcwd()
            os.chdir(localdir)
            print("get file", remotefile)
            a.get_file("{}".format(remotefile))
            print("done")
            
            a.logout()
            os.chdir(cwd)
            
            if progress_callback is not None:
                progress_callback.emit(100)
            
        
    def GetFile(self):
        self.threadpool.start(self.worker)

if __name__ == '__main__':

    print ("Hallo???")
    asyncCopy = AsyncCopyFromSSH()
    
    username = 'edo'
    port = 22
    host = 'vishighmem01.esc.rl.ac.uk'
    private_key = "C:/Users/ofn77899/.ssh/id_rsa"
    
    asyncCopy.setRemoteConnectionSettings(username=username, 
                                port=port, host=host, private_key=private_key)
    asyncCopy.SetRemoteFileName(dirname='/home/edo', filename='head.mha')
    asyncCopy.SetDestinationDir(os.path.abspath('.'))
    asyncCopy.GetFile()

    # need to keep the interpreter alive until the thread has finished
    from time import sleep
    for i in range(100):
        tc = asyncCopy.threadpool.activeThreadCount()
        if tc == 0:
            break
        # print (tc)
        sleep(1)