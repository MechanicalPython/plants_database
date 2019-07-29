#! /usr/local/bin/python3
"""
Handles the database.  The database is in a dictionary format:
    {plant latin name:  {'Image': 'Podophyllum delavayi.jpg',
                         'Common_name': 'Chinese mayapple',
                         'Family': 'Berberidaceae',
                         'Genus': 'Podophyllum are rhizomatous perennials with lobed leaves, varying in shape from hexagon to starburst, with a central stem. The leaves are thick and textured, with prominent veins and often marbled or mottled in shades of green and brown. The flowers are cup- or bell-shaped, upright or hanging, in red, pink or white, and may be followed by red or yellow fruit',
                         'Details': 'P. delavayi is a rhizomatous perennial producing circular leaves up to 30cm across with deep, jagged lobes. These emerge heavily bronzed in spring, changing to very dark green mottling with age. Clusters of narrow, hanging, dark red flowers are produced below the leaves in summer, followed by black fruit',
                         'Range': 'W China',
                         'Foligae': ['Deciduous'],
                         'Habit': ['Bushy'],
                         'Hardiness': 'H4',
                         'Sunlight': ['Full Shade', 'Partial Shade'],
                         'Aspect': ['North-facing', 'West-facing', 'East-facing'],
                         'Exposure': ['Sheltered'],
                         'Soil_type': ['Clay', 'Loam'],
                         'Moisture': ['Moist but well-drained'],
                         'pH': ['Acid', 'Neutral'],
                         'Max_height': 0.5,
                         'Min_height': 0.1,
                         'Max_spread': 0.5,
                         'Min_spread': 0.1,
                         'Time_to_height': '2-5 years',
                         'Cultivation': 'Grow in humus-rich, leafy, moist soil in full or partial shade, sheltered from wind',
                         'Propagation': 'Propagate by seed sown in containers in an open frame as soon as ripe, or by division in spring or late summer',
                         'Pruning': 'No pruning needed',
                         'Pests': 'Emerging leaves may be damaged by slugs and snails',
                         'Diseases': 'Generally disease free',
                         'Favourite': False,
                         'plant_native': True/None,
                         'plant_is_fragrant',
                         'plant_awards',
                         'plant_pollination',
                         'plant_garden_type',
                         'plant_planting_places',
                         'flower',
                         'foliage',
                         'fruit',
                         'stem',
                         'spring',
                         'summer',
                         'autumn',
                         'winter',
                         'plant_plant_type'
                         }

Needs:
    Input dict from GUI checkbox:


Module must do the following:
    Find all plants that match submit dictionary and convert to a pandas dataframe
    Add fields to plants.pkl
    Add favourites to plants.pkl
"""

import os
import pickle

if os.path.exists(f'/Users/Matt/pyprojects/plants/Resources'):
    resources_file = f'/Users/Matt/pyprojects/plants/Resources'
else:
    resources_file = f"{__file__.split('.app')[0]}.app/Contents/Resources"

plants_db = f'{resources_file}/plants.pkl'
favourites_path = f'{resources_file}/favourites.pkl'


class Search:
    """
    Assumes 'or' condition.
    In submit dict, 1 is True/selected
    Input is {Attribute (Habit) : {Property 1 (Bushy): 1 (True) or 0 (False), ...}}

    """

    def __init__(self, submit):
        with open(plants_db, 'rb') as f:
            self.db = pickle.load(f)
        self.submit = submit

    def convert_submit(self):
        """
        Convert input to {property: [ls of attributes], ..}
        """
        new_submit = {}
        for attribute, values in self.submit.items():
            new_submit.update({attribute: []})
            for value, boolean in values.items():
                if boolean == 1:
                    new_submit[attribute].append(value)
        self.submit = new_submit
        return new_submit

    def find_matches(self):
        plant_matches = []
        for plant, attributes in self.db.items():  # plant, {attribute: value}
            tracker = True
            for attribute, details in attributes.items():  # foliage, [d, e]
                if details is None:  # Convert None value to 'None' so it matches the submit version of none
                    details = 'None'
                if type(details) is not list:  # Just in case it's not a list.
                    details = [details]
                if tracker is False:  # Breaks the loop is the plant has failed already to avoid extra computation.
                    continue
                if attribute in self.submit:  # Check that attribute being looked at is in the submit dict.
                    if any(detail in details for detail in self.submit[attribute]) is False:  # if none of [d, e] in submit[foliage] --> [d]:
                        tracker = False  # Change tracker to False as it failed this test and therefore this plant does not match.
            if tracker is True:
                plant_matches.append(plant)
        return plant_matches

    def main(self):
        self.submit = self.convert_submit()
        matches = self.find_matches()
        match_dict = {match: self.db[match] for match in matches}
        return match_dict


def favourites():
    if os.path.exists(favourites_path) is False:
        with open(favourites_path, 'wb') as f:
            pickle.dump([], f)
    with open(favourites_path, 'rb') as f:
        favs = pickle.load(f)
    return favs


def plant_options(options=None):
    """
    Returns the unique values for a given options. 
    :param options:
    :return:
    """
    if options is None:
        options = ['Foligae', 'Habit', 'Hardiness', 'Sunlight', 'Aspect', 'Exposure', 'Soil_type', 'Moisture', 'pH',
                   'Max_height', 'Min_height', 'Max_spread', 'Min_spread', 'Time_to_height', 'Favourite']
        # 'plant_native', 'plant_is_fragrant', 'plant_awards', 'plant_pollination', 'plant_garden_type',
        # 'plant_planting_places', 'flower', 'foliage', 'fruit', 'stem', 'spring', 'summer', 'autumn',
        # 'winter', 'plant_plant_type']

    options_dict = {}
    for option in options:
        options_dict.update({option: []})

    with open(f'{resources_file}/plants.pkl', 'rb') as f:
        d = pickle.load(f)
    for plant, values in d.items():
        for attribute, value in values.items():  # foliage, yes/no
            if attribute in options_dict.keys():

                if value not in options_dict[attribute]:
                    options_dict[attribute].append(value)

    for att, l in options_dict.items():
        flat_list = []
        for sublist in l:
            if type(sublist) is list:
                for i in sublist:
                    flat_list.append(i)
            else:
                flat_list.append(sublist)
        newlist = list(set(flat_list))
        if '' in newlist:
            newlist.remove('')
        newlist = ['None' if v is None else v for v in newlist]
        options_dict[att] = newlist
    return options_dict


if __name__ == '__main__':
    pass