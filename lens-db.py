import requests
from bs4 import BeautifulSoup
import polars as pl
import yaml
import re
import logging
from typing import List, Optional, Any
from dataclasses import dataclass

# global variables
RE_WHITE_SPACE = "\W+"
SONY_URL = "https://lens-db.com/system/sony-e/"




@dataclass
class Lens:
    closest_focusing_distance: str
    filters: str
    lens_construction: str
    maximum_magnification: str
    original_name: str
    production_status: str
    speed: str
    system: str
    weight: str
    focal_length: str
    focusing_modes: str
    number_of_blades: Any

    # derived fields
    min_aperture = Optional[float]
    max_aperture = Optional[float]
    min_focal_length = Optional[float]
    max_focal_length = Optional[float]
    is_prime = Optional[bool]
    is_zoom = Optional[bool]

    def __post_init__(self):
        self.min_aperture, self.max_aperture = self.get_apertures()
        self.min_focal_length, self.max_focal_length = self.get_focal_lengths()

    @property
    def filter_size(self) -> float:
        return self.filters.split('mm').split(' ')

    @property
    def min_focusing_distance(self) -> float:
        return self.closest_focusing_distance.strip('m [AF]')

    @property
    def no_of_blades(self) -> int:
        return int(self.number_of_blades.split(' ')[0])

    @property
    def is_autofocus(self) -> bool:
        has_autofocus = "auto" in self.focusing_modes.lower()
        return has_autofocus

    def get_apertures(self) -> float:
        apertures = self.speed.strip('F/').split('-')
        if len(apertures) == 1:
            min = float(apertures[0])
            max = float(apertures[0])
            self.is_zoom = False
        elif len(apertures) >= 2:
            min = float(apertures[0])
            max = float(apertures[1])
            self.is_zoom = True
        else:
            logging.error('Error parsing apertures; none found for %s',self.original_name)
        return (min, max)

    def get_focal_lengths(self) -> float:
        focal_length_nos = self.focal_length.strip('mm').split('-')
        if len(focal_length_nos) == 1:
            min = float(focal_length_nos[0])
            max = float(focal_length_nos[0])
            self.is_prime = True
        elif len(focal_length_nos) >= 2:
            min = float(focal_length_nos[0])
            max = float(focal_length_nos[1])
            self.is_prime = False
        else:
            logging.error('Error parsing focal lengths; none found for %s',self.original_name)

        return (min, max)


def camel_to_snake(name: str) -> str:
    "Rename strings to camelcase"
    name = name.replace(' ', '_')
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "")

def get_lens_model(full_lens_name: str) -> List[str]:
    "Parse the raw text and split into the name, model and filter size"
    pattern = r'^(.*?)\s*\[(.*?)\](?:.*⌀(\d+))?'
    match = re.match(pattern, full_lens_name)

    if match:
        results = {}
        lens_name = match.group(1).strip()
        lens_model = match.group(2).strip()
        filter_size = match.group(3)
        if filter_size:
            filter_size = filter_size.strip()
        else:
            filter_size = None

        results['name']  = lens_name
        results['model'] = lens_model
        results['filter_size'] = filter_size

        return results

def clean_str_list(text: str) -> str:
    """
    Remove and parse \n from strings
    Used in conjunction
    """
    split_texts = text.strip().split('\n')
    cleaned_texts = []
    for split_text in split_texts:
        test_string = split_text.strip()
        is_white_space = re.match(RE_WHITE_SPACE, test_string)
        print(is_white_space)
        if is_white_space:
            pass
        else:
            cleaned_texts.append(test_string)

    return ' '.join(cleaned_texts).strip().strip(":")


def parse_lens_link(lens_link: str) -> pl.DataFrame:
    page = requests.get(lens_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    features = soup.find_all('td')
    features_cleaned = []
    for feature in features:
        cleaned_text = clean_str_list(feature.get_text())
        features_cleaned.append(cleaned_text)

    lens_feature = {}
    for feature_index, feature in enumerate(features_cleaned):
        if feature in feature_keys:
            feature_value = features_cleaned[feature_index + 1]
            feature_key = camel_to_snake(feature)
            lens_feature[feature_key] = feature_value

    df = pl.from_dict(Lens(**lens_feature).__dict__)
    return df



if __name__ == "__main__":
    # configs
    required_features = yaml.SafeLoader(open('config/features.yml')).get_data()
    feature_keys = required_features.get('specs')

    page = requests.get(SONY_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    logging.info('saving information from %s', SONY_URL)
    with open('source/sony-lens.html', 'w') as f:
        f.write(soup.prettify())
        f.close


    system_lenses = soup.find_all("td", {"class": "uk-table-expand"})

    lenses = []
    for lens in system_lenses:
        single_lens = {}
        lens_data = get_lens_model(lens.get_text())
        # should only have one link per lens and return the href element
        link = lens.find_all('a', href=True)[0]['href']

        single_lens['link'] = link
        single_lens = {**single_lens, **lens_data}
        lenses.append(single_lens)

    df_lenses = pl.DataFrame({})
    for lens in lenses:
        link = lens.get('link')
        df_lens = parse_lens_link(lens_link = link)
        pl.concat([df_lenses, df_lens], how='vertical')


