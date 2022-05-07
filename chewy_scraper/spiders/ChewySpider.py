import scrapy
import json
import re
count = 1
class ChewySpider(scrapy.Spider):
    name = 'Chewy'
    start_urls= ['https://www.chewy.com/b/adult-11098']
  
    def parse(self, response):
        yield from response.follow_all(css="a.kib-product-image", callback=self.parse_product)
        next_page_link = response.css("a.kib-pagination-new-item--next::attr(href)").get()
        if next_page_link is not None:
            yield response.follow(next_page_link, callback=self.parse)
    
    def parse_product(self, response):
        global count
        count = count + 1
        print(count)
        title = response.css("div[id=product-title] h1::text").get()
        if title is None:
            title = response.css("h1._1I125sScbDIKrqDtOwiNEP::text").get()
            if title is None:
                print("title missing")
                print(response.url)
        if title is not None:
            title = title.strip()
        brand = response.css("div[id=product-subtitle] a span::text").get()
        if brand is None:
            brand = response.css("span._2nUyiqZtP6R5xwWK9zZQLO a::text").get()
            if brand is None:
                print("brand missing")
                print(response.url)
        reviews = response.css("a[data-ga-label=review-anchor]::text").get()
        if reviews is None:
            reviews = response.css("button._32qwAKraBTqYU31ifxREJq._2eag2j6Va8Fd3r5gzBXww-::text").get()
            if reviews is None:
                reviews = response.css("a.js-write-first-review::text").get()
                if reviews is not None:
                    reviews = '0'
        if reviews is None:
            print("reviews missing")
            print(response.url)
        else:
            reviews = reviews.strip()
        # categories = response.css("a.kib-breadcrumbs-item__link::text").getall()
        # if len(categories) == 0:
        #     categories = response.css("a.bc-link span::text").getall()
        #     if len(categories) == 0:
        #         print("missing categories")
        #         print(response.url)
       
        attr = response.xpath("//div[@id='vue-portal__sfw-attribute-buttons']/@data-attributes").get()
        price_map = {}
        if attr is None:
            attr = response.xpath("//script/text()").re_first('window.__APOLLO_STATE__\s*=\s*"(\{.*?\})";')
            if attr is not None:
                attr = json.loads(attr.replace('\\\"', '"').replace('\\\\', '\\'))
                num2label = {}
                num2price = {}
                for k in attr:
                    if k.startswith('AttributeValue'):
                        num2label[str(attr[k]['id'])] = attr[k]['value']
                    if k.startswith('Item:'):
                        if  len(attr[k]['attributeValues({"usage":["DEFINING"]})']) > 0:
                            num2price[attr[k]['attributeValues({"usage":["DEFINING"]})'][0]['__ref'][15:]] = attr[k]['advertisedPrice']
                for k in num2label:
                    price_map[num2label[k]] = num2price[k]
            if len(price_map) == 0:
                price_map = response.xpath("//span[has-class('ga-eec__price')]/text()").get()
                if price_map is None:
                    price_map = response.xpath("//*[@data-testid='advertised-price']/text()").get()
                if price_map is None:
                    print(response.url)
                else:
                    price_map = price_map.strip()
        else:
            tmp = {}
            attr = json.loads(attr)
            attr = attr[0]['attributeValues']
            for it in attr:
                tmp[it['id']] = it['value']
            item_map = response.xpath('//script/text()').re_first("var\s*variationsItemMap\s*=\s*(\{.*?\})\n").strip()
            item_data = response.xpath("//script/text()").re_first("var\s*itemData\s*=\s*(\{[\s\S]*?\});").strip()
            item_map = json.loads(item_map)
            keys = re.findall("'(\d*)'\s*:", item_data)
            prices = re.findall("price: '\$(\d*\.\d*)'", item_data)
            for i, it in enumerate(keys):
                price_map[tmp[item_map[it][0]]] = prices[i]
        yield {
            'name': title,
            'categories': ['a', 'b'],
            'brand': brand,
            'reviews': reviews,
            'prices': price_map
        }