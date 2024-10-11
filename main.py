# Code by AkinoAlice@Tyrant_Rex

from utility.handler.log import Logger

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

from utility.handler.database import DatabaseOperator
from utility.modal.patent import PatentInfo
from collections import defaultdict

from urllib.request import urlopen
from uuid import uuid4

import re


class Scraper(object):
    def __init__(self, page_load_strategy: str = "eager") -> None:
        self.options = webdriver.EdgeOptions()
        self.options.page_load_strategy = page_load_strategy

        self.driver = webdriver.Edge(options=self.options)

        self.logger = Logger(__name__)
        # disable following modules logging to warnings
        self.logger.set_module_level("selenium", "WARNING")
        self.logger.set_module_level("urllib3", "WARNING")

    def search(self, keyword: str) -> tuple[int, int]:
        self.driver.get("https://gpss2.tipo.gov.tw/gpsskmc/gpssbkm")
        self.keyword = keyword
        self.logger.info(f"Searching {self.keyword}", False)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "_21_1_T"))
        )
        search_bar = self.driver.find_element(By.NAME, "_21_1_T")
        search_bar.send_keys(self.keyword)
        search_bar.send_keys(Keys.RETURN)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/font[2]/span[1]",
                )
            )
        )

        # counter
        self.total_patent_found = self.driver.find_element(
            By.XPATH,
            "/html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/font[1]",
        ).text.replace(",", "")
        self.total_page_found = self.driver.find_element(
            By.XPATH,
            "/html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/font[2]/span[2]",
        ).text.replace(",", "")

        if self.total_patent_found:
            self.total_patent = int(self.total_patent_found)
        else:
            self.total_patent = 0

        if self.total_page_found:
            self.total_page = int(self.total_page_found)
        else:
            self.total_page = 0

        return self.total_patent, self.total_page

    def get_patent_url(self, page: int = 1) -> list[str]:
        """Get list of patent

        Args:
            search_string (str): search string
            page (str): page number

        Returns:
            list[WebElement]: selenium web elements
        """
        self.driver.get("https://gpss2.tipo.gov.tw/gpsskmc/gpssbkm")
        self.logger.info(f"Scraping {self.driver.title} page:{page}", False)

        # search
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "_21_1_T"))
        )
        search_bar = self.driver.find_element(By.NAME, "_21_1_T")
        search_bar.send_keys(self.keyword)
        search_bar.send_keys(Keys.RETURN)

        # jump to page
        page_bar = self.driver.find_element(By.ID, "jpage")
        page_bar.send_keys(str(page))
        page_bar.send_keys(Keys.RETURN)

        # wait 10 seconds for web page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sumtr1"))
        )
        patents_list = self.driver.find_elements(By.CLASS_NAME, "sumtr1")

        target_url = []
        for patents_row in patents_list:
            # /html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[6]/a
            patent_href = patents_row.find_element(
                By.XPATH, f"./td[6]/a"
            ).get_attribute("href")
            if patent_href:
                target_url.append(patent_href)

        return target_url

    def get_patent_information(self, page_url: str, time_wait: int = 3) -> PatentInfo:
        """get patent info form page element

        Args:
            page_url  (str): patent page url
            time_wait (int): time wait for next page

        Returns:
            PatentInfo: the information of patent info
        """
        # enter patent page
        self.driver.get(page_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/form/div[1]/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr/td[1]/div[2]/div[2]/table/tbody",
                )
            )
        )

        # find patent information
        self.logger.info("Page loaded. Finding patent information...")
        patent_info_category = self.driver.find_elements(By.CLASS_NAME, "dettb01")
        patent_info_value = self.driver.find_elements(By.CLASS_NAME, "dettb02")

        # page in chinese version
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
        # URL URL: str

        patent_dict = defaultdict(str)
        for category, value in zip(patent_info_category, patent_info_value):
            patent_dict[category.text] = value.text
        patent_dict["URL"] = page_url

        # pdf file
        menu = self.driver.find_element(
            By.XPATH,
            "/html/body/form/div[1]/div/table/tbody/tr[3]/td/table/tbody/tr[1]/td/ul/li[2]",
        )
        pdf_element = self.driver.find_element(
            By.XPATH,
            "/html/body/form/div[1]/div/table/tbody/tr[3]/td/table/tbody/tr[1]/td/ul/li[2]/ul/li[2]/a",
        )

        # moving cursor
        ActionChains(self.driver).move_to_element(menu).perform()
        ActionChains(self.driver).move_to_element(pdf_element).key_down(
            Keys.CONTROL
        ).click().perform()
        self.logger.debug(f"Opening pdf: {page_url}")

        # switch window
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.logger.debug(f"Switched windows:{self.driver.window_handles[-1]}")

        # switch to iframe
        self.driver.switch_to.frame("LEFT")
        pdf_frameset = self.driver.find_element(
            By.XPATH,
            "/html/body/form/table/tbody/tr[6]/td/input",
        )
        pdf_frameset.click()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.logger.debug(f"Switched windows:{self.driver.window_handles[-1]}")

        # download pdf
        pdf_url = self.driver.current_url
        self.logger.info(f"Downloading pdf:{pdf_url}")
        pdf_file_name_regex_group = re.search(r"([A-Z]+-\d+)\.pdf", pdf_url)

        if pdf_file_name_regex_group:
            pdf_file_name = pdf_file_name_regex_group.group(1)
            patent_dict["PDFFilePath"] = f"./patent/{pdf_file_name}.pdf"
        else:
            patent_dict["PDFFilePath"] = f"./patent/{str(uuid4())}.pdf"

        try:
            pdf_file = urlopen(pdf_url)
            if "application/pdf" in pdf_file.info().get_content_type():
                with open(patent_dict["PDFFilePath"], "wb") as f:
                    f.write(pdf_file.read())
                WebDriverWait(self.driver, 5)
            else:
                self.logger.error("Failed to download PDF, content-type mismatch.")
        except Exception as e:
            self.logger.error(f"Error downloading PDF: {str(e)}")

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
            PatentURL=patent_dict["URL"],
            PatentFilePath=patent_dict["PDFFilePath"],
        )

        # clean up tabs
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])

        self.driver.implicitly_wait(time_wait)
        self.logger.info(patent_info, True)
        return patent_info

    def stop_driver(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()
    database = DatabaseOperator(
        database="PatentDatabase",
        user="postgres",
        password="example_password",
        host="localhost",
        port=5432,
    )

    total_patent, total_page = scraper.search("鞋面")
    for url in scraper.get_patent_url(page=1):
        patent_info = scraper.get_patent_information(url)
        database.inset_patent(patent_info)
    scraper.stop_driver()
