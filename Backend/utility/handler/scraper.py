# Code by AkinoAlice@Tyrant_Rex

import hashlib
import re
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

import requests  # type: ignore[import-untyped]
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from Backend.utility.error.scraper import HTTPUnexpectedSchemesError
from Backend.utility.handler.log_handler import Logger
from Backend.utility.model.handler.scraper import PatentImageInfoModel, PatentImageModel, PatentModel

# from utility.error.scraper import HTTPUnexpectedSchemesError
# from utility.handler.log_handler import Logger
# from utility.model.handler.scraper import PatentModel


class PatentScraper:
    """Scraper class for scraping Taiwan Patent Office's website."""

    def __init__(self, time_wait: int = 3) -> None:
        """
        Initialize the Scraper with the given page load strategy.

        Args:
            time_wait (int): page time wait in second. Defaults to 3.

        Returns:
            None

        """
        self.logger = Logger().get_logger()
        self.time_wait = time_wait

    def create_scraper(self) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.binary_location = "./Driver/chromedriver-win64/chromedriver.exe"
        self.driver = webdriver.Chrome()

    def search(self, keyword: str) -> tuple[int, int]:
        """
        Perform a search on Taiwan Patent Office's website.

        Args:
            keyword (str): keyword to search

        Returns:
            (int, int): total number of patents found and total number of pages found

        """
        self.driver.get("https://tiponet.tipo.gov.tw/gpss4/gpsskmc/gpssbkm")
        self.keyword = keyword
        self.logger.info("Start Searching: %s", keyword)

        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.NAME, "_21_1_T")))
        search_bar = self.driver.find_element(By.NAME, "_21_1_T")
        search_bar.send_keys(self.keyword)
        search_bar.send_keys(Keys.RETURN)

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/font[2]/span[1]",
                ),
            ),
        )

        # counter
        _total_patent_found = self.driver.find_element(
            By.XPATH,
            "/html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/font[1]",
        ).text.replace(",", "")
        _total_page_found = self.driver.find_element(
            By.XPATH,
            "/html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/font[2]/span[2]",
        ).text.replace(",", "")

        self.total_patent_found = int(_total_patent_found)
        self.total_page_found = int(_total_page_found)

        return self.total_patent_found, self.total_page_found

    def get_patent_url(self, page: int = 1) -> list[str]:
        """
        Get list of patent.

        Args:
            search_string (str): search string
            page (str): page number

        Returns:
            list[WebElement]: selenium web elements

        """
        self.driver.get("https://tiponet.tipo.gov.tw/gpss4/gpsskmc/gpssbkm")
        self.logger.info("Scraping: %s", self.driver.title)
        self.logger.info("Scraping Page: %s", page)

        # search
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.NAME, "_21_1_T")))
        search_bar = self.driver.find_element(By.NAME, "_21_1_T")
        search_bar.send_keys(self.keyword)
        search_bar.send_keys(Keys.RETURN)

        # jump to page
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.ID, "jpage")))
        page_bar = self.driver.find_element(By.ID, "jpage")
        page_bar.send_keys(str(page))
        page_bar.send_keys(Keys.RETURN)

        # wait 10 seconds for web page load
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "sumtr1")))
        patents_list = self.driver.find_elements(By.CLASS_NAME, "sumtr1")

        target_url = []
        for patents_row in patents_list:
            # /html/body/form/div[1]/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[6]/a
            patent_href = patents_row.find_element(By.XPATH, "./td[6]/a").get_attribute("href")
            if patent_href:
                target_url.append(patent_href)

        return target_url

    def get_patent_information(self, page_url: str) -> PatentModel:
        """
        Get patent info form page element.

        Args:
            page_url  (str): patent page url

        Returns:
            PatentModel: the information of patent info

        """
        # enter patent page
        self.driver.get(page_url)
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/form/div[1]/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr/td[1]/div[2]/div[2]/table/tbody",
                ),
            ),
        )

        # find patent information
        self.logger.info("Page loaded. Finding patent information...")
        patent_info_category = self.driver.find_elements(By.CLASS_NAME, "dettb01")
        patent_info_value = self.driver.find_elements(By.CLASS_NAME, "dettb02")
        patent_title = self.driver.find_elements(By.XPATH, "/html/body/form/div[1]/div/table/tbody/tr[1]/td[1]")[
            0
        ].text.replace("\n", "")

        # in chinese version
        # 名稱 Title: str
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
        ActionChains(self.driver).move_to_element(pdf_element).key_down(Keys.CONTROL).click().perform()
        self.logger.debug("Opening pdf: %s", page_url)

        # switch window
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.logger.debug("Switched windows: %s", self.driver.window_handles[-1])

        # switch to iframe
        self.driver.switch_to.frame("LEFT")
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/form/table/tbody/tr[6]/td/input",
                ),
            ),
        )
        pdf_frameset = self.driver.find_element(
            By.XPATH,
            "/html/body/form/table/tbody/tr[6]/td/input",
        )

        ActionChains(self.driver).move_to_element(pdf_frameset).key_down(Keys.CONTROL).click().perform()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.logger.debug("Switched windows: %s", self.driver.window_handles[-1])

        # wait redirect
        while not self.driver.current_url.endswith(".pdf"):
            WebDriverWait(self.driver, 1)

        pdf_url = self.driver.current_url
        self.logger.info(pdf_url)

        self.logger.info("Downloading pdf: %s", pdf_url)
        pdf_file_name_group = re.search(r"([A-Z]+-\d+)\.pdf", pdf_url)

        # download pdf
        if not pdf_file_name_group:
            self.logger.error("Failed to get PDF file name from URL.")
            self.pdf_file_name = "".join([c for c in pdf_url if re.match(r"\w", c)])
        else:
            self.pdf_file_name = pdf_file_name_group.group(1)

        patent_dict["PDFFilePath"] = f"./patent/{self.pdf_file_name}.pdf"
        pdf_save_path = Path(patent_dict["PDFFilePath"])

        if not pdf_url.startswith(("http", "https")):
            raise HTTPUnexpectedSchemesError(pdf_url)

        pdf_file = urlopen(pdf_url)  # noqa: S310

        if "application/pdf" in pdf_file.info().get_content_type():
            with Path.open(pdf_save_path, mode="wb") as f:
                f.write(pdf_file.read())
            WebDriverWait(self.driver, 5)
        else:
            self.logger.error("Failed to download PDF, content-type mismatch.")

        patent_info = PatentModel(
            Title=patent_title,
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
        self.driver.switch_to.window(self.driver.window_handles[0])

        self.driver.implicitly_wait(self.time_wait)
        self.logger.info(patent_info)
        return patent_info

    def get_patent_image(self, page_url: str) -> PatentImageInfoModel:
        self.driver.get(page_url)

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/form/div[1]/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr/td[1]/div[2]/div[2]/table/tbody",
                ),
            ),
        )

        a_tags = self.driver.find_elements(By.TAG_NAME, "a")
        patent_image_links: list[str] = []
        for a_tag in a_tags:
            a_tag_href = a_tag.get_attribute("href")
            if not a_tag_href:
                continue

            patent_image_links.extend(
                a_tag_href for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"] if a_tag_href.endswith(ext)
            )

        self.logger.info(patent_image_links)
        patent_image_dir = Path(f"./patent_image/{self.pdf_file_name}")
        if not patent_image_dir.exists():
            patent_image_dir.mkdir(parents=True, exist_ok=True)

        downloaded_hashes = set()
        image_list: list[PatentImageModel] = []
        for img_idx, link in enumerate(patent_image_links, 1):
            try:
                response = requests.get(link, timeout=self.time_wait)
                if response.ok:
                    img_bytes = response.content
                    img_hash = hashlib.sha256(img_bytes).hexdigest()

                    if img_hash in downloaded_hashes:
                        self.logger.warning("Image duplicate: %s", link)
                        continue

                    downloaded_hashes.add(img_hash)

                    img = Image.open(BytesIO(img_bytes)).convert("RGB")
                    image_file_path = patent_image_dir / f"{img_idx}.png"
                    img.save(image_file_path, format="PNG")
                    self.logger.info("Image saved: %s", image_file_path)
                    image_list.append(PatentImageModel(image_path=str(image_file_path), page=img_idx))

                else:
                    self.logger.critical("Image download fail: %s", link)
            except Exception as e:
                msg = f"Image error: {e}"
                self.logger.exception(msg)

        patent_image_info = PatentImageInfoModel(patent_serial=self.pdf_file_name, image_list=image_list)
        self.logger.info(patent_image_info)
        return patent_image_info

    def destroy_scraper(self) -> None:
        """Stop the driver."""
        self.driver.quit()


Scraper = PatentScraper()

if __name__ == "__main__":
    # database_config = DatabaseConfig(
    #     host="localhost",
    #     port=5432,
    #     username="root",
    #     password="password",
    #     database="patent_database",
    # )
    # database = Database(config=database_config, debug=True)
    total_patent, total_page = Scraper.search("鞋面")
    # for page_number in range(1, total_page):
    for page_number in range(1, 2):
        for url in Scraper.get_patent_url(page=page_number):
            patent_data = Scraper.get_patent_information(url)
            Scraper.get_patent_image(url)
    #         database.insert_patent(patent_data)

    Scraper.destroy_scraper()
