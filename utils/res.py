import os, sys, errno
import tempfile
import time
import json
from colorama import Fore

SUCCESS = Fore.GREEN + "  [SUCCESS] " + Fore.RESET
FAIL = Fore.RED + "  [FAIL] " + Fore.RESET

username = ""
password = ""
site = "https://www.srrdb.com/"
sitexxx= "https://www.srrxxx.com/"
srrdb_api = "https://www.srrdb.com/api/search/"
srrxxx_api = "https://www.srrxxx.com/api/search/"
srrdb_download = "https://www.srrdb.com/download/srr/"
srrxxx_download = "https://www.srrxxx.com/download/srr/"

loginData = {"username": username, "password": password}
loginUrl = site + "account/login"
loginUrlxxx = sitexxx + "account/login"
loginTestUrl = site
loginTestUrlxxx = sitexxx
loginTestString = username

rar_version = "C:\\Python\\Python39\\pyrescene-master\\rarv"
srr_temp_foder = "C:\\Python\\Python39\\pyrescene-master\\rarv\\tmp"

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            return True
        else:
            raise OSError(e)
    else:
        return True

def search_by_name(name, s, xxx=False, isdir = False):
    if not name or name == "":
        raise ValueError("Release must have a valid name")

    if not isdir:
        name_search = srrdb_api + "r:" + name.rsplit( ".", 1 )[ 0 ]
        if xxx:
            name_search = srrxxx_api + "r:" + name.rsplit( ".", 1 )[ 0 ]
    else:
        name_search = srrdb_api + "r:" + name
        if xxx:
            name_search = srrxxx_api + "r:" + name

    try:
        response = s.retrieveContent(name_search)
        data = response.json()
    except:
        raise

    if 'resultsCount' not in data or int(data['resultsCount']) < 1:
        return None

    return data['results']

def download_srr(rls, s, xxx=False, path=None):
    if not rls or rls == "":
        raise ValueError("Release must have a valid name")

    srr_download = srrdb_download + rls
    if xxx:
        srr_download = srrxxx_download + rls

    if not path or path == "":
        path = tempfile.gettempdir()

    if not os.path.isdir(path):
        raise IOError("Output directory \"", path, "\" does not exist.")

    #create path for file to be stored
    path = os.path.join(path, os.path.basename(srr_download + ".srr"))

    try:
        response = s.retrieveContent(srr_download)

        if response.text == "The SRR file does not exist.":
            return (False, "Release does not exist on srrdb.com")

        if response.text == "You've reached your daily download limit.":
            raise ValueError("You've reached your daily download limit.")

        if response.text == "You have sent too many requests in a given amount of time.":
            raise ValueError("You have sent too many requests in a given amount of time.")

        with open(path, "wb") as local_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    local_file.write(chunk)
                    local_file.flush()
    except:
        raise

    return path