# -- coding: utf-8 --
class RemoteRepo():
    # read message from repo
    def __init__(self):
        import os
        print "hit get remote url"
        # get ipns hash from git remote command
        gitRemoteCmd = "git remote get-url --all origin"
        gitRemote = os.popen(gitRemoteCmd).read().strip('\n')
        gitRemoteSplit = gitRemote.split("/")
        if gitRemoteSplit[-2] == 'ipns':
            self.remoteUrl = gitRemote
            self.remoteHash = gitRemoteSplit[-1]
            print gitRemoteSplit
            print "hit resolve ipns name"
            # analysis ipfs hash from ipns hash
            # use ipfs resolve command
            remoteFileUrlList = os.popen("ipfs resolve /ipns/%s" % self.remoteHash).read().strip("\n").split("/")
            if remoteFileUrlList[1] == "ipfs":
                self.remoteFileHash = remoteFileUrlList[-1]
                print "hit get ipfs file key"
                # get timestamp of the repo
                ipfsCatTimeStamp = "ipfs cat %s/timestamp" % (self.remoteFileHash)
                print ipfsCatTimeStamp
                self.timeStamp = os.popen(ipfsCatTimeStamp).read()
        else:
            # fail to analysis the url path
            self.remoteHash = ""
            self.timeStamp = ""
            self.remoteUrl = ""
        self.rootFileUrl = ""

    def getRemoteHash(self):
        return self.remoteHash

    def getRemoteUrl(self):
        return self.remoteUrl

    def getTimeStamp(self):
        return self.timeStamp

    def getRemoteFileHash(self):
        return self.remoteFileHash

class RemoteRepoPlatform():
    # a Class to handle all method for platform
    def __init__(self):
        # get repo info from server
        import requests
        import json
        import os
        # from suds.client import Client
        # remoteip = "47.105.76.115"
        # remoteport = "8000"
        # client = Client("http://%s:%s/webservice/?wsdl"%(remoteip,remoteport))
        # self.cf = Config().getHitConfig()
        # # self.repoUrl = self.cf.get("remote \"origin\"","repoUrl")
        # self.repoName = self.cf.get("remote \"origin\"","repoName")
        # self.userName = self.cf.get("remote \"origin\"","userName")
        gitRemoteCmd = "git remote get-url --all origin"
        self.gitRemoteUrl = os.popen(gitRemoteCmd).read().strip('\n')
        argsplit = self.gitRemoteUrl.split("/")
        self.userName = argsplit[-2]
        self.repoName = argsplit[-1].split(".")[-2]

        # 待补充真正的url获取IPFS地址
        # the ip of server api
        self.repoIpfsUrl = "http://47.105.76.115:8000/webservice/"
        # self.remoteIpfs = client.service.getIpfsHash(self.repoName)
        ipfsHashData = json.dumps({"method":"getIpfsHash","ownername":self.userName,"reponame":self.repoName})
        response = requests.post(self.repoIpfsUrl,data=ipfsHashData).json()
        if response["response"] == "success":
            self.remoteIpfsHash = response["ipfs_hash"]
            self.remoteIpfsUrl = "http://localhost:8080/ipfs/" + self.remoteIpfsHash

    def verifiAuth(self,userName,pwd):
        # verify identity of the user
        # Return: True/False
        import json
        import requests
        apiData = json.dumps({"method":"checkUserPassword","username":userName,"password":pwd})
        response = requests.post(self.remoteIpfsUrl,data=apiData).json()
        if response["response"] == "success":
            return True
        else:
            return False

    def hitTransfer(self,username,password,newRepoName,newRepoHash):
        import json
        import requests
        data = {"method": "hitTransfer", "username": username, "password": password, "reponame": newRepoName,
                "ipfsHash": newRepoHash}
        data = json.dumps(data)
        # print "update ipfs hash to %s" % remoteAddress
        response = requests.post(self.repoIpfsUrl, data=data).json()
        return response

    def getRemoteIpfsHashByRepo(self,ownerName,repoName):
        import json
        import requests
        ipfsHashData = json.dumps({"method": "getIpfsHash", "ownername": ownerName, "reponame": repoName})
        response = requests.post(self.repoIpfsUrl, data=ipfsHashData).json()
        return response

    def changeIpfsHash(self,username,pwd,reponame,ownername,ipfshash):
        import json
        import requests
        dataUpdate = {"method": "changeIpfsHash", "username": username, "password": pwd,
                      "reponame": reponame, "ownername": ownername,
                      "ipfsHash": ipfshash}
        dataUpdate = json.dumps(dataUpdate)

        updateRequest = requests.post(self.repoIpfsUrl, data=dataUpdate).json()
        return updateRequest

    def verifiAuthRepo(self,userName,pwd,ownerName,repoName):
        import json
        import requests
        apiData = json.dumps({"method":"checkUserPasswordRepo", "username": userName, "password": pwd, "reponame": repoName, "ownername":ownerName})
        response = requests.post(self.remoteIpfsUrl, data=apiData).json()
        if response["response"] == "success":
            return True
        else:
            return False

    def getIpfsHash(self,hitUrl):
        import json
        import requests
        ownername,reponame = self.parserHitUrl(hitUrl)
        ipfsHashData = json.dumps(
            {"method": "getIpfsHash", "ownername": ownername, "reponame": reponame})
        response = requests.post("http://47.105.76.115:8000/webservice/", data=ipfsHashData).json()
        if response["response"] == "success":
            remoteIpfsHash = response["ipfs_hash"]
            return remoteIpfsHash
        else:
            return 0

    def parserHitUrl(self,hitUrl):
        # TODO:
        # 返回处理结果
        if self.verifyHitUrl(hitUrl):
            argsplit = hitUrl.split("/")
            ownername = argsplit[-2]
            reponame = argsplit[-1].split(".")[-2]
            return ownername,reponame
        else:
            print "error hit url"
            return False

    def verifyHitUrl(self,hitUrl):
        if hitUrl[0:26] == "http://47.105.76.115:8000/" or hitUrl[0:19] == "47.105.76.115:8000/":
            return True
        else:
            return False

    def dealArgs(self, gitPushCmd, arg):
        # TODO:
        # if user add a remote url, there should changes it to hit command
        if self.verifyHitUrl(arg):
            gitPushCmd += ""
        else:
            gitPushCmd += " " + arg
        return gitPushCmd

class Config():
    # config .hit/ folder
    # not use for now
    def __init__(self):
        self.path = ".hit/config"

    def initConfig(self,repoName,userName):
        # init config file
        import ConfigParser
        from funcmodule import mkdir
        mkdir(".hit")
        cf = ConfigParser.ConfigParser()
        cf.read(self.path)
        cf.add_section("remote \"origin\"")
        cf.set("remote \"origin\"","repoName",repoName)
        cf.set("remote \"origin\"","userName",userName)
        with open(self.path, "w+") as f:
            cf.write(f)

    def changeConfig(self,repoName,userName):
        # update config file
        import ConfigParser
        from funcmodule import mkdir
        mkdir(".hit")
        cf = ConfigParser.ConfigParser()
        cf.read(self.path)
        cf.set("remote \"origin\"", "repoName", repoName)
        cf.set("remote \"origin\"", "userName", userName)
        with open(self.path, "w+") as f:
            cf.write(f)

    def getHitConfig(self):
        # get hit config
        import ConfigParser
        cf = ConfigParser.ConfigParser()
        cf.read(self.path)
        return cf

class AccessControl():
    # authority management
    # not use for now
    def __init__(self,pathhash):
        # initial
        import os
        self.projPath = os.getcwd()+'/'
        self.systemPath = os.path.expanduser('~')+'/'
        self.filePath = self.systemPath + ".hit/"
        from funcmodule import mkdir
        mkdir(self.filePath)
        self.ipfsKeyPath = self.systemPath + ".ipfs/keystore/"
        self.pathhash = pathhash

    def setKeyName(self,keyName):
        # set keyName
        self.keyName = keyName

    def setKeyNameFromJson(self):
        # read keyName from authority file
        # and set it as keyName of the class
        import json
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        self.keyName = jsonDict["keyName"]

    def initJson(self):
        # initial authority file
        import json
        import des
        self.createUserKey("self")
        publicKeyIpns = self.getPublicKeyOfIPNS()
        deskey = des.keyGen()
        desClass = des.DESCipher(deskey)
        jsonDict = {"keyName":self.keyName,
                "auth":[{'userKey':self.pubkey.save_pkcs1().decode(),
                         "publicKey":desClass.des_encrypt(publicKeyIpns),
                         "DESKey":self.encrypt(deskey,self.pubkey)}]}
        with open(self.pathhash, 'w') as fout:
            fout.writelines(json.dumps(jsonDict))
            fout.close()

    def getPublicKeyOfIPNS(self):
        # read ipns key from .ipfs
        import binascii
        with open(self.ipfsKeyPath+self.keyName, "rb+") as f:
            data = f.read()
            f.close()
            return binascii.b2a_hex(data)

    def createUserKey(self,userKeyName):
        # gen a user key
        # the key is used to identify user
        import os
        if os.access(self.filePath+userKeyName+'.public.pem',os.F_OK) and os.access(self.filePath+userKeyName+'.private.pem',os.F_OK):
            print "The key already exists"
            self.getUserKey(userKeyName)
        else:
            import rsa
            (self.pubkey, self.privkey) = rsa.newkeys(1024)

            with open(self.filePath+userKeyName+'.public.pem', 'w+') as f:
                f.write(self.pubkey.save_pkcs1().decode())
                f.close()
            with open(self.filePath+userKeyName+'.private.pem', 'w+') as f:
                f.write(self.privkey.save_pkcs1().decode())
                f.close()

    def getUserKey(self,userKeyName):
        # read user key from .hit
        import os
        if os.access(self.filePath+userKeyName+'.public.pem',os.F_OK) and os.access(self.filePath+userKeyName+'.private.pem',os.F_OK):
            import rsa
            with open(self.filePath+userKeyName+'.public.pem', 'r') as f:
                self.pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
                f.close()
            with open(self.filePath+userKeyName+'.private.pem', 'r') as f:
                self.privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())
                f.close()
        else:
            print "You don't have a key named %s" % userKeyName

    @staticmethod
    def encrypt(message,pubkey):
        # rsa encrypt
        import rsa
        import binascii
        return binascii.b2a_hex(rsa.encrypt(message.encode(), pubkey))

    @staticmethod
    def decrypt(crypto,privkey):
        # rsa decrypt
        import rsa
        import binascii
        return rsa.decrypt(binascii.a2b_hex(crypto), privkey).decode()

    # @staticmethod
    # def sign(message,privkey):
    #     import rsa
    #     return rsa.sign(message.encode(), privkey, 'SHA-1')
    #
    # @staticmethod
    # def verify(message,signature,pubkey):
    #     import rsa
    #     return rsa.verify(message.encode(), signature, pubkey)

    # add a user to authority file
    def addAdmin(self,userPublicKey):
        import json
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        # publicKeyIpns = self.getPublicKeyOfIPNS()
        authFlag = self.verifiAuth(self.pubkey)
        if authFlag:
            if self.verifiAuth(userPublicKey):
                print "The user is already in the list."
            else:
                import des
                deskey = des.keyGen()
                desClass = des.DESCipher(deskey)
                publicKeyIpns = self.getPublicKeyFromJson()
                jsonDict["auth"].append({'userKey':userPublicKey.save_pkcs1().decode(),
                                         "publicKey":desClass.des_encrypt(publicKeyIpns),
                                         "DESKey":self.encrypt(deskey,userPublicKey)})
                with open(self.pathhash, 'w') as fout:
                    fout.writelines(json.dumps(jsonDict))
                    fout.close()
                print "The user has been added."
        else:
            print "You don't have authority to do this!!!"


    # delete a user from authority key
    def deleteAdmin(self,userPublicKey):
        import json
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        authFlag = self.verifiAuth(self.pubkey)
        if authFlag:
            if self.verifiAuth(userPublicKey):
                for auth in jsonDict['auth']:
                    if auth["userKey"] == userPublicKey.save_pkcs1().decode():
                        jsonDict["auth"].remove(auth)
                        break
                with open(self.pathhash, 'w') as fout:
                    fout.writelines(json.dumps(jsonDict))
                    fout.close()
                print "The user have been deleted."
            else:
                print "The user is not in the list."
        else:
            print "You don't have authority to do this!!!"

    # verity whether the user in the authority file
    def verifiAuth(self,userPublicKey):
        import json
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        authFlag = False
        for userAuth in jsonDict["auth"]:
            if userAuth["userKey"] == userPublicKey.save_pkcs1().decode():
                authFlag = True
                break
        return authFlag

    # get ipns public key from authority file
    def getPublicKeyFromJson(self):
        import json
        # import binascii
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        publicKeyOfIPNS = ''

        for userAuth in jsonDict["auth"]:
            if userAuth["userKey"] == self.pubkey.save_pkcs1().decode():
                import des
                deskey = self.decrypt(userAuth["DESKey"],self.privkey)
                desClass = des.DESCipher(str(deskey))
                publicKeyOfIPNS = desClass.des_descrypt(userAuth["publicKey"])
                break
        # if authFlag:
        #     dataTurn = binascii.a2b_hex(publicKeyOfIPNS)
        #     filePath = self.keyName
        #     binfile = open(filePath,'wb')
        #     binfile.write(dataTurn)
        #     print "You have generate the key for publish ipns."
        # else:
        #     print "You don't have authority to do this!!!"

        return publicKeyOfIPNS

    # save ipns key to .ipfs
    def savePublicKeyOfIpns(self,ipnsKey):
        import binascii
        dataTurn = binascii.a2b_hex(ipnsKey)
        with open(self.ipfsKeyPath+self.keyName,'wb') as f:
            f.write(dataTurn)
            f.close()
            print "You have get the key for publish ipns."

    # delete the key from ipfs
    def deleteIPNSKey(self):
        import os
        cmd = "ipfs key rm %s" % self.keyName
        os.system(cmd)

    # delete user key from .hit
    def deleteUserKey(self,userKeyName):
        import os
        os.system("rm "+ self.filePath + userKeyName + '.public.pem')
        os.system("rm "+ self.filePath + userKeyName + '.private.pem')

