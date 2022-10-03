from PIL import Image
from io import BytesIO
import sys
import logging
from os import walk
from os.path import (
    join,
    isfile,
    isdir)
from uuid import uuid4

def func_name():
    return sys._getframe(1).f_code.co_name

def get_files(directory):
    file_list = list()
    for root, dirs, files in walk(directory, topdown=False):
        for name in files:
            if not name.startswith(".") and (
                                            name.lower().endswith(".jpg") or
                                            name.lower().endswith(".png") or
                                            name.lower().endswith(".jpeg")
                                        ):
                file_list.append(join(root, name))
    return file_list

def generate_id():
    return str(uuid4())