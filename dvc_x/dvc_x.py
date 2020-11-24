
import paramiko as ssh

from getpass import getpass


class DVCRem:
    """ Main class of a dvcrem"""
    __version__ = "0.0.1"  #

    def __init__(self,logfile=None, port=None, host=None,username=None,private_key=None):
        self.logfile = "ssh.log"

        self.port = 22
        self.host = 'scarf.rl.ac.uk'
        self.username = 'scarf562'
        self.private_key = '/home/drFaustroll/.ssh/dvc'
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
        ssh.util.log_to_file("test.log")
        self.identity = None
        self.channel = None
        self.client = None

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

    def login_pw(self):
        print('trying to login to {h} on port {p} with username {u} please provide password: '.format(h=self.host,p=self.port,u=self.username))
        pw = getpass()
        self.client = ssh.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        self.client.connect(self.host, self.port, self.username, password=pw)
        self.channel = self.client.invoke_shell()

    def logout(self):
        self.channel.close()
        self.client.close()

    def run(self,command):
        stdin, stdout, stderr = self.client.exec_command(command)

        print("stdout")
        print(stdout.read())
        print("stderr")
        print(stderr.read())


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
        sftp = ssh.SFTPClient.from_transport(self.client.get_transport())
        sftp.put(filename, filename)
        sftp.close()

    def get_file(self,filename):
        sftp = ssh.SFTPClient.from_transport(self.client.get_transport())
        sftp.get(filename, filename)
        sftp.close()

    def remove_file(self,filename):
        sftp = ssh.SFTPClient.from_transport(self.client.get_transport())
        sftp.remove(filename)
        sftp.close()

    def listdir(self,path='./'):
        sftp = ssh.SFTPClient.from_transport(self.client.get_transport())
        data = sftp.listdir_attr(path=path)
        sftp.close()
        return data

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
#        self.remove_file(ff)
#        self.remove_file(filename)



def main():
    """ Run the main program """
    t=DVCRem()
    print(t.info())

if __name__ == "__main__":
    main()
