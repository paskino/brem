import paramiko as ssh
import posixpath, ntpath, os
from getpass import getpass
from PySide2 import QtCore
from eqt.threading import Worker
from brem.version import version as brem_version

remotepath = os.path

class BasicRemoteExecutionManager(object):
    """ Main class of a brem"""
    

    def __init__(self,logfile=None, port=None, host=None,username=None,\
        private_key=None, remote_os=None):
        self.logfile = "ssh.log"

        self.port = port
        self.host = host
        self.username = username
        self.private_key = private_key
        self.remote_os = remote_os

        self.__version__ = brem_version

        if private_key is not None:
            self.private_key = private_key
        if logfile is not None:
            self.logfile = logfile
        if port is not None:
            self.port = port
        if host is not None:
            self.host = host
        if username is not None:
            self.username = username

        global remotepath
        remotepath = posixpath
        if remote_os is not None:
            if remote_os == 'Windows':
                remotepath = ntpath

        ssh.util.log_to_file(self.logfile)
        self.identity = None
        self.channel = None
        self.client = None
        self.sftp =  None

    def login(self,passphrase=False):

        ps=None
        if passphrase:
            print("""trying to login to {h} on port {p} with username {u}
                    with the following key {k}
                    please provide passphrase""".format(h=self.host,p=self.port,u=self.username,k=self.private_key))
            ps = getpass()

        self.identity = ssh.RSAKey.from_private_key_file(self.private_key,password=ps)
        self.client = ssh.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        self.client.connect(self.host, self.port, self.username, pkey=self.identity)
        self.channel = self.client.invoke_shell()
        self.sftp = ssh.SFTPClient.from_transport(self.client.get_transport())

    def login_pw(self, pw=None):
        if pw is None:
            print('trying to login to {h} on port {p} with username {u} please provide password: '.format(h=self.host,p=self.port,u=self.username))
            pw = getpass()
        self.client = ssh.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        self.client.connect(self.host, self.port, self.username, password=pw)
        self.channel = self.client.invoke_shell()
        self.sftp = ssh.SFTPClient.from_transport(self.client.get_transport())

    def logout(self):
        self.sftp.close()
        self.channel.close()
        self.client.close()

    def run(self,command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read(), stderr.read()


    def generate_keys(self,filename=None,bits=4096,passphrase=False):
        phrase=None
        if passphrase:
            phrase =  getpass()
        if filename is None:
            filename = 'mykey-rsa'

        private_key = ssh.RSAKey.generate(bits=bits, progress_func=None)
        private_key.write_private_key_file(filename, password=phrase)

        pub = ssh.RSAKey(filename=filename, password=phrase)
        with open("{}.pub".format(filename), "w") as f:
            print("{name} {key}".format(name=pub.get_name(), key=pub.get_base64()), file=f)

    def info(self):
        return " version {}".format(self.__version__)

    def put_file(self,filename, remote_filename=None):
        # check file exists TBD
        if remote_filename is None:
            remote_filename = remotepath.abspath(
                remotepath.join(self.remote_home_dir,os.path.basename(filename)))
        self.sftp.put(filename, remote_filename)

    @property
    def remote_home_dir(self):
        if self.client is not None:
            stdout, stderr = self.run( "python -c \"import os; print (os.path.expanduser('~'))\"")
            print ("remote_home_dir", stdout)
            return stdout.decode('utf-8').rstrip()
        else:
            raise ValueError('Please provide login first')
    @property
    def local_home_dir(self):

        return os.path.expanduser("~")

    def get_file(self,filename, localdir=None):
        if localdir is None:
            self.sftp.get(filename, filename)
        else:
            self.sftp.get(filename, os.path.join(os.path.abspath(localdir), filename))

    def remove_file(self,filename):
        self.sftp.remove(filename)

    def listdir(self,path='./'):
        data_dir = self.sftp.listdir(path=path)
        data = self.sftp.listdir_attr(path=path)
        cd = self.sftp.getcwd()
        return cd, data_dir,data

    def changedir(self,dirname):
        self.sftp.chdir(dirname)

    def stat(self, path):
        return self.sftp.stat(path)

    def authorize_key(self,filename):
        ff='randomfiletoauthorize.sh'
        remotefile = remotepath.join(self.remote_home_dir, 'mykey-rsa.pub')
        self.put_file(
            os.path.join(os.path.dirname(filename), os.path.basename(filename)+".pub"),
            remotefile
            )

        with open(ff,'w', newline='\n') as f:
            print('''
if [ ! -d ~/.ssh ]; then
    mkdir ~/.ssh
fi
if [ ! -f ~/.ssh/authorized_keys ]; then
    touch .ssh/authorized_keys
fi
if [[ $(grep -c "$(cat mykey-rsa.pub)" ~/.ssh/authorized_keys) == 0 ]]; then
    cat {f} >> .ssh/authorized_keys
else
    echo "key already present"
fi
                    '''.format(f=remotefile), file=f)
        self.put_file(ff)
        self.run("/bin/sh ./{}".format(ff))
        self.remove_file(ff)
        self.remove_file(remotefile)

    def submit_job(self,jdir,job,nodes=1,tps=32,name="mytest",cons="amd",time="00:20:00"):

        ff="submit.slurm"
        self.changedir(jdir)
        with open(ff,'w', newline='\n') as f:
            print('''#!/usr/bin/env bash
#SBATCH --nodes={nodes}
#SBATCH --tasks-per-node={tps}
#SBATCH --job-name="{name}"
#SBATCH -C [{cons}]
#SBATCH -t {time}

{job}
            '''.format(nodes=nodes, tps=tps,cons=cons,name=name,time=time,job=job),file=f)
        self.put_file(ff, remote_filename=remotepath.join(jdir, ff))
        stdout, stderr = self.run("cd {} && sbatch ./{}".format(jdir,ff))
        a=stdout.strip().split()
        if a[0] != "Submitted":
            print(stderr)
        return int(a[3])

    def job_info(self,jid):
        stdout, stderr = self.run("scontrol show jobid -dd  {}".format(jid))
        return stdout

    def job_status(self,jid):
         stdout, stderr = self.run("scontrol show jobid -dd  {} | grep JobState | cut -f 2 -d = | cut -f 1 -d ' '".format(jid))
         return stdout.strip()

    def job_cancel(self,jid):
         stdout, stderr = self.run("scancel  {}".format(jid))
         return stdout

import functools

class RemoteRunControlSignals(QtCore.QObject):
    status = QtCore.Signal(tuple)
    job_id = QtCore.Signal(int)

class RemoteRunControl(object):
    '''RemoteRunControl base class to handle asynchronous interaction with a remote running job

    :param connection_details: required parameters passed in a dictionary server_name, server_port, username, private_key
    :param type: dict 
    '''

    def __init__(self, connection_details=None):
        self.connection_details = connection_details
        self.conn                = None
        self._jobid              = None
        self._job_status         = None
        self.jobs                = {}
        
        self.internalsignals = RemoteRunControlSignals()
        self.internalsignals.job_id.connect(self.set_job_id)
        self.internalsignals.status.connect(self.set_job_status)
        
        self.threadpool = QtCore.QThreadPool()
        self._Worker = None
        
    
    def set_job_id(self, value):
        self.job_id = value
        self.jobs[value] = None
        # attach finished signal
        # self.dvcWorker.signals.finished.connect(lambda: self.job_finished())
    def set_job_status(self, value):
        self.job_status = value[1]
        self.jobs[value[0]] = value[1]
    def get_job_status(self, jobid):
        try:
            return self.jobs[jobid]
        except KeyError as ke:
            return 'Job not found.'

    @property
    def Worker(self):
        return self._Worker
    
    def create_job(self, fn, **kwargs):
        '''Creates a job to run function fn'''
        if not self.check_configuration():
            raise ValueError('Connection details are not specified or complete. Got', \
                        self.connection_details)

        kwargs['username']    = self.connection_details['username']
        kwargs['port']        = self.connection_details['server_port']
        kwargs['host']        = self.connection_details['server_name']
        kwargs['private_key'] = self.connection_details['private_key']
        self._Worker_kwargs = kwargs
        self._Worker = Worker(fn, **kwargs)
                
        
        # other signal/slots should be connected from outside
    
    @property
    def signals(self):
        if self.Worker is not None:
            return self.Worker.signals
        else:
            raise ValueError('Worker function is not defined')
            # return self.Worker.signals
    def run_job(self):
        self.threadpool.start(self.Worker)
        
    @property
    def job_id(self):
        return self._jobid
    @job_id.setter
    def job_id(self, value):
        print ("setting job_id", value)
        self._jobid = value
    @property
    def connection_details(self):
        return self._connection_details
    @connection_details.setter
    def connection_details(self, value):
        if value is not None:
            self._connection_details = dict(value)
        else:
            self._connection_details = None
    @property
    def job_status(self):
        return self._job_status
    @job_status.setter
    def job_status(self, value):
        print("setting job_status", value)
        if self.job_id is not None:
            self._job_status = value
    
    
    def check_configuration(self):
        def f (a,x,y):
            return x in a and y
        ff = functools.partial(f, self.connection_details.keys())
        # return functools.reduce(ff, ['username','server_port', 'server_name','private_key'], True)
        required = ['username','server_port', 'server_name','private_key']
        available = self.connection_details.keys()
        ret = True
        for x in required:
            ret = ret and (x in available)
        return ret

    def cancel_job(self, job_id):
        host = self.connection_details['server_name']
        username = self.connection_details['username']
        port = self.connection_details['server_port']
        private_key = self.connection_details['private_key']

        a = BasicRemoteExecutionManager( host=host, 
                                              username=username,
                                              port=port,
                                              private_key=private_key)
        a.login(passphrase=False)
        self.internalsignals.status.emit((job_id, "CANCELLING"))
        a.job_cancel(job_id)
        self.internalsignals.status.emit((job_id, "CANCELLED"))
        a.logout()
    
    def pytail(self, connection, logfile, start_at):
        
        tail = '''
import os, sys, functools
def pytail(filename, start_at):
    with open(filename, 'r') as f:
        # skip to line start_at
        ret = []
        i = 0
        while True:
            line = f.readline()
            if line == '':
                break
            if i > start_at:
                ret.append(line)
            i += 1
    return ret

if __name__ == '__main__':
    stdout = pytail(sys.argv[1],int(sys.argv[2]))
    msg = functools.reduce(lambda x,y: x+y, stdout, '')
    print (msg)
'''             
        remotehomedir = connection.remote_home_dir

        with open("pytail.py", 'w') as pytail:
            print (tail, file=pytail)
        connection.put_file("pytail.py", remotepath.join(remotehomedir, 'pytail.py'))

        stdout, stderr = connection.run('python pytail.py {} {}'.format(logfile, start_at))
        
        # remove pytail.py from the server.
        # connection.remove_file(dpath.join(connection.remote_home_dir, 'pytail.py'))
        
        # print ("logfile", logfile)
        # print ("stdout", stdout.decode('utf-8'))
        # print ("stdout", stderr)

        # expand tabs and newlines
        return stdout
    

def main():
    """ Run the main program """
    t=BasicRemoteExecutionManager()
    print(t.info())

if __name__ == "__main__":
    main()
