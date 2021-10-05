#!/usr/bin/env python3

import pysftp
import re
import os
import fnmatch
import zipfile
import subprocess
import shutil

os.chdir('/path/to/script/root/dir')   

# Credentials for server
myHostname = "ftpHostName"
myUsername = "ftpUserName"
myPort = <portNo>
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
copiedFiles = []

#files paths
localDirPath = "/path/to/script/root/dir"
unzipped = "/path/to/unzipped/directory/"
remoteDir1 = "/path/to/ftp/directory1/"

# 1. Connect to site 
def download_files():
    with pysftp.Connection(host=myHostname, username=myUsername, port=myPort, private_key='/home/centos/.ssh/id_rsa', cnopts=cnopts) as sftp:
        print("Connection to MF ftp successful")
        # 1a. Download files
        localFiles = os.listdir(localDirPath)
        print("Checking for Files")
        for attr in sftp.listdir_attr(remoteDir1):
            try:
                if attr.filename not in localFiles and fnmatch.fnmatch(attr.filename, "*.zip"):
                    sftp.get(os.path.join(remoteDir1, attr.filename))
                    copiedFiles.append(attr.filename)
            except IOError:
                print("Error downloading files") 

    sftp.close()
    return (copiedFiles)

# 2. Unzip files & move to unzipped
def unzip_files(copiedFiles):
    for f in copiedFiles:
        print("Processing " + f)
        if os.path.getsize(f) == 0:
            os.remove(f)
            print("{} was invalid, so removed".format(f))
        else:
            with zipfile.ZipFile(f, 'r') as zip_ref:
                for fileName in zip_ref.namelist():
                    if fileName.endswith('.mfa') and fileName not in unzipped:
                        try:
                            zip_ref.extract(
                                fileName, "/path/to/extracted/directory" )
                        except BadZipfile:
                            print("{} is an invalid file".format(fileName))
                    else:
                        pass
    #Look for MFA files & move to root directory
    for root, dirs, files in os.walk((os.path.normpath(unzipped)), topdown=False):
        for name in files:
            if name.endswith('.mfa'):
                SourceFolder = os.path.join(root, name)
                try:
                    shutil.move(SourceFolder, unzipped)
                except shutil.Error:
                    pass
    return unzipped


def main():
    downloaded_files = download_files()
    unzip = unzip_files(copiedFiles)

if __name__ == "__main__":
    main()
