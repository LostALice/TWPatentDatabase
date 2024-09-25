# Code by AkinoAlice@Tyrant_Rex

from utility.handler.log_handler import Logger

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium import webdriver


class Scraper(object):
    def __init__(self, headless=True) -> None:
        self.options = webdriver.EdgeOptions()
        self.driver = webdriver.Edge(options=self.options)
        self.logger = Logger("./logging.log")

    # gether patent list
    def searching(self, search_string: str) -> list[WebElement]:
        self.driver.get("https://gpss2.tipo.gov.tw/gpsskmc/gpssbkm")
        title = self.driver.title
        self.logger.info(f"Scraping {title}", False)

        # search
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "_21_1_T"))
        )
        search_bar = self.driver.find_element(By.NAME, "_21_1_T")
        search_bar.send_keys(search_string)
        search_bar.send_keys(Keys.RETURN)

        # wait 10 seconds for web page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sumtr1"))
        )
        patents_list = self.driver.find_elements(By.CLASS_NAME, "sumtr1")

        target_url = []
        self.logger.debug(patents_list)
        self.logger.info([i.text for i in patents_list], True)
        for patents_row in patents_list:
            # /html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[6]/a
            # /html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr[3]

            target_url.append(patents_row.find_element(By.XPATH, f"./td[6]/a"))

        return target_url

    def stop_driver(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()
    scraper.searching("鞋面")
    scraper.stop_driver()
