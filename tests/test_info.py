
import dvc_x as drx

#a=drx.DVCRem(private_key="/home/drFaustroll/.ssh/id_routers")

a=drx.DVCRem(host="scarf.rl.ac.uk",username="scarf562",port=22,private_key="/home/drFaustroll/.ssh/dvc")

a.login(passphrase=False)

#a.generate_keys()
#a.authorize_key('mykey-rsa.pub')
#a.changedir('.')
#print(a.listdir())

jobid = a.submit_job("/home/vol02/scarf562/playground/dvc")

print(jobid)

status = a.job_status(jobid)
print(status)
info = a.job_info(jobid)
print(info)
ss = a.job_cancel(jobid)
print(ss)


a.logout()


