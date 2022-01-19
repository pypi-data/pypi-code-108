import requests

async def paper_request(type: str, url: str):
    base_url = "https://papermc.io/api/v2/"

    headers = {
        "accept": "application/json"
    }
    try:
        r = requests.request(method = type, url = f"{base_url}{url}", headers = headers)
    except requests.exceptions.RequestException:
        return "Err: requests.RequestException; There was an ambiguous exception that occurred while handling your request"
    except requests.exceptions.ConnectionError:
        return "Err: requests.ConnectionError; A Connection error occurred"
    except requests.exceptions.HTTPError:
        return "Err: requests.HTTPError; An HTTP error occurred"
    except requests.exceptions.URLRequired:
        return "Err: requests.URLRequired; A valid URL is required to make a request"
    except requests.exceptions.TooManyRedirects:
        return "Err: requests.TooManyRedirects; Too many redirects"
    except requests.exceptions.ConnectTimeout:
        return "Err: requests.ConnectTimeout; The request timed out while trying to connect to the remote server"
    except requests.exceptions.ReadTimeout:
        return "Err: requests.ReadTimeout; The server did not send any data in the allotted amount of time"
    except:
        return "Err: Unknown; An unknown error has occured"
    #except requests.Timeout:
    #    return "Err: requests.Timeout; The request timed out."
    return r.json()
