import requests
from bs4 import BeautifulSoup
import polars as pl
import yaml
import re
import logging
from typing import List, Optional, Any
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)

# global variables
RE_WHITE_SPACE = "\W+"
RE_SPEED = r'F/(\d+(?:\.\d+)?)'
RE_FOCAL = r'(\d+)mm'
SONY_URL = "https://lens-db.com/system/sony-e/"

@dataclass
class Lens:
    closest_focusing_distance: str
    filters: str
    lens_construction: str
    maximum_magnification: str
    original_name: str
    production_status: str
    system: str
    weight: str
    focusing_modes: str
    number_of_blades: Any

    # derived fields
    min_aperture: float = field(init=False)
    max_aperture: float = field(init=False)
    fixed_aperture: bool = field(init=False)
    min_focal_length: float = field(init=False)
    max_focal_length: float = field(init=False)
    is_prime: bool = field(init=False)
    is_zoom: bool = field(init=False)

    # due to inconsistency between descriptions, have to parse alternative features as well
    speed: Optional[str] = ""
    focal_length: Optional[str] = ""
    speed_range: Optional[str] = ""
    focal_length_range: Optional[str] = ""


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
        matches = re.findall(RE_SPEED, self.speed if self.speed != "" else self.speed_range)
        speed_ranges = [float(match) for match in matches]

        if len(speed_ranges) == 1:
            min = speed_ranges[0]
            max = speed_ranges[0]
            self.fixed_aperture = True
        elif len(speed_ranges) >= 2:
            min = speed_ranges[0]
            max = speed_ranges[1]
            self.fixed_aperture = False
        else:
            logging.error('Error parsing apertures; none found for %s',self.original_name)
        return (min, max)

    def get_focal_lengths(self) -> float:
        matches = re.findall(RE_FOCAL, self.focal_length if self.focal_length != "" else self.focal_length_range)
        focal_ranges = [int(match) for match in matches]
        if len(focal_ranges) == 1:
            min = focal_ranges[0]
            max = focal_ranges[0]
            self.is_prime = True
            self.is_zoom = False
        elif len(focal_ranges) >= 2:
            min = focal_ranges[0]
            max = focal_ranges[1]
            self.is_prime = False
            self.is_zoom = True
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

    lens = Lens(**lens_feature)

    df = pl.from_dict(lens.__dict__)
    return df



if __name__ == "__main__":
    # configs
    required_features = yaml.SafeLoader(open('config/features.yml')).get_data()
    feature_keys = required_features.get('specs')

    page = requests.get(SONY_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # logging.info('saving information from %s', SONY_URL)
    # with open('source/sony-lens.html', 'w') as f:
    #     f.write(soup.prettify())
    #     f.close

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
        logging.info('creating lens data for %s', lens.get('name'))
        logging.info('link: %s', lens.get('link'))
        link = lens.get('link')
        df_lens = parse_lens_link(lens_link = link)
        df_lenses = pl.concat([df_lenses, df_lens], how='vertical')

    df_lenses.to_pandas().to_parquet('outputs/lens.parquet')
