
import paramiko as ssh

from getpass import getpass


class DVCRem:
    """ Main class of a dvcrem"""
    __version__ = "0.0.1"  #

    def __init__(self,logfile=None, port=None, host=None,username=None,\
        private_key=None):
        self.logfile = "ssh.log"

        self.port = port
        self.host = host
        self.username = username
        self.private_key = private_key
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

    def login_pw(self):
        print('trying to login to {h} on port {p} with username {u} please provide password: '.format(h=self.host,p=self.port,u=self.username))
        pw = getpass()
        self.client = ssh.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        self.client.connect(self.host, self.port, self.username, password=pw)
        self.channel = self.client.invoke_shell()

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

    def put_file(self,filename):
        # check file exists TBD
        self.sftp.put(filename, filename)

    def get_file(self,filename):
        self.sftp.get(filename, filename)

    def remove_file(self,filename):
        self.sftp.remove(filename)

    def listdir(self,path='./'):
        data_dir = self.sftp.listdir(path=path)
        data = self.sftp.listdir_attr(path=path)
        cd = self.sftp.getcwd()
        return cd, data_dir,data

    def changedir(self,dirname):
        self.sftp.chdir(dirname)


    def authorize_key(self,filename):
        ff='randomfiletoauthorize.sh'
        self.put_file(filename)
        with open(ff,'w') as f:
            print('''
                    if [[ $(grep -c "$(cat mykey-rsa.pub)" ~/.ssh/authorized_keys) == 0 ]]; then
                        cat {f} >> .ssh/authorized_keys
                    else
                       echo "key already present"
                    fi
                    '''.format(f=filename),file=f)
        self.put_file(ff)
        self.run("/bin/sh ./{}".format(ff))
        self.remove_file(ff)
        self.remove_file(filename)

    def submit_job(self,jdir,job,nodes=1,tps=32,name="mytest",cons="amd",time="00:20:00"):

        ff="submit.slurm"
        self.changedir(jdir)
        with open(ff,'w') as f:
            print('''#!/usr/bin/env bash
#SBATCH --nodes={nodes}
#SBATCH --tasks-per-node={tps}
#SBATCH --job-name="{name}"
#SBATCH -C [{cons}]
#SBATCH -t {time}

{job}
            '''.format(nodes=nodes, tps=tps,cons=cons,name=name,time=time,job=job),file=f)
        self.put_file(ff)
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



def main():
    """ Run the main program """
    t=DVCRem()
    print(t.info())

if __name__ == "__main__":
    main()
