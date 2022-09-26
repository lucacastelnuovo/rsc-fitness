import os
import json
import locale
import datetime
import requests
import scrapy
from scrapyscript import Job, Processor
from minio import Minio


class RscSpider(scrapy.spiders.Spider):
    name = "rsc"

    def start_requests(self):
        yield self.request()

    def request(self):
        url = "https://publiek.usc.ru.nl/publiek/laanbod.php?PRESET[Laanbod][inschrijving_id_pool_id][]=768114_2"

        body = {
            "PRESET[Laanbod][inschrijving_id_pool_id][]": "768114_2",
            "PRESET[Laanbod][where_naam_ibp][]": "pack=a%3A5%3A%7Bs%3A6%3A%22n.naam%22%3Bs%3A7%3A%22Fitness%22%3Bs%3A12%3A%22jlap.pool_id%22%3Bs%3A1%3A%222%22%3Bs%3A10%3A%22jlap.intro%22%3Bs%3A0%3A%22%22%3Bs%3A16%3A%22jlap.betaalwijze%22%3Bs%3A6%3A%22gratis%22%3Bs%3A10%3A%22jlap.prijs%22%3Bs%3A4%3A%220.00%22%3B%7D",
        }

        request = scrapy.FormRequest(
            url=url,
            method="POST",
            formdata=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (compatible; LucaBot/2.1; +https://lucacastelnuovo.nl)",
            },
            cookies={"publiek": self.cookie},
        )

        return request

    def parse(self, response):
        for row in response.xpath('//*[@class="responstable clickabletr"]//tr'):
            date = str(row.xpath("td[1]//text()").get()).strip()
            time = str(row.xpath("td[2]//text()").get()).strip()
            spots = str(row.xpath("td[4]//text()").get()).strip() or "55/55"

            if spots == "None":
                continue

            reservations = int(spots.split("/")[0])

            yield {"date": date, "time": time, "reservations": reservations}


def getAuthCookie():
    session = requests.Session()

    session.get("https://publiek.usc.ru.nl/publiek/login.php")
    session.post(
        "https://publiek.usc.ru.nl/publiek/login.php",
        data={
            "username": os.environ.get("RSC_USERNAME"),
            "password": os.environ.get("RSC_PASSWORD"),
        },
    )

    return session.cookies["publiek"]


def runScraper(authCookie):
    settings = scrapy.settings.Settings(values={"LOG_LEVEL": "WARNING"})

    processor = Processor(settings=settings)
    job = Job(RscSpider, cookie=authCookie)

    return processor.run(job)


def sortResults(results):
    slots = {}
    locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

    for result in results:
        date = datetime.datetime.strptime(result["date"], "%a %d %b %Y").strftime(
            "%Y-%m-%d"
        )

        if date in slots:
            slots[date].append([result["time"], result["reservations"]])
        else:
            slots[date] = [[result["time"], result["reservations"]]]

    return slots


def storeSlots(slots):
    with open("/app/data.json", "w", encoding="utf-8") as f:
        json.dump(slots, f, separators=(",", ":"))

    MINIO_CLIENT = Minio(
        "s3.castelnuovo.dev",
        os.environ.get("S3_ACCESS_KEY"),
        os.environ.get("S3_SECRET_KEY"),
    )

    MINIO_CLIENT.fput_object(
        "rsc.castelnuovo.dev",
        "data.json",
        "/app/data.json",
    )


def main():
    cookie = getAuthCookie()
    print(cookie)
    # results = runScraper(cookie)
    # slots = sortResults(results)

    # storeSlots(slots)


main()
