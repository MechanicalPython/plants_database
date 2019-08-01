#! /usr/local/bin/python3


from plants import gui
from plants import rhs_scrape
import os
from plants import resources_file


if os.path.exists(f'{resources_file}/plants.pkl') is False:
    rhs_scrape.main_downloader()


app = gui.SelectionScreen()
app.mainloop()

