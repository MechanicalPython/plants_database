#!/usr/bin/env python3

import subprocess
import os


def update():
    process = subprocess.Popen(["git", "pull", "origin", "master"], stdout=subprocess.PIPE)
    output = process.communicate()[0]

    req_file = f'{os.path.dirname(__file__)}/requirements.txt'
    process = subprocess.Popen(["pip", "install", "-r", f'{req_file}'])
    output = process.communicate()[0]
