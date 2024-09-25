#Code by AkinoAlice@Tyrant_Rex

from utility.handler.log_handler import Logger

from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.common.by import By # type: ignore

from selenium.common.exceptions import TimeoutException # type: ignore
from selenium import webdriver # type: ignore


class Scraper(object):
    def __init__(self, headless=True) -> None:
        self.options = webdriver.EdgeOptions()
        self.driver = webdriver.Edge(options=self.options)
        self.logger = Logger("./logging.log")

    # gether patent list
    def searching(self, search_string: str) -> None:
        self.driver.get("https://gpss2.tipo.gov.tw/gpsskmc/gpssbkm")
        title = self.driver.title
        self.logger.info(f"Scraping {title}", False)

        # search
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "_21_1_T")))
        search_bar = self.driver.find_element(By.NAME, "_21_1_T")
        search_bar.send_keys(search_string)
        search_bar.send_keys(Keys.RETURN)

        # wait 10 seconds for wait web page load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sumtr1")))
        patents_list = self.driver.find_elements(By.XPATH, "/html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr")
        for i in patents_list:
            print(i)

    def stop_driver(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()
    scraper.searching("A43B")
    scraper.stop_driver()
