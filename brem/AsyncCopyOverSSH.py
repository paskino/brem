from PySide2 import QtCore
from eqt.threading import Worker
import paramiko
from brem import BasicRemoteExecutionManager
import os, ntpath, posixpath
import socket
from .brem import Windows, POSIX

class RemoteAsyncCopyOverSSHSignals(QtCore.QObject):
    status = QtCore.Signal(tuple)
    job_id = QtCore.Signal(int)
class AsyncCopyOverSSH(object):
    '''Class to handle async copy of files over SSH
    
    :param remote_os: type of the remote os, can be 'POSIX' or 'Windows', default 'POSIX'
    :type remote_os: str
    '''
    def __init__(self, remote_os=POSIX):

        self.remotepath = self.SetRemoteOS(remote_os)

        self.internalsignals = RemoteAsyncCopyOverSSHSignals()
        self.threadpool = QtCore.QThreadPool()
        self.logfile = 'AsyncCopyFromSSH.log'
        self._worker = None
        self._remote_os = None
        self.SetDestinationFileName(None)
        self.SetRemoteOS(remote_os)
        
    def SetRemoteDir(self, dirname):
        '''Set the remote directory name
        
        :param dirname: remote directory name
        :type dirname: str
        '''
        self.remotedir = dirname

    def SetFileName(self, filename):
        '''Set the remote file name
        
        :param file: remote file name
        :type dirname: str
        '''
        self.filename = filename
    
    def SetDestinationFileName(self, fname):
        '''Set the destination name
        
        :param fname: destination file name
        :type fname: path
        '''
        self.dest_fname = fname

    def SetLocalDir(self, dirname):
        '''Set the local directory name
        
        :param dirname: local directory name
        :type dirname: path
        '''
        self.localdir = dirname

    def SetCopyToRemote(self):
        '''Set the behaviour to copy file from local to remote'''
        self.direction = 'to'

    def SetCopyFromRemote(self):
        '''Set the behaviour to copy file from remote to local'''
        self.direction = 'from'
    
    def SetRemoteOS(self, value):
        '''Set the remote OS
        
        :param value: 'Windows' or 'POSIX'
        :type value: str'''
        allowed_os = [Windows, POSIX]
        if value == POSIX:
            self.remotepath = posixpath
        elif value == Windows:
            self.remotepath = ntpath
        else:
            raise ValueError('Expected value in {}. Got {}'.format([POSIX,Windows], value))
        self._remote_os = value

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
                                  update_delay=10
                                  )
        return self._worker

    def setRemoteConnectionSettings(self, username=None, 
                                    port= None, host=None, private_key=None):
        '''Set the connection parameter to configure the BasicRemoteExecutionManager
        
        :param username: user name on the remote
        :type username: str
        :param port: port to connect to
        :type port: int
        :param host: host name or IP
        :type host: str
        :param private_key: filename for the private key for the SSH connection
        :type private_key: str or path
        '''
        self.connection_details = {'username': username, 
                                   'port': port,
                                   'host': host, 
                                   'private_key': private_key,
                                   }
    def copy_worker(self, **kwargs):
        # retrieve the appropriate parameters from the kwargs
        host         = kwargs.get('host', None)
        username     = kwargs.get('username', None)
        port         = kwargs.get('port', None)
        private_key  = kwargs.get('private_key', None)
        logfile      = kwargs.get('logfile', None)
        update_delay = kwargs.get('update_delay', None)
        direction    = kwargs.get('direction', None)
        filename     = kwargs.get('filename', None)
        remotedir    = kwargs.get('remotedir', None)
        localdir     = kwargs.get('localdir', None)
        
        if direction is not None and filename is not None and remotedir is not None and localdir is not None:
            # get the callbacks
            message_callback  = kwargs.get('message_callback', None)
            progress_callback = kwargs.get('progress_callback', None)
            status_callback   = kwargs.get('status_callback', None)
            
            
            from time import sleep
            
            a = BasicRemoteExecutionManager(host=host,username=username,port=22,private_key=private_key, remote_os=self._remote_os)

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
                dest_fname = self.remotepath.join(self.remotedir, filename)
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
        '''Configures and starts an async copy from remote to local
        
        :param filepath: path to the remote file to get
        :type filepath: str or path
        :param destination_dir: local destination directory
        :type destination_dir: str or path'''
        self.SetCopyFromRemote()
        self.SetLocalDir(destination_dir)

        self.SetRemoteDir(self.remotepath.dirname(filepath))
        self.SetFileName(self.remotepath.basename(filepath))

        self.threadpool.start(self.worker)


    def PutFile(self, filepath, destination_dir):
        '''Configures and starts an async copy from local to remote
        
        :param filepath: path to the local file to copy to the remote
        :type filepath: str or path
        :param destination_dir: remote destination directory
        :type destination_dir: str or path'''
        self.SetCopyToRemote()
        filepath = os.path.abspath(filepath)
        self.SetLocalDir(os.path.dirname(filepath))
        self.SetFileName(os.path.basename(filepath))
        
        self.SetRemoteDir(destination_dir)
        
        self.threadpool.start(self.worker)


    
    
