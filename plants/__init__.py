
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
