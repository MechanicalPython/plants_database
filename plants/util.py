#! /usr/local/bin/python3.7

"""
General functions that are needed in projects.
All functions need to / should be usable in all functions and operate in that project folder.
"""

import datetime
import hashlib
import os


def timer(func):
    def f(*args, **kwargs):
        start = datetime.datetime.now()
        rv = func(*args, **kwargs)
        end = datetime.datetime.now()
        print('Time taken', end - start, ' for ', func.__name__)
        return rv
    return f


def hashfile(path):
    """Returns md5 hexdigest (len=32)"""
    if os.path.exists(path) is False:
        raise TypeError('Path is not valid')
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        hasher.update(f.read())

    return hasher.hexdigest()


def check_size(path):
    return os.path.getsize(path)


def find_duplicate_files(dir_path):
    """
    Prints out the duplicate files
    :param dir_path:
    :return:
    """
    # Get all file paths in the dir
    print('Walking')
    all_files = []
    for dir, subdirs, files in os.walk(dir_path):
        # Convert all files to full filepath
        files = [f'{dir}/{file}' for file in files]
        all_files.extend(files)

    print('Checking file sizes')
    # Check file size for all files
    file_sizes = {}  # File name: size
    for file in all_files:
        file_sizes.update({file: os.path.getsize(file)})
    sizes = list(file_sizes.values())
    dup_sizes = set([x for x in sizes if sizes.count(x) > 1])

    print('Checking hashes')
    # Files with same file size check hash
    hashed_files = {}  # {hash: [ls of files]}
    for file, size in file_sizes.items():
        if size in dup_sizes:
            hash = hashfile(file)
            if hash in hashed_files.keys():
                hashed_files[hash].append(file)
            else:
                hashed_files.update({hash: [file]})

    # Print file name
    for files in hashed_files.values():
        if len(list(files)) > 1:
            print(files)


def sha1hash(string):
    """Returns sha1 hexsigest which is 40 characters long"""
    return hashlib.sha1(string.encode('utf-8')).hexdigest()


if __name__ == '__main__':
    pass
