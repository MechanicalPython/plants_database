#!/usr/bin/env python3

import subprocess
import os


def update():
    os.chdir(f'{os.path.dirname(__file__)}')
    process = subprocess.Popen(["git", "pull", "origin", "master"], stdout=subprocess.PIPE)
    output = process.communicate()[0]

    req_file = f'{os.path.dirname(__file__)}/requirements.txt'
    process = subprocess.Popen(["pip3", "install", "-r", f'{req_file}', "--user"])
    output = process.communicate()[0]
