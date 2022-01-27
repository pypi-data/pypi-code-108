import requests

def get_curriculum(settings):
    url = settings["mwc_site_url"] + "/index.json"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        raise IOError(f"Error getting curriculum from {url}.")
