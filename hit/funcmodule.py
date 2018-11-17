# -- coding: utf-8 --
def gitPushExchange(pathLocalRemoteRepo,args):
    import os
    # TUDO:
    # changge git push command to hit
    # identify the remote url and adjust it to IPFS
    remoteNameList = os.popen("git remote").read().splitlines()
    for i,arg in enumerate(args):
        if arg in remoteNameList:
            args[i] = pathLocalRemoteRepo
        if arg[0:4] == "http":
            args[i] = pathLocalRemoteRepo
        else:
            args.insert(1,pathLocalRemoteRepo)

    pushCmd = "git"
    for arg in args:
        pushCmd += " " + arg

    return pushCmd

# gen a random 32 byte key
def genKey32():
    # gen a random 32 byte key
    import random
    import string
    return ''.join(random.sample(string.ascii_letters + string.digits, 32))

def mkdir(path):
    # new folder
    import os
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)

    if not isExists:
        print path+': create successfull'
        os.makedirs(path)
        return True
    else:
        print path+': path already exist'
        return False

def readPublicKey(keyPath):
    # use rsa to read a publickey file
    # not use
    with open(keyPath, 'r') as f:
        import rsa
        pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
        f.close()
    return pubkey


