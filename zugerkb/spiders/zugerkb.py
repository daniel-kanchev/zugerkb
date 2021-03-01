import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from zugerkb.items import Article


class ZugerkbSpider(scrapy.Spider):
    name = 'zugerkb'
    start_urls = ['https://www.zugerkb.ch/private/anlegen-und-boerse/news-und-analysen']

    def parse(self, response):
        links = response.xpath('//a[text()="Mehr"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_pages = response.xpath('//ul[@class="pagination"]//a/@href').getall()
        yield from response.follow_all(next_pages, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//article//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="col-xs-6"]//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//p[@class="intro"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
