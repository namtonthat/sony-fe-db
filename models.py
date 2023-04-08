"""
Basic Lens model generated from lens-db.com
"""

from dataclasses import dataclass
from typing import Optional, Any
import logging


@dataclass
class Lens:
    closest_focusing_distance: str
    filters: str
    lens_construction: str
    maximum_magnification: str
    optical_design: str
    original_name: str
    production_details: str
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

