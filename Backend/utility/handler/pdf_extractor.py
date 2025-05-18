# Code by JaguarChou
# Modify by AkinoAlice@TyrantRey

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import easyocr  # type: ignore[import-untyped]
import numpy as np
from pdf2image import convert_from_path

from Backend.utility.handler.log_handler import Logger

# from log_handler import Logger


class PDFExtractor:
    def __init__(self, max_workers: int = 3) -> None:
        """
        Initialize the PDFExtractor with configurable thread pool size.

        Args:
            max_workers (int, optional): Maximum number of worker threads.
                If None, uses default ThreadPoolExecutor size (typically CPU count).

        """
        self.logger = Logger().get_logger()
        self.reader = easyocr.Reader(["ch_tra", "en"])
        self.max_workers = max_workers
        self.lock = threading.Lock()

    def process_single_pdf(self, pdf_file_path: str, poppler_path: str, output_dir: str = "./pdf_output") -> str:
        """
        Process a single PDF file to extract text.

        Args:
            pdf_file_path (str): The path to the input PDF file.
            poppler_path (str): The poppler path
            output_dir (str, optional): The directory to save output files. Defaults to "./pdf_output".

        """
        self.logger.info("Start process pdf: %s", pdf_file_path)
        pdf_filename = pdf_file_path.split("/")[-1]
        pdf_file_id = pdf_filename.split("0")[0]
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        images = convert_from_path(pdf_file_path, dpi=300, poppler_path=poppler_path)

        all_text_output = ""

        for i, image in enumerate(images):
            page_num = i + 1
            with self.lock:
                self.logger.info("Processing %s Page: %s", pdf_file_id, page_num)

            ocr_result = self.reader.readtext(np.array(image), detail=0, paragraph=True)
            extracted_text = "\n".join(ocr_result).strip()

            all_text_output += f"\n--- Page {page_num} ---\n{extracted_text}\n"

        # Save the extracted text to a file
        output_text_path = Path(output_dir) / f"{pdf_file_id}.txt"
        with Path.open(output_text_path, "w", encoding="utf-8") as f:
            f.write(all_text_output)

        self.logger.info("Finish processing %s", pdf_filename)
        return str(output_text_path)

    def process_multiple(
        self, pdf_file_paths: list, poppler_path: str, output_dir: str = "./pdf_output"
    ) -> dict[str, str | None]:
        """
        Process multiple PDF files in parallel using thread-based parallelism.

        Args:
            pdf_file_paths (list): List of paths to PDF files.
            poppler_path (str): The poppler path.
            output_dir (str, optional): The directory to save output files. Defaults to "./pdf_output".

        Returns:
            dict: Dictionary mapping PDF file paths to their respective output text file paths.

        """
        results: dict[str, str | None] = {pdf_path: None for pdf_path in pdf_file_paths}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures_to_pdfs = {
                executor.submit(self.process_single_pdf, pdf_path, poppler_path, output_dir): pdf_path
                for pdf_path in pdf_file_paths
            }

            # Process results outside the loop
            try:
                for future in as_completed(futures_to_pdfs):
                    pdf_path = futures_to_pdfs[future]
                    try:
                        output_path = future.result()
                        results[pdf_path] = output_path
                    except Exception as e:
                        msg = f"Error processing {pdf_path}: {e!r}"
                        self.logger.exception(msg)
            except Exception as e:
                msg = f"Error in parallel processing: {e!r}"
                self.logger.exception(msg)

        return results

    def process(self, pdf_file_path: str, poppler_path: str, output_dir: str = "./pdf_output") -> str:
        """
        Process a single PDF file (maintained for backwards compatibility).

        Args:
            pdf_file_path (str): The path to the input PDF file.
            poppler_path (str): The poppler path
            output_dir (str, optional): The directory to save output files. Defaults to "./pdf_output".

        """
        return self.process_single_pdf(pdf_file_path, poppler_path, output_dir)


if __name__ == "__main__":
    extractor = PDFExtractor(max_workers=3)  # Using 3 worker threads
    pdf_list = ["./patent/TWAN-202509128.pdf", "./patent/TWAN-202510764.pdf", "./patent/TWAN-202510765.pdf"]

    poppler_path = r"D:\Tools\Poppler-windows\Release-24.08.0-0\poppler-24.08.0\Library\bin"

    # Process PDFs in parallel
    results = extractor.process_multiple(pdf_list, poppler_path)

    # Display results
    for pdf_path, output_path in results.items():
        if output_path:
            print(f"Successfully processed {pdf_path} -> {output_path}")  # noqa: T201
        else:
            print(f"Failed to process {pdf_path}")  # noqa: T201
