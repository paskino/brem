
import dvc_x as drx

#a=drx.DVCRem(private_key="/home/drFaustroll/.ssh/id_routers")

a=drx.DVCRem()

a.login(passphrase=False)

#a.generate_keys()
a.authorize_key('mykey-rsa.pub')
a.logout()

