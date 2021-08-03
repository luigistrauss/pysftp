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
unzipped = "/path/to/unzipped/directory/"
localDirPath = "/path/to/script/root/dir"
remoteDir1 = "/path/to/ftp/directory1/"
remoteDir2 = "/path/to/ftp/directory2/"

# 1. Download files for both vessels
def download_files():
    with pysftp.Connection(host=myHostname, username=myUsername, port=myPort, private_key='/path/to/.ssh/id_rsa', cnopts=cnopts) as sftp:
        print("Connection to MF ftp successful")
        # 2.a Download 1st set of files
        localFiles = os.listdir(localDirPath)
        print("Checking 1st Files")
        for attr in sftp.listdir_attr(remoteDir1):
            try:
                if attr.filename not in localFiles and fnmatch.fnmatch(attr.filename, "*.zip"):
                    sftp.get(os.path.join(remoteDir1, attr.filename))
                    copiedFiles.append(attr.filename)
            except IOError:
                print("Error downloading 1st files") 

        # 2.b Download Oceanic Champion files
        localFiles = os.listdir(localDirPath)
        print("Checking 2nd Files")
        for attr in sftp.listdir_attr(remoteDir2):
            try:
                if attr.filename not in localFiles and fnmatch.fnmatch(attr.filename, "*.zip"):
                    sftp.get(os.path.join(remoteDir2, attr.filename))
                    copiedFiles.append(attr.filename)
            except IOError:
                print("Error downloading CHP files")
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
                    if fileName.endswith('HR.S01') and fileName not in unzipped:
                        try:
                            zip_ref.extract(
                                fileName, unzipped)
                        except BadZipfile:
                            print("{} is an invalid file".format(fileName))
                    else:
                        pass
    #Look for SPS files & move to root directory
    for root, dirs, files in os.walk((os.path.normpath(unzipped)), topdown=False):
        for name in files:
            if name.endswith('HR.S01'):
                SourceFolder = os.path.join(root, name)
                try:
                    shutil.move(SourceFolder, unzipped)
                except shutil.Error:
                    pass
    # remove empty directories
    print("Removing empty directories")
    dirs = list(os.walk(unzipped))
    for path, _, _ in dirs[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)
    return unzipped

# 3. Create mfa files by triggering shell script
def process_mfa(unzipped):
    # 5. Trigger ionsps script
    mfa = subprocess.call(
        ['sh', '/path/to/shell/script/.sh', '/path/to/unzipped/directory/'])
    print("MFA generation complete")
    # 6. Remove all unzipped files to ensure no duplicate imports
    remove_files = subprocess.run(
        ["rm", "-rf", "/path/to/unzipped/directory/"])
    print(remove_files)

def main():
    downloaded_files = download_files()
    unzip = unzip_files(copiedFiles)
    processing = process_mfa(unzipped)

if __name__ == "__main__":
    main()
