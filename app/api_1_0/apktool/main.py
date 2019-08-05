_author_="rongrong"

import reSign
import modRes
import os
import datetime


"""
'''反编译apk'''
#def apktookapk():
foldername = r"test"
tmpnum = 1
for apkname in os.listdir(foldername):
    print(apkname)
    apkpath = 'test/' + apkname
    template = 'template/dexpack' + str(tmpnum)
    cmd_apktool = "apktool d -s -f " + apkpath + " -o " + template
    os.system(cmd_apktool)
    tmpnum +=1 
"""

starttime = datetime.datetime.now()
#def pcworkflow(Number,nameStr):
foldername = r"template"
Number = '2'
for filename in os.listdir(foldername):
    dexpack = 'dexpack'
    if filename == dexpack + Number:
     apkname = Number + "rongrong.apk"
     apkpath = 'test/' + apkname
     print(filename)
     filepath = 'template/' + filename
     
     '''修改apk名称'''
     nameStr = '你好哇~'
     modRes.modifyRes(nameStr,filepath)

     '''重打包apk'''
     cmd_packapk = "apktool b -f " + filepath
     os.system(cmd_packapk)

     '''重签名apk'''
     newapkpath = filepath + "/dist/" + apkname
     apk_unsign_path = apkpath + "unsign.apk"
     cmd_cpnewapk = "cp " + newapkpath + " " +  apk_unsign_path
     os.system(cmd_cpnewapk)
     apk_sign_path = apkpath + "sign.apk"
     reSign.reSigner(apk_unsign_path, apk_sign_path)
     
     ''' 删除中间文件'''
     cmd_remove_unsignapk = "rm -f " + apk_unsign_path
     os.system(cmd_remove_unsignapk)
endtime = datetime.datetime.now()
print (endtime - starttime) 

