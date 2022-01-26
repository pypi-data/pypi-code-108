from flask import request

def webevidence(request):

    """!
    Get evidence from a web request (gets headers, cookies and query parameters)
    
    @type request: Request 
    @param request: A Request object
    @rtype dict
    @return A dictionary of web evidence that can be using in flowdata.evidence.add_from_dict()

    """

    webevidence = {}

    for header in request.headers:
        webevidence["header." + header[0].lower()] = header[1]

    for cookieKey, cookieValue in request.cookies.items():
        webevidence["cookie." + cookieKey] = cookieValue

    for query,value in request.args.items():

        webevidence["query." + query] = value
    
    webevidence["server.client-ip"] =  request.remote_addr

    webevidence["server.host-ip"] =  request.host

    if (request.is_secure):
        webevidence["header.protocol"] = "https"
    else:
        webevidence["header.protocol"] = "http"

    return webevidence

def set_response_header(flowData, response):
    
    """!
    Set UACH response header in web response (sets Accept-CH header in response)
    
    @type response: Response 
    @param response: A Response object
    @param response_header_dict: Dictionary containing response header key and values to be set
    @rtype response
    @return A response object containing headers with non null values in response

    """
    
    # Get response headers dictionary containing key values to be set in response  
    response_header_dict = flowData["set-headers"]["responseheaderdictionary"]
    for response_key, response_value in response_header_dict.items():
        response_value = response_value.replace(",", ", ")
        if response_value != "":
            response.headers[response_key] = response_value

    return response