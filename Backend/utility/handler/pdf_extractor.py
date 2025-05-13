# Code by JaguarChou
# Code by AkinoAlice@TyrantRey

from pathlib import Path

import easyocr
import numpy as np
from pdf2image import convert_from_path

from Backend.utility.handler.log_handler import Logger

# 初始化 OCR 支援繁中+英文
reader = easyocr.Reader(["ch_tra", "en"])


class PAFExtractor:
    def __init__(
        self,
    ) -> None:
        self.logger = Logger().get_logger()

    def process(self, pdf_file_path: str, output_dir: str = "./outout") -> None:
        """
        Processes a PDF file to extract text and identify blank pages.

        This method converts each page of the input PDF to an image and applies OCR to extract text.
        If no text is detected on a page, the page is saved as a PNG image in a designated output directory.

        Args:
            pdf_file_path (str): The path to the input PDF file.
            output_dir (str, optional): The directory to save output files. Defaults to "./outout".

        Returns:
            None: This function does not return a value. It logs the processing information and saves output images and text.

        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        image_dir = Path(output_dir) / "blank_pages"
        Path(image_dir).mkdir(parents=True, exist_ok=True)

        self.logger.info("Start process pdf: %s", pdf_file_path)

        images = convert_from_path(pdf_file_path, dpi=300)

        all_text_output = ""

        for i, image in enumerate(images):
            page_num = i + 1
            self.logger.info("Processing Page: %s", page_num)

            ocr_result = reader.readtext(np.array(image), detail=0, paragraph=True)
            extracted_text = "\n".join(ocr_result).strip()

            if not extracted_text:
                img_filename = Path(image_dir) / f"page_{page_num:03}.png"
                image.save(img_filename)
                self.logger.warning("No words detected, saving image: %s", img_filename)
                extracted_text = "[此頁無偵測到文字]"

            all_text_output += f"\n--- Page {page_num} ---\n{extracted_text}\n"


if __name__ == "__main__":
    PAFExtractor().process("/Users/jaguar911121/Desktop/reporttest/TWAN-202500047.pdf")
