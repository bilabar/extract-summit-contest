import scrapy
from scrapy.selector import Selector


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://zzcvcpnfzoogpxiqupsergvrmdopqgrk-744852047878.us-south1.run.app/navigation"
    ]

    def parse(self, response):
        book_links = response.css("h3 a")
        for request in response.follow_all(book_links, callback=self.parse_book):
            request.meta["zyte_api_automap"] = {
                "httpResponseBody": True,
                "product": True,
                "productOptions": {"extractFrom": "httpResponseBody"},
            }
            yield request

    def parse_book(self, response):
        rp = response.raw_api_response["product"]
        selector = Selector(text=response.body)
        if "wayfair.com" in rp["canonicalUrl"]:
            name = rp["name"]
            rating = selector.xpath(
                "//p[@data-rtl-id='reviewsHeaderReviewsAverage']/text()"
            ).get()
            brand = selector.css(
                'div[data-rtl-id="listingManufacturerName"] a::text'
            ).get()
            sku = rp["sku"]
            price = (
                response.xpath(
                    '//span[@data-hb-id="BoxV3" and @data-test-id="PriceDisplay"]/text()'
                )
                .get()
                .strip("$")
            )
        elif "homedepot.com" in rp["canonicalUrl"]:
            name = selector.xpath(
                '//div[@class="product-details__badge-title--wrapper--vtpd5"]//h1/text()'
            ).get()
            brand = rp["brand"]["name"]
            rating = rp["aggregateRating"]["ratingValue"]
            sku = response.xpath(
                '//div[@class="sui-flex sui-text-xs sui-flex-wrap"]//h2[contains(text(), "Store SKU #")]//span/text()'
            ).get()
            price = rp["price"]
        else:
            name = rp["name"]
            rating = rp["aggregateRating"]["ratingValue"]
            brand = rp["brand"]["name"]
            sku = rp["sku"]
            price = rp["price"]

        yield {
            "url": rp["url"],
            "name": name,
            "brand": brand,
            "sku": sku,
            "price": price,
            "rating": float(rating),
            "reviews": rp["aggregateRating"]["reviewCount"],
        }
