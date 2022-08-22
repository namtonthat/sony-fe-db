# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags

class lensItem(scrapy.Item):
    # define the fields for your item here like:
    productName     = scrapy.Field()
    mount           = scrapy.Field()
    sku             = scrapy.Field()
    weight          = scrapy.Field()
    minFocalLength  = scrapy.Field()
    maxFocalLength  = scrapy.Field()
    maxSpeed        = scrapy.Field()
    minSpeed        = scrapy.Field()
    dimensions      = scrapy.Field()
    # diameter        = scrapy.Field()
    # length          = scrapy.Field()
    focus           = scrapy.Field()
    frontFilter     = scrapy.Field()
    magnification   = scrapy.Field()
    closeFocus      = scrapy.Field()
    oss             = scrapy.Field()
    apertureBlades  = scrapy.Field()
    groupsElements  = scrapy.Field()
    releaseDate     = scrapy.Field()
    listPrice       = scrapy.Field()
    fullFrame       = scrapy.Field()
    source          = scrapy.Field()
    imageSource     = scrapy.Field()
