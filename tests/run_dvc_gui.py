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
            if self.run_control.job_id is not None:

                dialogue = DVCSLURMProgressDialog(    parent=self,
                                        title="Run Remote Monitor", 
                                        connection_details=self.connection_details, 
                                        job_ids = [self.run_control.job_id]
                                        )
                dialogue.Ok.clicked.connect(dialogue.close)
            
                dialogue.exec()
            else:
                pass

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
            # self.run_control.create_job()
            self.run_control.signals.status.connect(self.updateStatusBar)
            self.run_control.signals.finished.connect(self.processFinished)
            self.run_control.run_job()
        else:
            print ("No connection details")

    def cancel_job(self, job_id):
        pass
    

    def updateStatusBar(self, status):
        if isinstance(status, str):
            msg = status
        elif isinstance(status, tuple):
            msg = "Job {}: {}".format(*status)
            if status[1] in ['PENDING', 'RUNNING', 'FINISHED']:
                self.job_id = status[0]
        else:
            msg = 'Some update, type status {}'.format(type(status))
        self.statusBar().showMessage(msg)

    def processFinished(self):
        msg = ( self.run_control.job_id, "FINISHED" )
        self.updateStatusBar(msg)

class DVCSLURMProgressDialog(QtWidgets.QDialog):
    def __init__(self, parent, title, connection_details, job_ids):
        QtWidgets.QDialog.__init__(self, parent)

        self._job_ids = None
        self.job_ids = job_ids
        self.parent_app = parent

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
        # let's use this button to connect to a running job
        bb.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(
            lambda: self.monitor_job()
        )
        # bb.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(
        #     lambda: self.run_job()
        # )
        
        bb.button(QtWidgets.QDialogButtonBox.Apply).setText("Monitor Job")
        
        
        # select logfile
        # input files
        # requires 3 different 
        # self.addWidget()

        # add widgets
        # jobidl = QtWidgets.QLabel(parent=self)
        # jobidl.setText("Job id: ")
        
        # combo box to select the job id
        formWidget = UIFormFactory.getQWidget(parent=self)
        combo = QtWidgets.QComboBox(formWidget.groupBox)
        for job in self.job_ids:
            combo.addItem(str(job))
        formWidget.addWidget(combo,'Job id:', 'job_selector')

        status = QtWidgets.QLabel(formWidget.groupBox)
        formWidget.addWidget(status, 'Status:', 'status')

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
        # vert_layout.addWidget(jobidl)
        vert_layout.addWidget(formWidget)
        vert_layout.addWidget(prog_bar)
        vert_layout.addWidget(cat)
        # finally 
        # add the button box to the vertical layout, but outside the
        # form layout
        vert_layout.addWidget(bb)
        self.setLayout(vert_layout)


        # save references 
        self.widgets = {'layout': vert_layout, 
                        'buttonBox': bb, 'textEdit': cat, 
                        # 'jobid': jobidl, 
                        'progressBar': prog_bar, 'formWidget': formWidget, 'job_selector': combo}

        
        self.connection_details = connection_details
        
        # store a reference
        # self.threadpool = QtCore.QThreadPool()
        # # create a RemoteRunControl
        # self.runner = RemoteRunControl()
        # self.runner.connection_details = connection_details
        # folder=dpath.abspath("/work3/cse/dvc/test-edo")
        # logfile = dpath.join(folder, "remotedvc.out")
        # self.runner.dvclog_fname = logfile

    @property
    def job_ids(self):
        return self._job_ids
    @job_ids.setter
    def job_ids(self, value):
        self._job_ids = list(value)
    
    def monitor_job(self):
        print ("should know which job this is! {}".format(self.job_ids))
        jobid = self.widgets['job_selector'].currentText()
        run_control = self.parent_app.run_control
        run_control.signals.message.connect(self.appendText)
        run_control.signals.progress.connect(self.update_progress)
        run_control.signals.finished.connect(lambda: self.reset_interface() )
        run_control.signals.status.connect(self.update_status)
        # run_control.internalsignals.cancelled(self.on_cancelled)
        

    @property
    def Ok(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Ok)
    
    @property
    def Apply(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Apply)

    @property
    def Abort(self):
        return self.widgets['buttonBox'].button(QtWidgets.QDialogButtonBox.Abort)

    def reset_interface(self):
        self.Apply.setEnabled(True)
        # check if the job had been cancelled
        run_control = self.parent_app.run_control
        selected_job = self.widgets['job_selector'].currentText()
        status = run_control.jobs[selected_job]
        self.widgets['formWidget'].widgets['status_field'].setText(status)

    def cancel_job(self):
        print ("Should cancel running job")
        # self.statusBar().showMessage("Canceling job")
        selected_job = self.widgets['job_selector'].currentText()
        run_control = self.parent_app.run_control
        run_control.cancel_job(selected_job)
        # self.statusBar().showMessage("Job cancelled")
        self.widgets['progressBar'].setValue(0)
    
    def appendText(self, txt):
        print ("DVCSLURMProgressDialog appendText")
        self.widgets['textEdit'].append(txt)

    def update_progress(self, value):
        print ("DVCSLURMProgressDialog update_progress")
        self.widgets['progressBar'].setValue(value)

    def update_status(self, update):
        print ("DVCSLURMProgressDialog update_status")
        self.widgets['formWidget'].widgets['status_field'].setText(update[1])
        # self.statusBar().showMessage("Job {}: {}".format(*update))
        if update[1] == b'PENDING':
            self.widgets['progressBar'].setMaximum(0)
            self.widgets['progressBar'].setMinimum(0)
            self.widgets['progressBar'].setValue(0)
        else:
            self.widgets['progressBar'].setMaximum(100)
        
    def on_cancelled(self):
        #self.
        jobid = self.widgets['job_selector'].currentText()

    
    

    
import functools

class RemoteRunControlSignals(QtCore.QObject):
    status = QtCore.Signal(tuple)
    job_id = QtCore.Signal(int)

class RemoteRunControl(object):
    def __init__(self, parent=None, connection_details=None, 
                 reference_filename=None, correlate_filename=None,
                 dvclog_filename=None,
                 dev_config=None):
        self.connection_details = connection_details
        self.reference_fname    = reference_filename
        self.correlate_fname    = correlate_filename
        self.dvclog_fname       = dvclog_filename
        self.conn                = None
        self._jobid              = None
        self._job_status         = None
        self.jobs                = {}
        
        self.internalsignals = RemoteRunControlSignals()
        self.internalsignals.job_id.connect(self.set_job_id)
        self.internalsignals.status.connect(self.set_job_status)
        
        self.threadpool = QtCore.QThreadPool()
        self.dvcWorker = None
    
    def set_job_id(self, value):
        self.job_id = value
        self.jobs[value] = None
        # attach finished signal
        # self.dvcWorker.signals.finished.connect(lambda: self.job_finished())
    def set_job_status(self, value):
        self.job_status = value[1]
        self.jobs[value[0]] = value[1]

    def create_job(self):
        if not self.check_configuration():
            raise ValueError('Connection details are not specified or complete. Got', \
                        self.connection_details)
        username = self.connection_details['username']
        port = self.connection_details['server_port']
        host = self.connection_details['server_name']
        private_key = self.connection_details['private_key']
        self.dvcWorker = Worker(self.run_dvc_worker, 
                host=host, username=username, port=port, 
                private_key=private_key, logfile=self.dvclog_fname, 
                update_delay=10)
        
        # other signal/slots should be connected from outside
    
    @property
    def signals(self):
        if self.dvcWorker is not None:
            return self.dvcWorker.signals
        else:
            # try to create a worker
            self.create_job()
            return self.dvcWorker.signals

    def run_job(self):
        self.threadpool.start(self.dvcWorker)
        
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
    def reference_fname(self):
        return self._reference_fname
    @reference_fname.setter
    def reference_fname(self, value):
        '''setter for reference file name.'''
        self._reference_fname = value
        
    @property
    def correlate_fname(self):
        return self._correlate_fname
    @correlate_fname.setter
    def correlate_fname(self, value):
        '''setter for correlate file name.'''
        self._correlate_fname = value
        
    @property
    def dvclog_fname(self):
        return self._dvclog_fname
    @dvclog_fname.setter
    def dvclog_fname(self, value):
        '''setter for dvclog file name.'''
        self._dvclog_fname = value
        
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
            self.internalsignals.status.emit((jobid, status.decode('utf-8')))
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
        self.internalsignals.status.emit((jobid, 'FINISHED'))
        

    def cancel_job(self, job_id):
        host = self.connection_details['server_name']
        username = self.connection_details['username']
        port = self.connection_details['server_port']
        private_key = self.connection_details['private_key']

        a=drx.DVCRem(host=host,username=username,port=22,private_key=private_key)
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
