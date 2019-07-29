#! /usr/local/bin/python3


from plants import gui
from plants import rhs_scrape
import os


if os.path.exists(f'/Users/Matt/pyprojects/plants/Resources'):
    resources_file = f'/Users/Matt/pyprojects/plants/Resources'
else:
    resources_file = f"{__file__.split('.app')[0]}.app/Contents/Resources"

if os.path.exists(f'{resources_file}/plants.pkl') is False:

    rhs_scrape.main_downloader()


app = gui.SelectionScreen()
app.mainloop()

