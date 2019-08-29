#!/usr/bin/env python3

import subprocess
import os


def update():
    subprocess.call('git pull origin master')

    req_file = f'{os.path.dirname(__file__)}/requirements.txt'
    subprocess.call(f'pip install -r {req_file}')
