# -- coding: utf-8 --
import sys
import os
# import random
# import string
import time

import requests as requests

from .classmodule import *
from .funcmodule import *
import urllib2
import json
import ConfigParser
import getpass
import requests
import shutil


remoteAddress = "47.105.76.115:8000"

def main():
    args = sys.argv[1:]
    # print args
    if args[0] == 'push':
        projectLocation = os.getcwd()

        remoteRepo = RemoteRepoPlatform()
        # get remote ipfs hash
        remoteUrl = remoteRepo.gitRemoteUrl
        remoteHash = remoteRepo.remoteIpfsHash

        username = raw_input("user name: ")
        pwd = getpass.getpass('password: ')
        # verify auth
        if remoteRepo.verifiAuth(username,pwd):
            # gen a key to store remote repo
            pathLocalRemoteRepo = genKey32()
            # download remote repo to local
            print "hit get ipfs repo to local"
            ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteHash,pathLocalRemoteRepo) # 要重命名
            print ipfsGetRepoCmd
            os.system(ipfsGetRepoCmd)
            # push repo to downloaded remote repo
            print "hit push to local"
            # use local repo to deal push command
            gitPushCmd = "git push %s" % (pathLocalRemoteRepo)
            for arg in args[1:]:
                # TODO:
                # if user add a remote url, there should changes it to hit command
                gitPushCmd += " " + arg
            os.system(gitPushCmd)
            # get timestamp (remoteTimeStamp) of the remote repo
            # print "compare local repo with remote repo"
            # remoteTimeStamp = os.popen("ipfs cat %s/timestamp" % remoteFileHash).read()
            # if remoteRepo.timeStamp == remoteTimeStamp:
            os.chdir(pathLocalRemoteRepo)
            # update git repo
            os.system("git update-server-info")

            addResponse = os.popen("ipfs add -rH .").read()
            lastline = addResponse.splitlines()[-1].lower()
            if lastline != "added completely!":
                print lastline
                os.chdir(projectLocation)
                shutil.rmtree("%s" % pathLocalRemoteRepo)
                # os.system("rm -rf %s" % pathLocalRemoteRepo)
                return
            newRepoHash = addResponse.splitlines()[-2].split(" ")[1]

            dataUpdate = {"method":"changeIpfsHash","username":username,"password":pwd,
                                     "reponame":remoteRepo.repoName,"ownername":remoteRepo.userName,
                                     "ipfsHash":newRepoHash}
            dataUpdate = json.dumps(dataUpdate)
            # print dataUpdate
            updateRequest = requests.post(remoteRepo.repoIpfsUrl, data=dataUpdate).json()

            print updateRequest["response"]
            os.chdir(projectLocation)
            shutil.rmtree("%s" % pathLocalRemoteRepo)
            # os.system("rm -rf %s" % pathLocalRemoteRepo)
        else:
            print "ERROR: Access denied to push your code to the repo"



    elif args[0] == "transfer":
        if args[1][0:4] == "http":
            repoNameBare = args[1].split("/")[-1]
            # accessControl = AccessControl()
            rootLocation = os.getcwd()
            os.system("git clone --bare %s" % (args[1]))
            # repoNameBack = genKey32()
            # os.system("git clone %s %s"%(args[1],repoNameBack))
            # os.chdir(repoNameBack)

            username = raw_input("user name: ")
            password = getpass.getpass('password: ')
            newRepoName = raw_input("repository name: ")

            # config = Config()
            # config.initConfig(newRepoName, username)
            # os.system("git add .")
            # os.system("git commit -m 'hit init'")
            # os.system("git push %s" % rootLocation+"/"+repoNameBare)
            # os.chdir(rootLocation)
            # shutil.rmtree("%s/%s" % (rootLocation, repoNameBack))
            # os.system("rm -rf %s/%s" % (rootLocation, repoNameBack))

            os.chdir(repoNameBare)
            os.system("git update-server-info")
            # os.system("echo " + repr(time.time()) + " > timestamp")  # 生成一个时间戳文件

            response = os.popen("ipfs add -rH .").read()
            lastline = response.splitlines()[-1].lower()
            if lastline != "added completely!":
                print lastline
                return
            # newRepoHash = response.splitlines()[-1].split(" ")[1]
            newRepoHash = response.splitlines()[-2].split(" ")[1]
            # os.popen("ipfs key gen --type=rsa --size=2048 %s" % repoName).read()
            # namePublishCmd = "ipfs name publish --key=%s %s" % (repoName, newRepoHash)
            # remoteHash = os.popen(namePublishCmd).read().split(" ")[2][0:-1]

            # connect to the restful webservice
            data = {"method": "hitTransfer", "username": username, "password": password, "reponame": newRepoName, "ipfsHash":newRepoHash}
            data = json.dumps(data)
            # print "update ipfs hash to %s" % remoteAddress
            response = requests.post("http://" + remoteAddress + "/webservice/", data=data)
            response = response.json()
            # if response["response"] != "success":
            #     print response["response"]
            #     return

            print response["response"]

            shutil.rmtree("%s/%s" % (rootLocation, repoNameBare))
            # os.system("rm -rf %s/%s" % (rootLocation, repoNameBare))
        elif len(args) == 1:
            # TODO:
            # this method is not finish
            # we use this to upload a local repo to ipfs netwrok
            repoName = args[1].split("/")[-1]
            # change local repo to a bare repo
            # os.system("git clone --bare %s" % (args[1]))
            projectLocation = os.getcwd()
            os.chdir(repoName)
            os.system("git update-server-info")
            newRepoHash = os.popen("ipfs add -rH .").read().splitlines()[-1].split(" ")[1]
            remoteHash = os.popen("ipfs key gen --type=rsa --size=2048 %s" % repoName).read()
            namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash, newRepoHash)
            os.system(namePublishCmd)
            return

    elif args[0] == "pull":
        remoteRepoPlatform = RemoteRepoPlatform()
        remoteUrl = remoteRepoPlatform.gitRemoteUrl
        remoteIpfsUrl = remoteRepoPlatform.remoteIpfsUrl
        os.system("git remote set-url origin %s" % remoteIpfsUrl)
        cmd = "git"
        for arg in args:
            cmd += " " + arg
        os.system(cmd)
        os.system("git remote set-url origin %s" % remoteUrl)

    elif args[0] == "clone":
        remoteUrl = ""
        for i,arg in enumerate(args):
            if arg[0:26] == "http://47.105.76.115:8000/" or arg[0:19] == "47.105.76.115:8000/":
                remoteUrl = arg
                argsplit = arg.split("/")
                ownername = argsplit[-2]
                reponame = argsplit[-1].split(".")[-2]
                ipfsHashData = json.dumps(
                    {"method": "getIpfsHash", "ownername": ownername, "reponame": reponame})
                response = requests.post("http://47.105.76.115:8000/webservice/", data=ipfsHashData).json()
                if response["response"] == "success":
                    remoteIpfsHash = response["ipfs_hash"]
                    remoteIpfsUrl = "http://localhost:8080/ipfs/" + remoteIpfsHash
                    args[i] = remoteIpfsUrl
                    print "hit clone ipfs hash: " + args[i]
                    if len(args) <= i + 2:
                        args.append(reponame)
                    break
                else:
                    print response["response"]
                    return
        if len(remoteUrl) > 0:
            cmd = "git"
            for arg in args:
                cmd += " " + arg
            os.system(cmd)
            os.system("git remote set-url origin %s" % remoteUrl)
        else:
            print "error: wrong url."
    elif args[0] == "commit":
        # print args
        for i,arg in enumerate(args):
            if arg[0:2] == "-m":
                if len(arg) > 2:
                    args[i] = "-m"
                    args.insert(i+1,"\""+ arg[2:len(arg)] +"\"")
                    break
                elif arg == "-m" and len(args) > i+1:
                    temparg = "\"" + args[i + 1] + "\""
                    args[i + 1] = temparg
                    break
        cmd = "git"
        # print args
        for arg in args:
            cmd += " " + arg
        os.system(cmd)


    else:
        cmd = "git"
        for arg in args:
            cmd += " " + arg
        os.system(cmd)
    
if __name__ == '__main__':
    main()

