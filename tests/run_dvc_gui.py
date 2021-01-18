from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import QRegExp
import glob, sys, os
from functools import partial
import posixpath, ntpath
import posixpath as dpath
from dvc_x.ui import RemoteFileDialog
from dvc_x.ui import RemoteServerSettingDialog
import dvc_x as drx
from eqt.threading import Worker
from eqt.ui import FormDialog, UIFormFactory
import pysnooper

class MainUI(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)

        pb = QtWidgets.QPushButton(self)
        pb.setText("Configure Connection")
        pb.clicked.connect(lambda: self.openConfigRemote())
        br = QtWidgets.QPushButton(self)
        br.setText("Browse remote")
        br.clicked.connect(lambda: self.browseRemote())

        rdvc = QtWidgets.QPushButton(self)
        rdvc.setText("Run DVC remotely")
        rdvc.clicked.connect(lambda: self.runRemote())

        rdvc2 = QtWidgets.QPushButton(self)
        rdvc2.setText("Open Run DVC remotely")
        rdvc2.clicked.connect(lambda: self.openRunRemoteDialog())

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(pb)
        layout.addWidget(br)
        layout.addWidget(rdvc)
        layout.addWidget(rdvc2)
        widg = QtWidgets.QWidget()
        widg.setLayout(layout)
        self.setCentralWidget(widg)

        self.threadpool = QtCore.QThreadPool()

        self.show()
    def getSelected(self, dialogue):
        if hasattr(dialogue, 'selected'):
            for el in dialogue.selected:
                print ("Return from dialogue", el)
    def getConnectionDetails(self, dialog):
        for k,v in dialog.connection_details.items():
            print (k,v)
        self.connection_details = dialog.connection_details
    def openConfigRemote(self):

        dialog = RemoteServerSettingDialog(self,port=None,
                                    host=None,
                                    username=None,
                                    private_key=None)
        dialog.Ok.clicked.connect(lambda: self.getConnectionDetails(dialog))
        dialog.exec()
    def browseRemote(self):
        # private_key = os.path.abspath("C:\Apps\cygwin64\home\ofn77899\.ssh\id_rsa")
        # port=22
        # host='ui3.scarf.rl.ac.uk'
        # username='scarf595'
        if hasattr(self, 'connection_details'):
            username = self.connection_details['username']
            port = self.connection_details['server_port']
            host = self.connection_details['server_name']
            private_key = self.connection_details['private_key']

            logfile = os.path.join(os.getcwd(), "RemoteFileDialog.log")
            dialogue = RemoteFileDialog(self,
                                        logfile=logfile,
                                        port=port,
                                        host=host,
                                        username=username,
                                        private_key=private_key)
            dialogue.Ok.clicked.connect(lambda: self.getSelected(dialogue))

            dialogue.exec()
    def openRunRemoteDialog(self):
        if hasattr(self, 'connection_details'):
            username = self.connection_details['username']
            port = self.connection_details['server_port']
            host = self.connection_details['server_name']
            private_key = self.connection_details['private_key']

            logfile = os.path.join(os.getcwd(), "RemoteFileDialog.log")
            # logfile = os.path.abspath("C:/Users/ofn77899/Documents/Projects/CCPi/GitHub/PythonWorkRemote/dvc_x/RemoteFileDialogue.log")
            dialogue = DVCRunDialog(    parent=self,
                                        title="Run Remote Monitor", 
                                        connection_details=self.connection_details
                                        )
            dialogue.Ok.clicked.connect(dialogue.close)
            
            dialogue.exec()
    def runRemote(self):
        if hasattr(self, 'connection_details'):
            username = self.connection_details['username']
            port = self.connection_details['server_port']
            host = self.connection_details['server_name']
            private_key = self.connection_details['private_key']
            folder=dpath.abspath("/work3/cse/dvc/test-edo")
            logfile = dpath.join(folder, "remotedvc_proc.out")
            print ("logfile", logfile)


            # self.dvcWorker = Worker(self.run_dvc_worker, host, username, port, 
            #     private_key, logfile)
            # self.dvcWorker.signals.message.connect(self.updateStatusBar)

            # self.threadpool.start(self.dvcWorker)

            self.run_control = RemoteRunControl(parent=self, connection_details=self.connection_details, 
                                                dvclog_filename=logfile)
            self.run_control.create_job()
            self.run_control.signals.message.connect(self.updateStatusBar)
            self.run_control.run_job()
        else:
            print ("No connection details")

    

    def updateStatusBar(self, status):
        self.statusBar().showMessage(status)

class DVCRunDialog(QtWidgets.QDialog):
    def __init__(self, parent, title, connection_details):
        QtWidgets.QDialog.__init__(self, parent)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
                                     | QtWidgets.QDialogButtonBox.Apply
                                     | QtWidgets.QDialogButtonBox.Abort)

        bb.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(
            lambda : self.accept()
        )

        bb.button(QtWidgets.QDialogButtonBox.Abort).clicked.connect(
            lambda: self.cancel_job()
        )
        bb.button(QtWidgets.QDialogButtonBox.Abort).setText("Cancel Job")
        bb.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(
            lambda: self.run_job()
        )
        bb.button(QtWidgets.QDialogButtonBox.Apply).setText("Submit Job")
        
        
        # select logfile
        # input files
        # requires 3 different 
        # self.addWidget()

        # add widgets
        jobidl = QtWidgets.QLabel(parent=self)
        jobidl.setText("Job id: ")

        # progress bar
        prog_bar = QtWidgets.QProgressBar(parent=self)
        prog_bar.setMinimum(0)
        prog_bar.setMaximum(100)
        
        # add the cat log 
        cat = QtWidgets.QTextEdit(self)
        cat.setReadOnly(True)
        cat.setMinimumHeight(100)
        cat.setMinimumWidth(560)

        vert_layout = QtWidgets.QVBoxLayout(self)
        vert_layout.addWidget(jobidl)
        vert_layout.addWidget(prog_bar)
        vert_layout.addWidget(cat)
        # finally 
        # add the button box to the vertical layout, but outside the
        # form layout
        vert_layout.addWidget(bb)
        self.setLayout(vert_layout)


        # save references 
        self.widgets = {'layout': vert_layout, 
                        'buttonBox': bb, 'textEdit': cat, 'jobid': jobidl, 
                        'progressBar': prog_bar}

        # store a reference
        self.threadpool = QtCore.QThreadPool()

        self.connection_details = connection_details

        # create a RemoteRunControl
        self.runner = RemoteRunControl()
        self.runner.connection_details = connection_details
        folder=dpath.abspath("/work3/cse/dvc/test-edo")
        logfile = dpath.join(folder, "remotedvc.out")
        self.runner.dvclog_fname = logfile

    @property
    def Ok(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Ok)
    
    @property
    def Apply(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Apply)

    @property
    def Abort(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Abort)

    
    
    def run_job(self):
        if hasattr(self, 'connection_details'):
            username = self.connection_details['username']
            port = self.connection_details['server_port']
            host = self.connection_details['server_name']
            private_key = self.connection_details['private_key']
            folder=dpath.abspath("/work3/cse/dvc/test-edo")
            logfile = dpath.join(folder, "remotedvc.out")
            print ("logfile", logfile)
            self.dvcWorker = Worker(self.runner.run_dvc_worker, 
                host=host, username=username, port=port, 
                private_key=private_key, logfile=logfile, update_delay=10)
            # connect signal/slots
            self.dvcWorker.signals.message.connect(self.appendText)
            self.dvcWorker.signals.progress.connect(self.update_progress)
            self.dvcWorker.signals.finished.connect(lambda: self.reset_interface() )
            self.dvcWorker.signals.status.connect(self.update_status)
            

            self.threadpool.start(self.dvcWorker)

            self.Apply.setEnabled(False)
            self.Apply.setText("Queueing")
        else:
            print ("No connection details")
    def reset_interface(self):
        self.Apply.setEnabled(True)
        self.Apply.setText("Submit job")

        # 
        import re
        m = re.search("^Job ([0-9]*)", self.widgets['jobid'].text())
        jid = ''
        if m is not None:
            jid = m.group(0) 
        self.widgets['jobid'].setText('{}: Finished'.format(jid))

    def cancel_job(self):
        print ("Should cancel running job")
        self.widgets['jobid'].setText("Canceling job")
        self.runner.cancel_job()
        self.widgets['jobid'].setText("Job cancelled")
        self.widgets['progressBar'].setValue(0)
    
    def appendText(self, txt):
        self.widgets['textEdit'].append(txt)

    def update_progress(self, value):
        self.widgets['progressBar'].setValue(value)

    def update_status(self, update):
        
        self.widgets['jobid'].setText("Job {}: {}".format(*update))
        if update[1] == b'PENDING':
            self.widgets['progressBar'].setMaximum(0)
        else:
            self.widgets['progressBar'].setMaximum(100)
        
    
    

    
import functools

class RemoteRunControlSignals(QtCore.QObject):
    status = QtCore.Signal(str)
    job_id = QtCore.Signal(int)

class RemoteRunControl(object):
    def __init__(self, parent=None, connection_details=None, 
                 reference_filename=None, correlate_filename=None,
                 dvclog_filename=None,
                 dev_config=None):
        self._connection_details = None
        self._reference_fname    = None
        self._correlate_fname    = None
        self._dvclog_fname       = None
        self.conn                = None
        self._jobid              = None
        self._job_status         = None
        
        self.internalsignals = RemoteRunControlSignals()
        self.internalsignals.job_id.connect(self.job_id)
        self.internalsignals.status.connect(self.job_status)
        
        self.threadpool = QtCore.QThreadPool()
        self.dvcWorker = None
        

    def create_job(self):
        username = self.connection_details['username']
        port = self.connection_details['server_port']
        host = self.connection_details['server_name']
        private_key = self.connection_details['private_key']
        self.dvcWorker = Worker(self.run_dvc_worker, 
                host=host, username=username, port=port, 
                private_key=private_key, logfile=self.dvclog_fname, 
                update_delay=10)
        # signal/slots should be connected from outside
    
    @property
    def signals(self):
        if self.dvcWorker is not None:
            return self.dvcWorker.signals
        return None

    def run_job(self):
        self.threadpool.start(self.dvcWorker)
        
    @property
    def job_id(self):
        return self._jobid
    @property
    def connection_details(self):
        return self._connection_details
    @property
    def reference_fname(self):
        return self._reference_fname
    @property
    def correlate_fname(self):
        return self._correlate_fname
    @property
    def dvclog_fname(self):
        return self._dvclog_fname
    @property
    def job_status(self):
        return self._job_status
    @job_id.setter
    def job_id(self, value):
        print ("setting job_id", value)
        self._jobid = value
    @connection_details.setter
    def connection_details(self, value):
        if value is not None:
            self._connection_details = dict(value)
        else:
            self._connection_details = None
    @reference_fname.setter
    def reference_fname(self, value):
        '''setter for reference file name.'''
        self._reference_fname = value
        if self.check_configuration():
            self.set_up()
    @correlate_fname.setter
    def correlate_fname(self, value):
        '''setter for correlate file name.'''
        self._correlate_fname = value
        if self.check_configuration():
            self.set_up()
    @dvclog_fname.setter
    def dvclog_fname(self, value):
        '''setter for dvclog file name.'''
        self._dvclog_fname = value
        if self.check_configuration():
            self.set_up()
    def check_configuration(self):
        def f (a,x,y):
            return x in a and y
        ff = functools.partial(f, ['username','server_port',
                                   'server_name','private_key'])
        if not functools.reduce(ff, self.connection_details.keys(), True):
            return False
        return True
    @job_status.setter
    def job_status(self, value):
        print("setting job_status", value)
        if self.job_id is not None:
            self._job_status = value
    # @pysnooper.snoop()
    def run_dvc_worker(self, **kwargs):
        # retrieve the appropriate parameters from the kwargs
        host         = kwargs.get('host', None)
        username     = kwargs.get('username', None)
        port         = kwargs.get('port', None)
        private_key  = kwargs.get('private_key', None)
        logfile      = kwargs.get('logfile', None)
        update_delay = kwargs.get('update_delay', None)
        # get the callbacks
        message_callback  = kwargs.get('message_callback', None)
        progress_callback = kwargs.get('progress_callback', None)
        status_callback   = kwargs.get('status_callback', None)
        
        
        from time import sleep
        
        a=drx.DVCRem(host=host,username=username,port=22,private_key=private_key)

        a.login(passphrase=False)

        inp="input.dvc"
        # folder="/work3/cse/dvc/test-edo"
        folder = dpath.dirname(logfile)
        datafolder="/work3/cse/dvc/test_data"

        with open(inp,'w', newline='\n') as f:
            print("""###############################################################################
#
#
#               example dvc process control file
#
#
###############################################################################

# all lines beginning with a # character are ignored
# some parameters are conditionally required, depending on the setting of other parameters
# for example, if subvol_thresh is off, the threshold description parameters are not required

### file names

reference_filename\t{0}/frame_000_f.npy\t### reference tomography image volume
correlate_filename\t{0}/frame_010_f.npy\t### correlation tomography image volume

point_cloud_filename\t{1}/medium_grid.roi\t### file of search point locations
output_filename\t{1}/medium_grid\t### base name for output files

### description of the image data files, all must be the same size and structure

vol_bit_depth           8                       ### 8 or 16
vol_hdr_lngth           96                      ### fixed-length header size, may be zero
vol_wide                1520                    ### width in pixels of each slice
vol_high                1257                    ### height in pixels of each slice
vol_tall                1260                    ### number of slices in the stack

### parameters defining the subvolumes that will be created at each search point

subvol_geom             sphere                  ### cube, sphere
subvol_size             80                      ### side length or diameter, in voxels
subvol_npts             8000                    ### number of points to distribute within the subvol

subvol_thresh           off                     ### on or off, evaluate subvolumes based on threshold
#   gray_thresh_min     27                      ### lower limit of a gray threshold range if subvol_thresh is on
#   gray_thresh_max     127                     ### upper limit of a gray threshold range if subvol_thresh is on
#   min_vol_fract       0.2                     ### only search if subvol fraction is greater than

### required parameters defining the basic the search process

disp_max                38                      ### in voxels, used for range checking and global search limits
num_srch_dof            6                       ### 3, 6, or 12
obj_function            znssd                   ### sad, ssd, zssd, nssd, znssd
interp_type             tricubic                ### trilinear, tricubic

### optional parameters tuning and refining the search process

rigid_trans             34.0 4.0 0.0            ### rigid body offset of target volume, in voxels
basin_radius            0.0                     ### coarse-search resolution, in voxels, 0.0 = none
subvol_aspect           1.0 1.0 1.0             ### subvolume aspect ratio



""".format(datafolder,folder),file=f)

        a.put_file(inp, remote_filename=dpath.join(folder, inp))


        job="""

module purge
module load AMDmodules foss/2019b

/work3/cse/dvc/codes/CCPi-DVC/build-amd/Core/dvc {0} > {1} 2>&1
#{0}
        """.format(inp, logfile)



        jobid = a.submit_job(folder,job)
        self.job_id = jobid
        print(jobid)
        status = a.job_status(jobid)
        print(status)
        i = 0
        start_at = 0
        while status in [b'PENDING',b'RUNNING']:
            i+=1
            # widgets['jobid'].setText("Job id: {} {}".format(jobid, str(status)))
            status_callback.emit((jobid, status.decode('utf-8')))
            if status == b'PENDING':
                print("job is queueing")
                # message_callback.emit("Job {} queueing".format(jobid))
            else:
                print("job is running")
                # widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Apply).setText('Running')
                
                # tails the output of dvc
                tail = self.pytail(a, logfile, start_at)
                # count the number of newlines
                for i in tail:
                    if i == "\n":
                        start_at+=1
                message_callback.emit("{}".format(tail.decode('utf-8')))
                # try to infer the progress
                def progress(line):
                    import re
                    try:
                        match = re.search('^([0-9]*)/([0-9]*)', line.decode('utf-8'))
                        if match is not None:
                            return eval(match.group(0))
                    except Exception as err:
                        print (err)

                line = tail.splitlines()
                if len(line) >= 2:
                    line = line[-2]

                curr_progress = progress(line)
                if curr_progress is not None:
                    # widgets['progressBar'].setValue(int(progress(line)*100))
                    progress_callback.emit(int(progress(line)*100))
                    print ("attempt evaluate progress ", progress(line))
                
            sleep(update_delay)
            status = a.job_status(jobid)
        

        # dvc computation is finished, we get the last part of the output
        tail = self.pytail(a, logfile, start_at)
        message_callback.emit("{}".format(tail.decode('utf-8')))
        # set the progress to 100
        progress_callback.emit(100)

        a.changedir(folder)
        a.get_file("slurm-{}.out".format(jobid))
        a.get_file("dvc.out".format(jobid))
        # here we should fetch also all the output files defined at
        # output_filename\t{1}/small_grid\t### base name for output files

        a.logout()
        

    def cancel_job(self):
        host = self.connection_details['server_name']
        username = self.connection_details['username']
        port = self.connection_details['server_port']
        private_key = self.connection_details['private_key']

        a=drx.DVCRem(host=host,username=username,port=22,private_key=private_key)
        a.login(passphrase=False)
        a.job_cancel(self.job_id)
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
        connection.put_file("pytail.py", dpath.join(remotehomedir, 'pytail.py'))

        stdout, stderr = connection.run('python pytail.py {} {}'.format(logfile, start_at))
        
        # remove pytail.py from the server.
        # connection.remove_file(dpath.join(connection.remote_home_dir, 'pytail.py'))
        
        # print ("logfile", logfile)
        # print ("stdout", stdout.decode('utf-8'))
        # print ("stdout", stderr)

        # expand tabs and newlines
        return stdout
    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainUI()

    sys.exit(app.exec_())
