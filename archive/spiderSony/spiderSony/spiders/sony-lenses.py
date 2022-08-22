import scrapy
import re

from scrapy.loader import ItemLoader
from scrapy.http import Request
from spiderSony.items import lensItem
# logging errors
import logging
logging.basicConfig(filename='error.log',level=logging.ERROR)

class sonyItems(scrapy.Spider):
    name = "sonyItems"

    start_urls = [
        'https://www.sony.com/electronics/lenses/t/camera-lenses'
    ]

    def parse(self, response):

        allurls     = response.xpath('//div[@class="product-name-wrap"]/a[@itemtype="http://schema.org/Product"]').css('a::attr(href)').getall()
        # add http: tag - add in 'specifications' - remove convertors
        urlLinks    = ["http:" + i for i in list(set(allurls))]
        # apply filters to the specifications
        rmConverters= [urlLink for urlLink in urlLinks if (not re.findall('converters', urlLink))]
        rmTC        = [urlLink for urlLink in rmConverters if (not re.findall('tc', urlLink))]
        rmSAL       = [urlLink for urlLink in rmTC if (not re.findall('sal', urlLink))]

        # only keep e mount lens
        eMountLinks = rmSAL

        for productURL in eMountLinks:
            yield scrapy.Request(productURL, callback = self.parse_imageURL)


    def isVariable(self, filteredList):
        if len(filteredList) == 2:
            # return second value
            return filteredList[1]
        else:
            # return the first value
            return filteredList[0]

    # get the image url
    def parse_imageURL(self, response):
        imageDiv        = response.xpath('//div[@data-mode="imageGallery"]/div/div/div/img/@data-src-desktop').get()
        imageSource     = "http:" + imageDiv
        specSource      = str(response).strip('<200 ').strip('>') + '/specifications'
        print(specSource)

        yield scrapy.Request(specSource, self.parse_spec, meta = {'imageSource': imageSource})

    def parse_spec(self, response):
        # generate dictionary of
        specValues      = response.xpath('//div[@class="grid no-grid-at-567 spec-section"]/div/dl/dd/text()').getall()
        specKeys        = response.xpath('//div[@class="grid no-grid-at-567 spec-section"]/div/dl/dt/strong/text()').getall()
        specDict        = dict(zip(specKeys, specValues))

        productName     = response.xpath('//a[@class="primary-link l3 breadcrumb-link"]/@title').get()
        fullFrame       = specDict.get('Format')
        listPrice       = response.xpath('//p[@itemtype="http://schema.org/Offer"]/strong/text()').get()
        SKU             = response.xpath('//span[@itemprop="model"]/text()').get()

        # lens specs from specDict
        weightValue     = specDict.get('Weight')

        # find the metric value
        if not re.findall('\d+ g', weightValue):
            weight      = weightValue
        else:
            weight      = re.findall('\d+ g', weightValue)[0].split('g')[0].strip()


        dimensions      = specDict.get('Dimensions (Diameter x Length)')
        # dimensions      = re.findall('\d+?.?\d+?.x.\d+?.?\d+.mm', specDict['Dimensions (Diameter x Length)'])[0]
        # diameter        = dimensions.split(' x ')[0]
        # length          = dimensions.split(' x ')[1].split('mm')[0].strip()

        groupsElements  = specDict.get("Lens Groups / Elements")
        # element         = re.findall('\d+', groupsElements)[1]
        # group           = re.findall('\d+', groupsElements)[0]

        mount           = specDict['Mount'].split("Sony ")[1]
        closeFocus      = specDict.get('Minimum Focus Distance')
        apertureBlades  = specDict.get('Aperture Blades')
        frontFilter     = specDict.get('Filter Diameter (mm)')

        # finding focal lengths
        focalLengths    = re.findall('\d+', specDict['Focal Length (mm)'])
        minFocalLength  = focalLengths[0]
        maxFocalLength  = self.isVariable(focalLengths)

        # finding apertures
        maxApertures    = re.findall('\d?\.?\d', specDict['Maximum aperture (F)'])
        maxSpeed        = maxApertures[0]
        minSpeed        = self.isVariable(maxApertures)

        magnification   = specDict.get('Maximum Magnification ratio (x)')
        oss             = specDict.get('Image stabilization (SteadyShot)')

        # sources
        source          = str(response).strip('<200 ').strip('/specifications>')
        imageSource     = response.meta['imageSource']

        # load items into item
        l            = lensItem(
            productName     = productName
            ,mount          = mount
            ,fullFrame      = fullFrame
            ,listPrice      = listPrice
            ,sku            = SKU
            ,weight         = weight
            ,minFocalLength = minFocalLength
            ,maxFocalLength = maxFocalLength
            ,maxSpeed       = maxSpeed
            ,minSpeed       = minSpeed
            ,dimensions     = dimensions
            ,focus          = "AF"
            ,frontFilter    = frontFilter
            ,magnification  = magnification
            ,apertureBlades = apertureBlades
            ,groupsElements = groupsElements
            ,source         = source
            ,imageSource    = imageSource
        )



        yield l
