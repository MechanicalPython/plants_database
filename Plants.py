#!/usr/bin/env python3

import sys

if len(sys.argv) > 1:
    if sys.argv[1] == '-U':
        import updater
        updater.update()
        print('Updated to latest version')
        quit()
    else:
        print('Incorrect flag. [-U] for update')
        quit()

else:
    from plants import gui

    app = gui.SelectionScreen()
    app.mainloop()

# test change