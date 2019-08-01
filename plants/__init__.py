
import os
import pickle

if os.path.exists(f'/Users/Matt/pyprojects/plants/Resources'):
    resources_file = f'/Users/Matt/pyprojects/plants/Resources'
else:
    resources_file = f"{__file__.split('.app')[0]}.app/Contents/Resources"


def get_plants_db():
    with open(f'{resources_file}/plants.pkl', 'rb') as f:
        plants = pickle.load(f)
    return plants

import pprint as pp
# atts = ['Image', 'Common_name', 'Family', 'Genus', 'Details', 'Range', 'Foligae', 'Habit',
#         'Hardiness', 'Sunlight', 'Aspect', 'Exposure', 'Soil_type', 'Moisture', 'pH',
#         'Max_height', 'Min_height', 'Max_spread', 'Min_spread', 'Time_to_height',
#         'Cultivation', 'Propagation', 'Pruning', 'Pests', 'Diseases', 'Favourite', 'plant_native',
#         'plant_is_fragrant', 'plant_awards', 'plant_pollination', 'plant_garden_type', 'plant_planting_places',
#         'flower', 'foliage', 'fruit', 'stem', 'spring', 'summer', 'autumn', 'winter', 'plant_plant_type']

remove_list = []
d = get_plants_db()
for plant, atts in d.items():
    if (sum(x is None for x in list(atts.values()))) > 12:  # 961 have more than 12 none values so remove those.
        remove_list.append(plant)
for p in remove_list:
    d.pop(p, None)

with open(f'{resources_file}/plants.pkl', 'wb') as f:
    pickle.dump(d, f)

