"""
https://docs.python.org/3/library/tk.html
GUI builder for the program. Must take inputs and give windows.
Foliage
Habit
Hardiness
Aspect
Exposure
Soil
Moisture
pH
Max_height
Min_height
Max_spread
Min_spread
Time_to_height
"""

import tkinter as tk
import tkinter.messagebox as msg
from collections import OrderedDict
import pandas as pd
from PIL import Image, ImageTk
import os

from plants import backend
from plants import convert_to_md
# Either uses plants/Resources or Contents/Resources if it's in a .app package.

if os.path.exists(f'/Users/Matt/pyprojects/plants/Resources'):
    resources_file = f'/Users/Matt/pyprojects/plants/Resources'
else:
    resources_file = f"{__file__.split('.app')[0]}.app/Contents/Resources"

class SelectionScreen(tk.Tk):
    """
    |        Foliage      |    Hardiness...
    | [] Foliage option 1 | [] H1       ...
    | [] Foliage option 2 | [] H2       ...
    | [] Foliage option 3 | [] H3       ...
    | [] None             | [] None     ...
    |                     |             ...
    |

    Definitions
    plants_db = main plants dictionary: {plant name: {soil_type: [ls of soil types], ...}, }
    attribute = the name of the variables a plant can have. E.g. Soil_type, Image, Common_name are all attributes
    property  = the value of the attribute. E.g. Clay (a soil type)
    options   = the unique properties for each attribute
    """

    def __init__(self, options=None):
        super().__init__()
        self.resizable(False, False)
        if not options:
            self.options = backend.plant_options()  # {attribute: [ls of unique properties]}
        else:
            self.options = backend.plant_options(options)

        self.favs = backend.favourites()
        self.checkbox_state = {}
        self.title('Plants')
        row = 0
        column = 0
        max_column_length = 8

        order_of_keys = sorted(self.options, key=lambda k: (-len(self.options[k]), k))
        list_of_tuples = [(key, self.options[key]) for key in order_of_keys]
        self.options = OrderedDict(list_of_tuples)

        for attribute, properties in self.options.items():
            self.checkbox_frame(title=attribute, options=properties, row=row, column=column)
            if column <= max_column_length:
                column += 1
            else:
                row += 1
                column = 0

        submit_frame = tk.Frame(self)
        submit_frame.grid(row=row + 2, column=0, columnspan=max_column_length)

        self.submit_button = tk.Button(submit_frame, text='Submit', command=self.get_inputs, height=3)
        self.submit_button.pack(fill='both', expand=True, side=tk.BOTTOM)

        # self.view_favs = tk.Button(submit_frame, text='View Favourites', command=self.view_favourites)

    def checkbox_frame(self, title='Default', options=None, row=None, column=None):
        frame = tk.Frame(self)
        frame.grid(row=row, column=column, sticky=tk.N)
        frame.pack_propagate(1)

        display_title = title.replace('_', ' ').capitalize()
        if 'max' in display_title.lower() or 'min' in display_title.lower():
            display_title = f'{display_title} (m)'
        label = tk.Label(frame, text=display_title, fg='red')
        label.grid(row=0, column=0)

        if 'None' in options:
            options.remove('None')
            options.sort()
            options.append('None')
        else:
            options.sort()

        row = 1
        for option in options:
            var = tk.IntVar()
            var.set(1)
            box = tk.Checkbutton(frame, text=str(option).replace('_', ' '), variable=var)
            box.grid(row=row, column=0, sticky=tk.W)
            row += 1
            if title in self.checkbox_state:
                self.checkbox_state[title].update({option: var})
            else:
                self.checkbox_state.update({title: {option: var}})

        def select_all():
            values = [value.get() for value in list(self.checkbox_state[title].values())]
            if all(values) == 1:
                for option in self.checkbox_state[title].keys():
                    self.checkbox_state[title][option].set(0)
            else:
                for option in self.checkbox_state[title].keys():
                    self.checkbox_state[title][option].set(1)

        select_all_button = tk.Button(frame, text='All', command=select_all)
        select_all_button.grid(row=row + 1, sticky=tk.W)

    def get_inputs(self):
        self.submit_button.config(relief='sunken')
        submit_values = {}
        for property, attributes in self.checkbox_state.items():
            submit_values.update({property: {}})
            for attribute, value in attributes.items():
                value = value.get()
                submit_values[property].update({attribute: value})
        return_values = backend.Search(submit_values).main()
        self.submit_button.config(relief='raised')
        if len(return_values) == 0:
            msg.showinfo('Input Alert', 'Search yielded no results. Try widening the search')
        elif len(return_values) > 100:
            msg.showinfo('Input Alert', f'You have selected {len(return_values)}. Please narrow search (100 is limit)')
        else:
            msg.showinfo('Plants', f'You have selected {len(return_values)} plants')
            ConfirmationWindow(return_values)  # In new window, shows the plant and asks for confirmation in their use.

    def view_favourites(self):
        pass


class ConfirmationWindow(tk.Toplevel):
    """
    Scrollable table view of image, plant name, description with checkboxes for the plants that are to be used.
    return_values are a subset of the plants.pkl database: {plant name: {soil_type: [ls of soil types], ...}, }
    """

    def __init__(self, return_values=None):
        """
        Canvas is the main widget. Then make a frame for all the plants to go in. Submit button that is independent of
        the plants frame.
        :param return_values:
        """
        super().__init__()
        self.return_values = return_values

        self.title('Confirmation')
        self.plants_canvas = tk.Canvas(self)
        self.geometry('1000x1000')

        self.plants_frame = tk.Frame(self.plants_canvas)
        self.bottom_frame = tk.Frame(self)

        self.scrollbar = tk.Scrollbar(self.plants_canvas, orient='vertical', command=self.plants_canvas.yview)
        self.plants_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.plants_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_frame = self.plants_canvas.create_window((0, 0), window=self.plants_frame)

        self.confirm_window_check_box = {}
        row = 0
        for plant_name, attributes in self.return_values.items():  # canvas default size is 50,000 pixels.
            self.mk_row(plant_name, attributes, row)
            row += 1

        self.submit_button = tk.Button(self.bottom_frame, text='          Submit          ', height=3, command=self.return_inputs)
        self.select_all_bt = tk.Button(self.bottom_frame, text='        Select all        ', height=3, command=self.select_all)
        self.add_favourite = tk.Button(self.bottom_frame, text='Add selected to favourites',
                                       height=3, command=self.add_selected_to_favourite)

        self.add_favourite.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.submit_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.select_all_bt.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.bind("<Configure>", self.on_frame_configure)
        self.bind_all("<MouseWheel>", self.mouse_scroll)
        self.plants_canvas.bind("<Configure>", self.task_width)

    def select_all(self):
        values = [value.get() for value in list(self.confirm_window_check_box.values())]
        if all(values) == 1:
            for plant, value in self.confirm_window_check_box.items():
                value.set(0)
        else:
            for plant, value in self.confirm_window_check_box.items():
                value.set(1)

    def add_selected_to_favourite(self):
        pass

    def return_inputs(self):
        plants_to_use = {}
        for plant, var in self.confirm_window_check_box.items():
            if var.get() == 1:
                plants_to_use.update({plant: self.return_values[plant]})
        if len(plants_to_use) == 0:
            msg.showinfo('Input Error', 'You have not selected any plants.')
            return None

        df = pd.DataFrame.from_dict(plants_to_use, orient='index').reset_index()
        df = df.rename(columns={'index': 'Latin_Name'})
        df = df[['Latin_Name', 'Image', 'Common_name', 'Details']]
        convert_to_md.Df2Md(df).main()
        self.destroy()

    def mk_row(self, plant_name, attributes, row):
        """
        | [] Plant name | Image | Details  |
        :param plant_name:
        :param attributes:
        :return:
        """
        frame = self.plants_frame

        var = tk.IntVar()
        var.set(0)
        check_button = tk.Checkbutton(frame, text=plant_name, variable=var, justify=tk.LEFT)
        check_button.grid(row=row, column=0)

        self.confirm_window_check_box.update({plant_name: var})

        try:
            image_file_path = f"{resources_file}/plant_images/{attributes['Image']}"
            load = Image.open(image_file_path)

        except OSError:
            image_file_path = f"{resources_file}/plant_images/no_plant.jpg"
            load = Image.open(image_file_path)
        imgx, imgy = load.size
        x, y = self.image_resize(imgx, imgy, 300, 300)
        render = ImageTk.PhotoImage(load.resize((x, y)), master=frame)
        img = tk.Label(frame, image=render)
        img.image = render
        img.grid(row=row, column=1)
        img.columnconfigure(0, weight=10)

        details = tk.Label(frame, text=attributes['Details'], wraplength=300, justify=tk.LEFT)
        details.grid(row=row, column=2, sticky=tk.E)

    def on_frame_configure(self, event=None):
        self.plants_canvas.configure(scrollregion=self.plants_canvas.bbox("all"))

    def task_width(self, event=None):
        canvas_width = event.width
        self.plants_canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def mouse_scroll(self, event):
        if event.delta:
            self.plants_canvas.yview_scroll(int(-1 * event.delta), 'units')

    @staticmethod
    def image_resize(imgx, imgy, newx, newy):
        if imgx == imgy:
            return newx, newy  # If it's square the resize has not distortions
        if imgx > imgy:
            scale = imgx / newx
        else:
            scale = imgy / newy
        return int(imgx / scale), int(imgy / scale)


if __name__ == '__main__':
    app = SelectionScreen()
    app.mainloop()
