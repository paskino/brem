from PySide2 import QtCore
from eqt.threading import Worker
import paramiko
from brem import BasicRemoteExecutionManager
import os, ntpath, posixpath
import socket

class RemoteAsyncCopyOverSSHSignals(QtCore.QObject):
    status = QtCore.Signal(tuple)
    job_id = QtCore.Signal(int)
class AsyncCopyOverSSH(object):
    '''Class to handle async copy of files over SSH'''
    def __init__(self, parent=None):

        self.internalsignals = RemoteAsyncCopyOverSSHSignals()
        self.threadpool = QtCore.QThreadPool()
        self.logfile = 'AsyncCopyFromSSH.log'
        self._worker = None
        self.dest_fname = None
        
    def SetRemoteDir(self, dirname):
        self.remotedir = dirname

    def SetFileName(self, filename):
        self.filename = filename
    
    def SetDestinationFileName(self, fname):
        self.dest_fname = fname

    def SetLocalDir(self, dirname):
        self.localdir = dirname

    def SetCopyToRemote(self):
        self.direction = 'to'

    def SetCopyFromRemote(self):
        self.direction = 'from'
    
    def SetRemoteOS(self, value):
        allowed_os = ['Windows', 'POSIX']
        if value in allowed_os:
            self.remote_os = value
        else:
            raise ValueError('Expected value in {}. Got {}'.format(allowed_os, value))

    @property
    def signals(self):
        return self.worker.signals

    @property
    def worker(self):
        if self._worker is None:
            username = self.connection_details['username']
            port = self.connection_details['port']
            host = self.connection_details['host']
            private_key = self.connection_details['private_key']
            localdir = self.localdir
            remote_os = self.connection_details['remote_os']

            self._worker = Worker(self.copy_worker, 
                                  remotedir=self.remotedir, 
                                  filename = self.filename,
                                  localdir=localdir,
                                  direction = self.direction,
                                  host=host, 
                                  username=username, 
                                  port=port, 
                                  private_key=private_key, 
                                  logfile=self.logfile, 
                                  update_delay=10,
                                  remote_os=remote_os
                                  )
        return self._worker

    def setRemoteConnectionSettings(self, username=None, 
                                    port= None, host=None, private_key=None, remote_os=None):
        self.connection_details = {'username': username, 
                                   'port': port,
                                   'host': host, 
                                   'private_key': private_key,
                                   'remote_os': remote_os}
    def copy_worker(self, **kwargs):
        # retrieve the appropriate parameters from the kwargs
        host         = kwargs.get('host', None)
        username     = kwargs.get('username', None)
        port         = kwargs.get('port', None)
        private_key  = kwargs.get('private_key', None)
        logfile      = kwargs.get('logfile', None)
        update_delay = kwargs.get('update_delay', None)
        direction    = kwargs.get('direction', None)
        remote_os    = kwargs.get('remote_os', None)
        filename     = kwargs.get('filename', None)
        remotedir    = kwargs.get('remotedir', None)
        localdir     = kwargs.get('localdir', None)
        
        if direction is not None and filename is not None and remotedir is not None and localdir is not None:
            # get the callbacks
            message_callback  = kwargs.get('message_callback', None)
            progress_callback = kwargs.get('progress_callback', None)
            status_callback   = kwargs.get('status_callback', None)
            
            
            from time import sleep
            
            a = BasicRemoteExecutionManager(host=host,username=username,port=22,private_key=private_key, remote_os=remote_os)

            try:
                a.login(passphrase=False)
            except paramiko.BadHostKeyException as exc:
                print (exc)
                return
            except paramiko.AuthenticationException as exc:
                print (exc)
                return
            except paramiko.SSHException as exc:
                print (exc)
                return
            except socket.error as exc:
                print (exc)
                return
            
            # if message_callback is not None:
            #     message_callback.emit("{}".format(tail.decode('utf-8')))
            # set the progress to 100
            if progress_callback is not None:
                progress_callback.emit(0)
            try:
                a.changedir(remotedir)
            except IOError as exc:
                print (exc)
                return
            cwd = os.getcwd()
            os.chdir(localdir)
            if direction == 'from':
                action = 'get'
                if status_callback is not None:
                    status_callback.emit("{} file {}".format(action, filename))
                a.get_file("{}".format(filename))
            else:
                action = 'put'
                # dest_fname   = kwargs.get('dest_fname', None)
                dest_fname = posixpath.join(self.remotedir, filename)
                if status_callback is not None:
                    status_callback.emit("{} file {}".format(action, filename))
                a.put_file(filename, dest_fname)
            if status_callback is not None:
                    status_callback.emit("done")
            
            a.logout()
            os.chdir(cwd)
            
            if progress_callback is not None:
                progress_callback.emit(100)
        else:
            print ("something wrong")
            
        
    def GetFile(self, filepath, destination_dir):
        self.SetCopyFromRemote()
        self.SetLocalDir(destination_dir)

        if self.connection_details['remote_os'] == 'Windows':
            remotepath = ntpath
        else:
            remotepath = posixpath

        self.SetRemoteDir(remotepath.dirname(filepath))
        self.SetFileName(remotepath.basename(filepath))

        self.threadpool.start(self.worker)


    def PutFile(self, filepath, destination_dir):
        self.SetCopyToRemote()
        filepath = os.path.abspath(filepath)
        self.SetLocalDir(os.path.dirname(filepath))
        self.SetFileName(os.path.basename(filepath))
        
        self.SetRemoteDir(destination_dir)
        
        print ("is worker None", self._worker is None)
        self.threadpool.start(self.worker)


    
    
