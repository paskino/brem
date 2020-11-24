
import dvc_x as drx

a=drx.DVCRem(private_key="/home/drFaustroll/.ssh/id_routers")

a.login(passphrase=True)
a.generate_keys()
a.autorize_keys('mykey-rsa.pub')
a.logout()

