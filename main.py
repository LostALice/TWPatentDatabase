from utility.handler.log_handler import Logger
from selenium import webdriver


class Scraper(object):
    def __init__(self, headless=True) -> None:
        self.options = webdriver.EdgeOptions()
        self.driver = webdriver.Edge(options=self.options)

    def query(self, search_string: str) -> None:
        self.driver.get("https://gpss2.tipo.gov.tw/gpsskmc/gpssbkm")
        title = self.driver.title
        Logger.info(f"Scraping {title}")

    def stop_driver(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    Scraper().main()
