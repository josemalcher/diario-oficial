# -*- coding: utf-8 -*-
from dateparser import parse
import datetime as dt

import scrapy

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class SpCampinasSpider(BaseGazetteSpider):
    TERRITORY_ID = "3509502"
    name = "sp_campinas"
    allowed_domains = ["campinas.sp.gov.br"]
    start_urls = ["http://www.campinas.sp.gov.br/diario-oficial/index.php"]
    sp_campinas_url = "http://www.campinas.sp.gov.br/"
    selector_url = (
        "http://www.campinas.sp.gov.br/diario-oficial/index.php?mes={}&ano={}"
    )

    def parse(self, response):
        """
        @url http://www.campinas.sp.gov.br/diario-oficial/index.php
        @returns requests 4
        """
        today = dt.date.today()
        next_year = today.year + 1
        for year in range(2015, next_year):
            for month in range(1, 13):
                if year == today.year and month > today.month:
                    return

                url = self.selector_url.format(month, year)
                yield scrapy.Request(url, self.parse_month_page)

    def parse_month_page(self, response):
        """
        @url http://www.campinas.sp.gov.br/diario-oficial/index.php?mes=1&ano=2018
        @returns items 23 23
        @scrapes date file_urls is_extra_edition territory_id power scraped_at
        """
        items = []
        month_year = response.css(
            ".tabelaDiario:first-child tr th:nth-child(2)::text"
        ).extract_first()  # "janeiro 2018"
        links = response.css(".tabelaDiario:first-child tr td a")
        for link in links:
            url = link.css("::attr(href)").extract_first().replace("../", "")
            day = link.css("::text").extract_first()
            date = parse(f"{day} {month_year}", languages=["pt"]).date()
            url = f"{self.sp_campinas_url}{url}"
            is_extra_edition = False
            power = "executive_legislature"
            items.append(
                Gazette(
                    date=date,
                    file_urls=[url],
                    is_extra_edition=is_extra_edition,
                    territory_id=self.TERRITORY_ID,
                    power=power,
                    scraped_at=dt.datetime.utcnow(),
                )
            )
        return items
