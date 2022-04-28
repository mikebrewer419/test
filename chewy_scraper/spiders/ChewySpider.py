from gc import callbacks
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
class ChewySpider(scrapy.Spider):
    name = 'Chewy'
    allowed_domains = ['www.chewy.com']
    start_urls = ['https://www.chewy.com/']
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 10
    }

    def __init__(self, category=None, *args, **kwargs):
        super(ChewySpider, self).__init__(*args, **kwargs)

    def parse(self,response):
        nav = response.xpath("//header[@id='chewy-global-header']/noscript/nav/ul")[1]
        yield from response.follow_all(nav.xpath("//li[count(*)=1]/a[starts-with(@href,'/b/')]"), callback=self.parseCategory)
    def parseCategory(self,response):
        yield from response.follow_all(xpath="//div[has-class('js-tracked-product-list')]/div[has-class('js-tracked-product')]/div[has-class('kib-product-card__canvas')]/a", callback=self.parseProduct)

    def parseProduct(self, response):
        name = response.xpath("//title/text()").get().split(" - ")[0]
        categories = response.xpath("//nav[has-class('kib-breadcrumbs')]/ol[has-class('kib-breadcrumbs__list')]/li[has-class('kib-breadcrumbs-item')]/a[has-class('kib-breadcrumbs-item__link')]/text()").getall()
        brand = response.xpath("//div[@data-testid='product-title']/span/a/text()").get()
        price = response.xpath("//div[@data-testid='advertised-price']/text()").get()
        reviews = response.xpath("//*[re:test(text(), '\d* Reviews$')]/text()").get()
        yield {
            'name': name,
            'brand': brand,
            'categories': categories,
            'price': price,
            'reviews': reviews
        }
    