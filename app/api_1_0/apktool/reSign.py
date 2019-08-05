__author__ = 'zhr'

import os
import os.path


def reSigner(oldapk, newapk, keystore="guding.keystore", keypass="Guding@123!"):
    cmd_sign = r'jarsigner -digestalg SHA1 -sigalg MD5withRSA -verbose -keystore %s -storepass %s -signedjar %s %s ' \
               r'guding' % (keystore, keypass, newapk, oldapk)

    os.system(cmd_sign)


# print "please input the unsigned apk name, keystore name, keypass num"
# unsignapkname = raw_input("input the unsigned apk name:")
# keystorename = raw_input("input the keystore name:")
# keypassnum = raw_input("input the keypass num:")
#
# signedapkname = "sign" + unsignapkname
# reSigner(unsignapkname, signedapkname, keystorename, keypassnum)