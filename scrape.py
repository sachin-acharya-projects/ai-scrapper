from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

SBR_WEBDRIVER = os.getenv("SBR_WEBDRIVER")


def scrape_website(website: str):
    print("Connecting to Scraping Browser...")
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, "goog", "chrome")

    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        print(f"Connected! Navigating to {website}...")
        driver.get(website)

        print("Taking page screenshot to file page.png")
        driver.get_screenshot_as_file("./page.png")

        print("Waiting captcha to solve...")
        solve_res = driver.execute(
            "executeCdpCommand",
            {"cmd": "Captcha.waitForSolve", "params": {"detectTimeout": 10000}},
        )
        print("Captcha solve status:", solve_res["value"]["status"])

        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html


def extract_body_content(html_content: str):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body

    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content: str):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content


def split_dom_content(dom_content: str, max_length: int = 6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
