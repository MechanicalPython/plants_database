
import os

if os.path.exists(f'/Users/Matt/pyprojects/plants/Resources'):
    resources_file = f'/Users/Matt/pyprojects/plants/Resources'
else:
    resources_file = f"{__file__.split('.app')[0]}.app/Contents/Resources"


