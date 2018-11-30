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
        remoteHash = remoteRepo.remoteIpfsHash
        ownername = remoteRepo.userName
        reponame = remoteRepo.repoName

        username = raw_input("user name: ")
        pwd = getpass.getpass('password: ')
        # verify auth
        if remoteRepo.verifiAuthRepo(username,pwd,ownername,reponame):
            # gen a key to store remote repo
            pathLocalRemoteRepo = genKey32()
            # download remote repo to local
            print "hit get ipfs repo to local"
            ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteHash,pathLocalRemoteRepo) # 要重命名
            os.system(ipfsGetRepoCmd)
            print "done."
            # push repo to downloaded remote repo
            print "hit push to local..."
            # use local repo to deal push command
            gitPushCmd = "git push %s" % (pathLocalRemoteRepo)
            for arg in args[1:]:

                gitPushCmd = dealArgs(gitPushCmd,arg)
                # gitPushCmd += " " + arg
            os.system(gitPushCmd)
            print "done"
            os.chdir(pathLocalRemoteRepo)
            # update git repo
            os.system("git update-server-info")

            # add file to ipfs network
            addResponse = os.popen("ipfs add -rH .").read()
            lastline = addResponse.splitlines()[-1].lower()
            if lastline != "added completely!":
                print lastline
                os.chdir(projectLocation)
                shutil.rmtree("%s" % pathLocalRemoteRepo, onerror=onerror)
                return
            newRepoHash = addResponse.splitlines()[-2].split(" ")[1]

            # update IPFS hash in the server
            dataUpdate = {"method":"changeIpfsHash","username":username,"password":pwd,
                                     "reponame":reponame,"ownername":ownername,
                                     "ipfsHash":newRepoHash}
            dataUpdate = json.dumps(dataUpdate)

            updateRequest = requests.post(remoteRepo.repoIpfsUrl, data=dataUpdate).json()

            print updateRequest["response"]
            os.chdir(projectLocation)
            shutil.rmtree("%s" % pathLocalRemoteRepo, onerror=onerror)

        else:
            print "ERROR: Access denied to push your code to the repo"



    elif args[0] == "transfer":
        if args[1][0:4] == "http":
            repoNameBare = args[1].split("/")[-1]

            username = raw_input("user name: ")
            password = getpass.getpass('password: ')
            newRepoName = raw_input("repository name: ")

            remoteRepo = RemoteRepoPlatform()
            if remoteRepo.verifiAuth(username,password):
                rootLocation = os.getcwd()
                os.system("git clone --bare %s" % (args[1]))
                os.chdir(repoNameBare)
                # update hit repo info
                os.system("git update-server-info")

                response = os.popen("ipfs add -rH .").read()
                if len(response.splitlines()) > 0:
                    lastline = response.splitlines()[-1].lower()
                    if lastline != "added completely!":
                        print lastline
                        return

                    newRepoHash = response.splitlines()[-2].split(" ")[1]
                    # add repo ipfs hash to server
                    data = {"method": "hitTransfer", "username": username, "password": password, "reponame": newRepoName,
                            "ipfsHash": newRepoHash}
                    data = json.dumps(data)
                    # print "update ipfs hash to %s" % remoteAddress
                    response = requests.post("http://" + remoteAddress + "/webservice/", data=data)
                    response = response.json()

                    print response["response"]

                    os.chdir(rootLocation)
                    # delete useless file
                    shutil.rmtree("%s/%s" % (rootLocation, repoNameBare), onerror=onerror)

                else:
                    print "ipfs add error"
            else:
                print "ERROR: Wrong user name or password."

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
                # parser url, get owner name and repo name
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

