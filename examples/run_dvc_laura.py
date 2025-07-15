import brem

from time import sleep
import os
#a=drx.DVCRem(private_key="/home/drFaustroll/.ssh/id_routers")

a = brem.BasicRemoteExecutionManager(host="scarf.rl.ac.uk",username="scarf978",port=22,private_key="C:/Users/lhe97136/.ssh/id7")

a.login(passphrase=False)

print(os.getcwd())