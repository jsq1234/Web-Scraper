import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from halo import Halo


class Scraper:
    url = 'https://hprera.nic.in/PublicDashboard'
    project_rows_query = '//div[@id="tab_project_main-filtered-data"]//div[@class="form-row"]'
    project_links_query = '//a[@onclick="tab_project_main_ApplicationPreview($(this));"]'
    menu_table_query = '//div[@id="project-menu-html"]//table'
    close_button_query = '//div[@id="modal-data-display-tab_project_main"]//div[@class="modal-header"]//button[@class="close"]'

    def __init__(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_project_name(self):
        return [item.get_attribute('innerHTML') for item in WebDriverWait(self.driver, 30).until(
            expected_conditions.presence_of_all_elements_located(
                (By.XPATH,
                 f'{self.project_rows_query}//span[@class="font-lg fw-600"]')
            )
        )]

    def scrape(self, N):
        self.driver.get(self.url)

        spinner = Halo(text='Getting projects', spinner='dots3')
        spinner.start()
        project_rows = self.get_project_rows()
        project_names = self.get_project_name()
        links = self.get_links(project_rows, N)
        spinner.stop()

        print("")

        list = []
        idx = 0
        for link in tqdm(links):
            link.click()

            table = self.get_menu_table()
            pan_no = self.get_table_item(table, "PAN No.")
            gstin_no = self.get_table_item(table, "GSTIN No.")
            name = self.get_table_item(table, "Name")
            permanent_address = self.get_table_item(table, "Permanent Address")

            self.get_close_button().click()

            data_dict = {
                'Project Name': project_names[idx],
                'Name': name,
                'PAN No.': pan_no,
                'GSTIN No.': gstin_no,
                'Permanent Address': permanent_address
            }

            list.append(data_dict)

            idx += 1
        self.driver.close()
        df = pd.DataFrame(list)
        return df

    def get_project_rows(self):
        return WebDriverWait(self.driver, 30).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, self.project_rows_query)
            )
        )

    def get_links(self, project_rows, N):
        """Returns 5 project links that is used to open the modal"""
        return project_rows.find_elements(By.XPATH, self.project_links_query)[:N]

    def get_menu_table(self):
        return WebDriverWait(self.driver, 30).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, self.menu_table_query)
            )
        )

    def get_close_button(self):
        return self.driver.find_element(By.XPATH, self.close_button_query)

    def get_table_item(self, table, item) -> str:
        # Name isn't in a span but directly in td, therefore we only need
        # span only in other cases
        return table.find_element(
            By.XPATH,
            f'//td[normalize-space() = "{item}"]/following-sibling::td[1]{ "" if item == "Name" else "//span" }').get_attribute('innerText')


scraper = Scraper()
project_list_info = scraper.scrape(5)

print(project_list_info)
