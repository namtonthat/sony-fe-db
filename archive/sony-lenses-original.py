import scrapy
import re

# from scrapy.loader import ItemLoader
# from spiderSony import lensItem


class sony(scrapy.Spider):
    name = "sony"

    start_urls = [
        'https://www.sony.com/electronics/lenses/t/camera-lenses?cameramount=e-mount'
    ]

    def parse(self, response):
        allurls = response.xpath('//div[@class="product-name-wrap"]/a[@itemtype="http://schema.org/Product"]').css('a::attr(href)').getall()
        # add http: tag - add in 'specifications' - remove convertors
        noConverters = [i for i in list(set(allurls)) if not re.findall('converters', i)]
        specurls     = ["http:" + i + "/specifications" for i in noConverters]
        # cleanurls    = ["http:" + i for i in noConverters]

        for productURL in specurls:
            yield scrapy.Request(productURL, callback = self.parse_spec)

    #  functions to determine features
    def isSteadyShot(self, specDict):
        try:
            if specDict['Image stabilization (SteadyShot)'] == "Optical SteadyShot™":
                return "Y"
            else:
                return "N"
        except KeyError:
            return "N"

    def isFullFrame(self, specDict):
        if specDict['Format'] == "35 mm full frame":
            return "Y"
        else:
            return "N"

    def isVariable(self, filteredList):
        if len(filteredList) == 2:
            return filteredList[1]
        else:
            return filteredList[0]

    # get the image url
    def getImage(self, response):
        imageSource     = response.xpath('//div[@data-mode="imageGallery"]/div/div/div/img/@data-src-desktop').get()
        imageURL        = "http:" + imageSource
        return imageURL

    def parse_spec(self, response):

        spec            = response.xpath('//div[@class="grid no-grid-at-567 spec-section"]/div/dl/dd/text()').getall()
        specHeadings    = response.xpath('//div[@class="grid no-grid-at-567 spec-section"]/div/dl/dt/strong/text()').getall()
        specDict        = dict(zip(specHeadings, specs))
        productName     = response.xpath('//a[@class="primary-link l3 breadcrumb-link"]/@title').get()
        price           = response.xpath('//p[@itemtype="http://schema.org/Offer"]/strong/text()').get()
        sku             = response.xpath('//span[@itemprop="model"]/text()').get()
        source          = str(response).strip('<200 ').strip('/specifications>')
        dimensions      = re.findall('\d+?.?\d+.x.\d+?.?\d+.mm', specDict['Dimensions (Diameter x Length)'])[0]
        elementGroups   = specDict["Lens Groups / Elements"]
        element         = re.findall('\d+', elementGroups)[1]
        group           = re.findall('\d+', elementGroups)[0]
        mountType       = specDict['Mount'].split("Sony ")[1]
        closeFocus      = specDict['Minimum Focus Distance']

        # finding focal lengths
        focalLengths    = re.findall('\d+', specDict['Focal Length (mm)'])
        minFocalLength  = focalLengths[0]
        maxFocalLength  = self.isVariable(focalLengths)

        # finding apertures
        maxApertures    = re.findall('\d?.?\d', specDict['Maximum aperture (F)'])
        maxSpeed        = maxApertures[0]
        minSpeed        = self.isVariable(maxApertures)

        imageURL        = scrapy.Request(source, callback = self.getImage)

        # yield results
        yield {
            'ProductName': productName
        }
