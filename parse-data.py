"""
Models for lenses found in lens-db.com
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional


def convert_str_to_float(string_to_convert) -> float:
    float_from_str = float(string_to_convert)
    return float_from_str


@dataclass
class Lens:
    name: str

    min_aperture: Optional[float] = None
    max_aperture: Optional[float] = None
    min_focal = Optional[float] = None
    max_focal = Optional[float] = None
    brand = Optional[str] = None
    mount = Optional[str] = None
    date_of_manufacture = Optional[int] = None
    year: Optional[str] = None

    def __post__init__(self):
        self.get_apertures()
        self.get_focals()

    @classmethod
    def get_focals(self):
        re_focal = "\d+\wmm"
        focals = [focal for focal in self.name if re.match(re_focal, self.name)]
        no_focals = len(focals)

        if no_focals >= 2:
            logging.warn(
                "Error parsing focals - more than two found. Keeping only the first two %s from full list",
                "\n".join(focals),
            )
            max_focal = focals[1]
            min_focal = focals[0]
        elif no_focals == 1:
            logging.info("Fixed focal found for %s, using %s", self.name, "".join(focals))
            max_focal = focals[0]
            max_focal = focals[1]
        else:
            logging.warn("Error parsing focals; none found %s", self.name)

        self.min_focal = convert_str_to_float(min_focal)
        self.max_focal = convert_str_to_float(max_focal)

    @classmethod
    def get_apertures(self):
        re_aperture = "(f|F)\w+\2f"
        apertures = [aperture for aperture in self.name if re.match(re_aperture, self.name)]
        no_apertures = len(apertures)

        if no_apertures >= 2:
            logging.warn(
                "Error parsing apertures - more than two found. Keeping only the first two %s from full list",
                "\n".join(apertures),
            )
            max_aperture = apertures[1]
            min_aperture = apertures[0]
        elif no_apertures == 1:
            logging.info("Fixed aperture found for %s, using %s", self.name, "".join(apertures))
            max_aperture = apertures[0]
            max_aperture = apertures[1]
        else:
            logging.warn("Error parsing apertures; none found %s", self.name)

        self.min_aperture = convert_str_to_float(min_aperture)
        self.max_aperture = convert_str_to_float(max_aperture)
