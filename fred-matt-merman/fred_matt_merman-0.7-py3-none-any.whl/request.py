import requests

def request(url):
    
    try:
        
        request = requests.get(url)
        check = request.status_code
    
        if check != 200: return -1
    
    except requests.ConnectionError: return -1
        
    return request
    
    
def get(url_base, url_key, type, id):
            
    url = ""
    
    if type == "category_children": url = url_base + "category/children?category_id=" + id + url_key
            
    elif type == "series": url = url_base + "category/series?category_id=" + str(id) + url_key
    
    elif type == "observation": url = url_base + "series/observations?series_id=" + id + url_key
        
    return request(url)