"""Scrapes the RHS database for all the plant details
"""

import os
import pickle
import requests
import pprint as pp
from plants import web
from plants import resources_file


homepage = 'https://www.rhs.org.uk/Plants/Search-Results?form-mode=true'


def convert_blank_to_none(func):
    def f(*args, **kwargs):
        rv = func(*args, **kwargs)
        if rv == '':
            return None
        return rv
    return f


class GetPlantsUrls:
    def __init__(self, startpage, iterations=None):
        self.currentpage = startpage
        self.iterations = iterations

    def get_details_pages(self, soup):
        """
        For a given page soup, return the list of /Plants/123/plant/Details
        :param soup:
        :return:
        """
        list_of_details_pages = []
        plants = soup.find_all('li', {'class': 'clr'})
        for plant in plants:
            if self.has_details(plant):
                list_of_details_pages.append(self.get_details_href(plant))
        return list_of_details_pages

    @staticmethod
    def get_next_href(soup):
        pagenav_buttons = soup.find_all('a', {'class': 'pagenav'})
        for pagenav_button in pagenav_buttons:
            if pagenav_button.get('title') == 'Next':
                return f"https://www.rhs.org.uk/Plants/Search-Results{pagenav_button.get('href')}"

    @staticmethod
    def has_details(plant_item):
        """
        Return True is there are details, False if none. Uses the plant image to check
        :return:
        """
        if plant_item.find('img').get('src') == '/assets/styles/images/bg/plant-icon.gif':
            return False
        else:
            return True

    @staticmethod
    def get_details_href(plant_item):
        atag = plant_item.find_all('a')
        hrefs = [a.get('href') for a in atag]
        for href in hrefs:
            if href.endswith('/Details') and href[0:8] == '/Plants/':
                return href
        print('ERROR: No href for ', plant_item.text)
        return None

    def main_loop(self):
        detail_href = []
        page = 0
        while True:
            soup = web.get_soup(self.currentpage, cache=False)
            print(page, self.currentpage)
            details = self.get_details_pages(soup)
            detail_href.extend(details)
            next_page = self.get_next_href(soup)
            page += 1
            if next_page is None or page == self.iterations:
                break
            self.currentpage = next_page

        return detail_href


class SinglePlantDetails:
    """
    {Picture: /path/to/pic, Other names: [ls of names], Family: str, Genus: str, Details: str, Foliage: str, Habit: str,
    Fragrance: str, Hardiness: str, Colour in Autumn:  ... , Sunlight:
    """
    def __init__(self, soup):
        if type(soup) == str:
            soup = web.get_soup(soup)
        self.soup = soup.find('div', {'class': 'grid g15-no-font-resize tmp1 gmp1'})
        self.image_dir = f'{resources_file}/plant_images/'
        if os.path.exists(self.image_dir) is False:
            os.mkdir(self.image_dir)

    @convert_blank_to_none
    def get_plant_latin_name(self):
        """
        Used as the key/unique ID for the plant
        :return:
        """
        r = self.soup.find('h1', {'class': 'Plant-formated-Name'})
        if r is not None:
            return r.text.strip().replace('/', '')  # For the image name.
        return None

    @convert_blank_to_none
    def get_common_name(self):
        r = self.soup.find('div', {'class': 'ib'}).find('h2')
        if r is not None:
            return r.text.strip()
        return None

    def get_image(self):
        """Downloads plant image to Resources/plant_images/latin_plant_name.jpg"""
        image = f'{self.get_plant_latin_name()}.jpg'.replace('/', '')

        if image in os.listdir(f'{self.image_dir}'):
            return image
        try:
            image_url = self.soup.find('div', {'class': 'plant-image g7'}).find('img').get('src')
        except AttributeError:
            return None
        if image_url.split('.')[-1] == 'gif':
            return None

        print('Downloading Image... ', image)
        img_data = requests.get(image_url).content
        with open(f'{self.image_dir}{image}', 'wb') as f:
            f.write(img_data)
        if os.path.exists(f'{self.image_dir}{image}'):
            return True
        else:
            return False

    @convert_blank_to_none
    def get_family(self):
        r = self.soup.find_all('li', {'data-facettype': 'genus_description'})
        if len(r) > 0:
            return r[0].text.replace('Family', '').strip()
        return None

    @convert_blank_to_none
    def get_genus(self):
        r = self.soup.find_all('li', {'data-facettype': 'genus_description'})
        if len(r) > 1:
            return r[1].text.replace('Genus', '').strip()
        return None

    @convert_blank_to_none
    def get_details(self):
        r = self.soup.find('li', {'data-facettype': 'description'})
        if r is not None:
            return r.text.replace('Details', '').strip()
        return None

    @convert_blank_to_none
    def get_plant_range(self):
        r = self.soup.find('li', {'data-facettype': 'plant_range'})
        if r is not None:
            return r.text.replace('Plant range', '').strip()
        return None

    def _get_characteristics(self):
        """First two in the li list are foilage and habit. The last are the hardiness ones including the hardiness
        scale."""
        char = self.soup.find('div', {'class': 'grid g3 char'})
        if char is None:
            return None
        return char.find('ul').find_all('li')

    @convert_blank_to_none
    def get_foliage(self):
        """
        :return: ls of Deciduous, Evergreen, Semi-evergreen
        """
        if self._get_characteristics is None:
            return None
        for li in self._get_characteristics:
            if 'Foliage' in li.text:
                return li.text.replace('Foliage', '').strip().split(' or ')
        return None

    @convert_blank_to_none
    def get_habit(self):
        """
        :return: ls of Bushy, Climbing, Clump-forming, Columnar/Upright, Trailing, Mat forming, Spreading/Branching,
        Tufted, Suckering, Submerged, Pendulour/Weeping, Floating
        """
        if self._get_characteristics is None:
            return None
        for li in self._get_characteristics:
            if 'Habit' in li.text:
                r = li.text.replace('Habit', '').strip().split(' or ')
                if r == ['Clump forming']:  # Special case where Clump forming and Clump-forming are both present
                    r = ['Clump-forming']
                return r
        return None

    @convert_blank_to_none
    def get_toxicity(self):
        if self._get_characteristics is None:
            return None
        for li in self._get_characteristics:
            if 'Toxicity' in li.text:
                return li.text.replace('Toxicity', '').strip()
        return None

    @convert_blank_to_none
    def get_hardiness(self):
        options = ['H1a', 'H1b', 'H1c', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7']
        if self._get_characteristics is None:
            return None
        for li in self._get_characteristics:
            if 'Hardiness' in li.text:
                r = li.find_all('p')[-1].text
                if r in options:
                    return r
        return None

    def _get_plant_colours(self):
        """Not in soup"""
        return None

    def _get_sunlight_box(self):
        return self.soup.find('div', {'class': 'grid sun g3'})

    @convert_blank_to_none
    def get_sunlight(self):
        """
        :return: ls of Full Shade, Partial shade, Full sun
        """
        if self._get_sunlight_box is None:
            return None
        li = self._get_sunlight_box.find('div', {'class': 'sunlight'}).find_all('li')
        if len(li) == 0:
            return None
        sunlight = []
        for l in li:
            sunlight.append(l.text.strip())
        return sunlight

    @convert_blank_to_none
    def get_aspect(self):
        """
        :return: ls of North-facing, West-facing, East-facing or South-facing
        """
        if self._get_sunlight_box is None:
            return None
        box = self._get_sunlight_box.find('div', {'class': 'plant-detailed-description'})
        if box is None:
            return None
        r = box.find_all('li')[0].text.replace('Aspect', '').split(' or ')
        return [r.strip() for r in r]

    @convert_blank_to_none
    def get_exposure(self):
        if self._get_sunlight_box is None:
            return None
        box = self._get_sunlight_box.find('div', {'class': 'plant-detailed-description'})
        if box is None:
            return None
        r = box.find_all('li')[1].text.replace('Exposure', '').split(' or ')
        return [r.strip() for r in r]

    @convert_blank_to_none
    def get_soil_type(self):
        """
        :return: ls of Clay, Loam, Sand, Chalk,
        """
        try:
            soils = self.soup.find('div', {'class': 'grid soil g3'}).find('div', {'class': 'soil-types clr'}).find_all('li')
            if len(soils) == 0:
                return None
            soil_types = []
            for soil in soils:
                soil_types.append(soil.text.strip())
            return soil_types
        except AttributeError:
            return None

    @convert_blank_to_none
    def get_moisture(self):
        """
        :return: ls of Moist but well-drained, Well-drained, Moist, Poorly-drained,
        """
        try:
            moistures = self.soup.find('div', {'class': 'grid soil g3'}).find('div', {'class': 'plant-detailed-description clr'}).find_all('li')
            return moistures[0].text.replace('Moisture', '').strip().split(', ')
        except AttributeError:
            return None

    @convert_blank_to_none
    def get_ph(self):
        """
        :return: ls of Acid, Neutral, Alkaline
        """
        try:
            ph = self.soup.find('div', {'class': 'grid soil g3'}).find('div', {'class': 'plant-detailed-description clr'}).find_all('li')
            return ph[2].text.replace('pH', '').strip().split(', ')
        except AttributeError:
            return None

    def _get_size(self, size_type):
        try:
            string = self.soup.find('div', {'class': 'grid size g3'}).find('li', {'class': f'ultimate-{size_type}'}).text.replace(f'Ultimate {size_type}', '').strip()
        except AttributeError:
            return None
        numbers = []
        for item in string.replace('-', ' ').split():
            try:
                numbers.append(float(item))
            except ValueError:
                pass

        if 'metre' in string:
            return numbers
        elif 'cm' in string:
            return [float(num)/100 for num in numbers]
        return None

    @convert_blank_to_none
    def get_max_height(self):
        """Returns max height"""
        r = self.get_height
        if r is None:
            return None
        return max(r)

    @convert_blank_to_none
    def get_min_height(self):
        """Returns min height"""
        r = self.get_height
        if r is None:
            return None
        return min(r)

    @convert_blank_to_none
    def get_max_spread(self):
        """Returns max spread"""
        r = self.get_spread
        if r is None:
            return None
        return max(r)

    @convert_blank_to_none
    def get_min_spread(self):
        """Returns min spread"""
        r = self.get_spread
        if r is None:
            return None
        return min(r)

    @convert_blank_to_none
    def get_time_to_height(self):
        r = self.soup.find('li', {'class': 'time-to-ultimate-height'})
        if r is None:
            return None
        return r.text.replace('Time to ultimate height', '').strip()

    @convert_blank_to_none
    def get_cultivation(self):
        try:
            return self.soup.find('div', {'class': 'how-to'}).find('p', {'data-facettype': 'cultivation'}).text.replace('Cultivation', '').strip()
        except AttributeError:
            return None

    @convert_blank_to_none
    def get_propagation(self):
        try:
            return self.soup.find('div', {'class': 'how-to'}).find('p', {'data-facettype': 'propagation'}).text.replace('Propagation', '').strip()
        except AttributeError:
            return None

    @convert_blank_to_none
    def get_pruning(self):
        try:
            for item in self.soup.find_all('p', {'data-facettype': 'pruning'}):
                if 'Pruning' in item.text:
                    return item.text.replace('Pruning', '').strip()
            return None
        except AttributeError:
            return None

    @convert_blank_to_none
    def get_pests(self):
        try:
            for item in self.soup.find_all('p', {'data-facettype': 'pruning'}):
                if 'Pests' in item.text:
                    return item.text.replace('Pests', '').strip()
            return None
        except AttributeError:
            return None

    @convert_blank_to_none
    def get_diseases(self):
        try:
            return self.soup.find('p', {'data-facettype': 'disease_resistance'}).text.replace('Diseases', '').strip()
        except AttributeError:
            return None

    def main(self):
        self._get_characteristics = self._get_characteristics()
        self._get_sunlight_box = self._get_sunlight_box()
        self.get_height = self._get_size('height')
        self.get_spread = self._get_size('spread')
        return {
            self.get_plant_latin_name():
                {
                'Image': self.get_image(),
                'Common_name': self.get_common_name(),
                'Family': self.get_family(),
                'Genus': self.get_genus(),
                'Details': self.get_details(),
                'Range': self.get_plant_range(),
                'Foligae': self.get_foliage(),
                'Habit': self.get_habit(),
                'Hardiness': self.get_hardiness(),
                'Sunlight': self.get_sunlight(),
                'Aspect': self.get_aspect(),
                'Exposure': self.get_exposure(),
                'Soil_type': self.get_soil_type(),
                'Moisture': self.get_moisture(),
                'pH': self.get_ph(),
                'Max_height': self.get_max_height(),
                'Min_height': self.get_min_height(),
                'Max_spread': self.get_max_spread(),
                'Min_spread': self.get_min_spread(),
                'Time_to_height': self.get_time_to_height(),
                'Cultivation': self.get_cultivation(),
                'Propagation': self.get_propagation(),
                'Pruning': self.get_pruning(),
                'Pests': self.get_pests(),
                'Diseases': self.get_diseases(),
                'Favourite': False
                }
        }


class ExtraPlantData:
    """
    Gets other details that are only attainable from search criteria for some reason.
    https://www.rhs.org.uk/Plants/Search-Results?f_plant_garden_type_architectural           =f%2Fplant_garden_type%2Farchitectural                   &form-mode=true&context=b%3D0%26hf%3D10%26l%3Den%26s%3Ddesc%2528plant_merged%2529%26sl%3DplantForm&unwind=undefined
    https://www.rhs.org.uk/Plants/Search-Results?f_plant_garden_type_city___courtyard_gardens=f%2Fplant_garden_type%2Fcity%20%26%20courtyard%20gardens&form-mode=true&context=b%3D0%26hf%3D10%26l%3Den%26s%3Ddesc%2528plant_merged%2529%26sl%3DplantForm&unwind=undefined
    https://www.rhs.org.uk/Plants/Search-Results?f_plant_garden_type_coastal                 =f%2Fplant_garden_type%2Fcoastal                         &form-mode=true&context=b%3D0%26hf%3D10%26l%3Den%26s%3Ddesc%2528plant_merged%2529%26sl%3DplantForm&unwind=undefined
    Types are:
        plant_native
        plant_is_fragrant
        plant_awards
        plant_pollination
        plant_garden_type
        plant_planting_places
        flower
        foliage
        fruit
        stem
        spring
        summer
        autumn
        winter
        plant_plant_type
    :return: {plant latin name: {attribute: value, ...}
    """
    def __init__(self):
        # replace {} with variable.
        self.base_url = 'https://www.rhs.org.uk/Plants/Search-Results?{}={}&form-mode=true&context=b%3D0%26hf%3D10%26l%3Den%26s%3Ddesc%2528plant_merged%2529%26sl%3DplantForm&unwind=undefined'
        with open(f'{resources_file}/plants.pkl', 'rb') as f:
            self.plants_db = pickle.load(f)

    # Get the extra data: {plant_latin_name: {d1: v, d2: v2...}}
    # Merge it into the existing data

    def main(self):
        """
        :return:
        """
        start_url = 'https://www.rhs.org.uk/Plants/Search-Results?form-mode=true'
        refine_by = web.get_soup(start_url).find('div', {'class': 'find-plant-form-left'})

        # ul, {data-facet-id: option}. For li in option, get input, value and enter to base_url.
        options = ['plant_garden_type', 'plant_planting_places',
                   'f/plant_colour_by_type/flower', 'f/plant_colour_by_type/foliage', 'f/plant_colour_by_type/fruit',
                   'f/plant_colour_by_type/stem', 'f/plant_colour_by_season/spring', 'f/plant_colour_by_season/summer',
                   'f/plant_colour_by_season/autumn', 'f/plant_colour_by_season/winter',
                   'plant_plant_type']
        # These options have no need to search for li, they just need to be added to the base url directly.
        url_starts = ['f/plant_native/true', 'f/plant_is_fragrant/true', 'f/plant_awards/award of garden merit',
                      'f/plant_pollination/true']

        for option in options:
            ul = refine_by.find('ul', {'data-facet-id': option})
            for li in ul.find_all('li'):
                url_starts.append(li.find('input').get('value'))
        # pattern for options is f/category/value or f/category/subcat/value
        for url in url_starts:  # url_input is the start page for several pages.
            start_url = self.base_url.replace('{}', url)
            value = url.split('/')[-1]  # Red or True
            cat = url.split('/')[-2]  # spring or plant_native
            plants_for_this_cat = self.plants_from_start_url(start_url)  # Dict of {plant_name: url}
            print(cat, value)
            for plant, plant_url in plants_for_this_cat.items():
                if plant not in self.plants_db:
                    print('Getting all data for ', plant)
                    self.plants_db.update(SinglePlantDetails(plant_url).main())

            for plant in self.plants_db.keys():
                if plant in plants_for_this_cat:
                    self.plants_db[plant].update({cat: value})
                else:
                    self.plants_db[plant].update({cat: None})
        return self.plants_db

    def plants_from_start_url(self, url):
        """
        Returns a dict of plants and their urls.
        :param url:
        :return:
        """
        plants = {}
        while True:
            print(url)
            soup = web.get_soup(url)
            plant_names = self.get_latin_names_from_search_page(soup)  # {name: details url}
            plants.update(plant_names)
            next_href = self.next_page(soup)
            if next_href is None:
                break
            else:
                url = next_href
        return plants

    @staticmethod
    def get_latin_names_from_search_page(soup):
        """Return {name: url}"""
        names = {}
        plants = soup.find_all('li', {'class': 'clr'})
        for plant in plants:
            tag = plant.find('a', {'class': 'Plant-formated-Name'})
            name = tag.text.strip().replace('/', '')  # Remove the slashes for image names.
            url = f"https://www.rhs.org.uk{tag.get('href')}"
            names.update({name: url})
        return names

    @staticmethod
    def next_page(soup):
        pagenav_buttons = soup.find_all('a', {'class': 'pagenav'})
        for pagenav_button in pagenav_buttons:
            if pagenav_button.get('title') == 'Next':
                return f"https://www.rhs.org.uk/Plants/Search-Results{pagenav_button.get('href')}"



def main_downloader():
    """Threads SinglePlantDetails for all the soups"""
    details_href = f'{resources_file}/detailshref.pkl'
    if os.path.exists(details_href) is False:  # If not done, get each plants url
        urls = GetPlantsUrls(homepage, iterations=1315).main_loop()  # 30041 pages in total, 1315 have useful information.
        with open(details_href, 'wb') as f:
            pickle.dump(urls, f)
    else:
        with open(details_href, 'rb') as f:
            urls = pickle.load(f)

    # Got list of urls (minus the rhs.org.uk bit), get them all now.
    url_head = 'https://www.rhs.org.uk'
    urls = [url_head + url for url in urls]
    return_details = {}
    for url in urls:
        print(url)
        try:
            soup = web.get_soup(url)
            data = SinglePlantDetails(soup).main()
            if data.keys() is None:
                continue
            return_details.update(data)
        except Exception as e:
            print(f'{__file__}: ERROR {e} for {url}')
            pass
    with open(f'{resources_file}/plants.pkl', 'wb') as output:
        pickle.dump(return_details, output)
    # Add extra metadata to the database
    ExtraPlantData().main()
    with open(f'{resources_file}/plants.pkl', 'wb') as output:
        pickle.dump(return_details, output)


def check_success():
    none_dict = {}
    with open(f'{resources_file}/plants.pkl', 'rb') as f:
        d = pickle.load(f)
    for plant, values in d.items():
        for value in values.keys():
            if value not in none_dict:
                none_dict.update({value: 0})

    for plant, values in d.items():
        for key, value in values.items():
            if value is None:
                none_dict[key] += 1

    pp.pprint(none_dict)
    return none_dict


if __name__ == '__main__':
    return_details = ExtraPlantData().main()
    with open(f'{resources_file}/plants.pkl', 'wb') as output:
        pickle.dump(return_details, output)


# todo - Add None to new keys for plants that do not have values.
# Order the keys so it looks nicer.
