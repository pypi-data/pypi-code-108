import time
from quick_crawler import page
from selenium import webdriver

def get_page_content_with_browser(url,chrome_driver_path):

    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    # set chromedriver.exe's path
    driver = webdriver.Chrome(executable_path=chrome_driver_path,
                              # chrome_options=options
                              )
    driver.implicitly_wait(0.5)
    # launch the page
    driver.get(url)

    html_obj = driver.find_element_by_tag_name("html")

    time.sleep(5)
    html_str=html_obj.get_attribute("outerHTML")
    from bs4 import BeautifulSoup
    # html = BeautifulSoup(html_obj.get_attribute("outerHTML"), features='lxml')
    # find elements
    # table_obj = driver.find_element_by_tag_name("table")
    # obtain target htmlstr
    # print(table_obj.get_attribute("outerHTML"))
    driver.close()
    return html_str

def get_country_list(chrome_driver="browsers/chromedriver.exe",read_countries_file="datasets/countries.csv", save_dataset_path="datasets"):
    # quick read csv file to a list of fields
    list_result = page.quick_read_csv(read_countries_file,
                                      fields=['Id', 'Url', 'English Name', 'French Name', 'Local Name', 'Region'])
    print(list_result)
    for country in list_result:
        id = country[0]
        url = country[1]
        print(url)
        html_str = get_page_content_with_browser(url,chrome_driver_path=chrome_driver)
        f_out = open(save_dataset_path, "w", encoding='utf-8')
        f_out.write(html_str)
        f_out.close()






