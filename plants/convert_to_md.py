"""
Converts a dictionary to a table view
Dict format: {

| Header 1    | Header 2|
| ----        | ---- |
| 5           | 6    |
| 9           | 10   |
| 13          | 14   |

Only works with typora probably.

"""
import os
import re

if os.path.exists(f'/Users/Matt/pyprojects/plants/Resources'):
    resources_file = f'/Users/Matt/pyprojects/plants/Resources'
else:
    resources_file = f"{__file__.split('.app')[0]}.app/Contents/Resources"


downloads_file = f"{os.path.expanduser('~')}/Downloads"


class Df2Md:
    def __init__(self, df):
        self.df = df
        self.main_string = ''

    def add_line(self, items):
        line = '|'
        for item in items:
            line += f'{item}|'
        line += '\n'
        self.main_string += line

    def headers(self):
        headers = self.df.columns.tolist()
        self.add_line(headers)

    def second_line(self):
        second_line = []
        for header in self.df.columns.tolist():
            second_line.append('-')
        self.add_line(second_line)

    def add_values(self):
        for header, row in self.df.iterrows():
            self.add_line(row.values.tolist())

    def get_images(self):
        m = re.compile(r'\|.+\.jpg')  # |any string of characters.jpg|
        jpgs = m.findall(self.main_string)
        image_dir = f'{resources_file}/plant_images/'
        for jpg in jpgs:
            jpg = jpg.split('|')[-1]
            plant_name = jpg.replace('.jpg', '').replace('|', '')
            self.main_string = self.main_string.replace(jpg, f"![{plant_name}]({image_dir}{jpg})")

    def main(self):
        self.headers()
        self.second_line()
        self.add_values()

        self.get_images()
        with open(f'{downloads_file}/plants.md', 'w') as f:
            f.write(self.main_string)


if __name__ == '__main__':
    pass
    # import pickle
    # with open(f'{resources_file}/plants.pkl', 'rb') as f:
    #     df = pd.DataFrame.from_dict(pickle.load(f), orient='index').head(10)
    #     df = df[['Common_name', 'Image', 'Details']]
    #     print(df)
    #
    # Df2Md(df).main()

