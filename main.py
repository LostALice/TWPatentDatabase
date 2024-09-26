# Code by AkinoAlice@Tyrant_Rex

from utility.handler.log_handler import Logger

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

from utility.modal.patent import PatentInfo
from collections import defaultdict


class Scraper(object):
    def __init__(self, headless=True) -> None:
        self.options = webdriver.EdgeOptions()
        self.driver = webdriver.Edge(options=self.options)
        self.logger = Logger("./logging.log")

    def searching(self, search_string: str) -> list[str]:
        """Get list of patent

        Args:
            search_string (str): search string

        Returns:
            list[WebElement]: selenium web elements
        """
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
        for patents_row in patents_list:
            # /html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[6]/a
            # /html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr[3]

            patent_href = patents_row.find_element(
                By.XPATH, f"./td[6]/a").get_attribute("href")
            if patent_href:
                target_url.append(patent_href)

        # self.stop_driver()
        return target_url

    def element_scrape(self, page_url: str) -> PatentInfo:
        """get patent info form page element

        Args:
            element (WebElement): patent page

        Returns:
            PatentInfo: the information of patent info
        """
        # enter patent page
        self.driver.get(page_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/form/div[1]/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr/td[1]/div[2]/div[2]/table/tbody"))
        )

        # find information
        self.logger.info("Page loaded. Finding patent information...")
        patent_info_category = self.driver.find_elements(
            By.CLASS_NAME, "dettb01")
        patent_info_value = self.driver.find_elements(By.CLASS_NAME, "dettb02")

        # in chinese version
        # 申請日 ApplicationDate: int
        # 公開日 PublicationDate: int
        # 申請號 ApplicationNumber: str
        # 公開號 PublicationNumber: str
        # 申請人 Applicant: str
        # 發明人 Inventor: str
        # 代理人 Attorney: str
        # 優先權 Priority: str
        # 公報IPC GazetteIPC: str
        # IPC IPC: str
        # 公報卷期 GazetteVolume: str
        # 類別碼 KindCodes: str

        patent_dict = defaultdict(str)
        for category, value in zip(patent_info_category, patent_info_value):
            patent_dict[category.text] = value.text

        patent_info = PatentInfo(
            ApplicationDate=int(patent_dict["申請日"]),
            PublicationDate=int(patent_dict["公開日"]),
            ApplicationNumber=patent_dict["申請號"],
            PublicationNumber=patent_dict["公開號"],
            Applicant=patent_dict["申請人"],
            Inventor=patent_dict["發明人"],
            Attorney=patent_dict["代理人"],
            Priority=patent_dict["優先權"],
            GazetteIPC=patent_dict["公報IPC"],
            IPC=patent_dict["IPC"],
            GazetteVolume=patent_dict["公報卷期"],
            KindCodes=patent_dict["類別碼"],
        )
        self.logger.info(patent_info, True)
        WebDriverWait(self.driver, 1)
        return patent_info

    def stop_driver(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()
    webpage_elements = scraper.searching("鞋面")
    for web_element in webpage_elements:
        scraper.element_scrape(web_element)
    scraper.stop_driver()
