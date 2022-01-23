import time
from selenium import webdriver
from bs4 import BeautifulSoup
from quick_crawler import page

def get_coutries_list(chrome_driver_path,save_path="datasets/countries.csv",temp_html_file="datasets/html.txt"):
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    # set chromedriver.exe's path
    driver = webdriver.Chrome(executable_path=chrome_driver_path,
                              # chrome_options=options
                              )
    driver.implicitly_wait(0.5)
    # launch the page
    driver.get("https://www.nationsonline.org/oneworld/countries_of_the_world.htm")

    html_obj = driver.find_element_by_tag_name("html")
    f_out = open(temp_html_file, "w", encoding='utf-8')
    f_out.write(html_obj.get_attribute("outerHTML"))
    f_out.close()

    time.sleep(10)

    html = BeautifulSoup(html_obj.get_attribute("outerHTML"), features='lxml')
    # find elements
    # table_obj = driver.find_element_by_tag_name("table")
    # obtain target htmlstr
    # print(table_obj.get_attribute("outerHTML"))

    tables = html.findAll("table")

    print(tables)

    driver.close()

    list_model = []
    for table in tables:
        trs = table.findAll("tr")
        for tr in trs:
            # print(tr)
            list_v = []
            for idx, td in enumerate(tr.findAll("td")):

                if idx == 0:
                    flag = td.find("div", {"class": "flag"})
                    if flag == None:
                        break
                    id = flag["id"]

                    list_v.append(id)
                elif idx == 1:
                    if td.find("a") == None:
                        break
                    href = td.find("a")["href"]
                    list_v.append('https://www.nationsonline.org/oneworld/' + href)
                    list_v.append(td.text)
                else:
                    list_v.append(td.text)
            print(list_v)
            if len(list_v) < 5:
                continue
            model = {
                "Id": list_v[0],
                "Url": list_v[1],
                "English Name": page.quick_remove_unicode(list_v[2]),
                "French Name": page.quick_remove_unicode(list_v[3]),
                "Local Name": page.quick_remove_unicode(list_v[4]),
                "Region": page.quick_remove_unicode(list_v[5])
            }
            list_model.append(model)

    page.quick_save_csv(save_path, ['Id', 'Url', 'English Name', 'French Name', 'Local Name', 'Region'], list_model)




