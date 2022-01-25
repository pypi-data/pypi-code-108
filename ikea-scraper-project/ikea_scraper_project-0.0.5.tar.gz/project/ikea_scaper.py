from scraper import Scraper


print('This scraper has returned the sofa samples from Ikea. The data is presented in a json file')
ikea = Scraper()
ikea.accept_cookies()
ikea.navigate_to_items()
ikea.get_links()
ikea.extract_info()
ikea.upload_images
ikea.check_dict()
ikea.download_info()
ikea.upload_to_cloud()

