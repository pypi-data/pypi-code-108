#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

def get(code: int) -> dict:

    try:
        d_details = _responses[code]
    except KeyError:
        raise ValueError(f'Response code not found: {code}')

    return d_details


_responses = {

    # ---------------------------------------------------------------- #
    # Informational responses (100–199)

    100: {
        'title': 'Continue',
        'description': (
            'This interim response indicates that everything so far is OK '
            'and that the client should continue the request, '
            'or ignore the response if the request is already finished.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/100'
    },
    101: {
        'title': 'Switching Protocol',
        'description': (
            'This code is sent in response to an Upgrade request header '
            'from the client, and indicates the protocol '
            'the server is switching to.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/101'
    },
    102: {
        'title': 'Processing (WebDAV)',
        'description': (
            'This code indicates that the server has received '
            'and is processing the request, '
            'but no response is available yet.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Glossary/WebDAV'
    },
    103: {
        'title': 'Early Hints',
        'description': (
            'This status code is primarily intended to be used '
            'with the Link header, letting the user agent start '
            'preloading resources while the server prepares a response.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/103'
    },

    # ---------------------------------------------------------------- #
    # Successful responses (200–299)

    200: {
        'title': 'OK',
        'description': (
            'The request has succeeded. '
            'The meaning of the success depends on the HTTP method: ' 
            'GET: The resource has been fetched '
            'and is transmitted in the message body. '
            'HEAD: The representation headers are included '
            'in the response without any message body. '
            'PUT or POST: The resource describing the result of the action '
            'is transmitted in the message body. '
            'TRACE: The message body contains the request message '
            'as received by the server.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200'
    },
    201: {
        'title': 'Created',
        'description': (
            'The request has succeeded and '
            'a new resource has been created as a result. '
            'This is typically the response sent after POST requests, '
            'or some PUT requests.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/201'
    },
    202: {
        'title': 'Accepted',
        'description': (
            'The request has been received but not yet acted upon. '
            'It is noncommittal, since there is no way in HTTP to later send '
            'an asynchronous response indicating the outcome of the request. '
            'It is intended for cases where another process or server '
            'handles the request, or for batch processing.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202'
    },
    203: {
        'title': 'Non-Authoritative Information',
        'description': (
            'This response code means the returned meta-information '
            'is not exactly the same as is available from the origin server, '
            'but is collected from a local or a third-party copy. '
            'This is mostly used for mirrors or backups of another resource. '
            'Except for that specific case, '
            'the \'200 OK\' response is preferred to this status.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/203'
    },
    204: {
        'title': 'No Content',
        'description': (
            'There is no content to send for this request, '
            'but the headers may be useful. '
            'The user-agent may update its cached headers '
            'for this resource with the new ones.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/204'
    },
    205: {
        'title': 'Reset Content',
        'description': (
            'Tells the user-agent '
            'to reset the document which sent this request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/205'
    },
    206: {
        'title': 'Partial Content',
        'description': (
            'This response code is used when the Range header is sent '
            'from the client to request only part of a resource.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/206'
    },
    207: {
        'title': 'Multi-Status (WebDAV)',
        'description': (
            'Conveys information about multiple resources, '
            'for situations where multiple status codes might be appropriate.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Glossary/WebDAV'
    },
    208: {
        'title': 'Already Reported (WebDAV)',
        'description': (
            'Used inside a <dav:propstat> response element '
            'to avoid repeatedly enumerating the internal members '
            'of multiple bindings to the same collection.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Glossary/WebDAV'
    },
    218: {
        'title': 'This is fine (Apache Web Server)',
        'description': (
            'Used as a catch-all error condition for allowing response bodies '
            'to flow through Apache when ProxyErrorOverride is enabled. '
            'When ProxyErrorOverride is enabled in Apache, '
            'response bodies that contain a status code of 4xx or 5xx '
            'are automatically discarded by Apache in favor of '
            'a generic response or a custom response specified '
            'by the ErrorDocument directive.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#218'
    },
    226: {
        'title': 'IM Used (HTTP Delta encoding)',
        'description': (
            'The server has fulfilled a GET request for the resource, '
            'and the response is a representation of the result '
            'of one or more instance-manipulations '
            'applied to the current instance.'
        ),
        'link': 'https://datatracker.ietf.org/doc/html/rfc3229'
    },

    # ---------------------------------------------------------------- #
    # Redirects (300–399)

    300: {
        'title': 'Multiple Choice',
        'description': (
            'The request has more than one possible response. '
            'The user-agent or user should choose one of them. '
            '(There is no standardized way of choosing one of the responses, '
            'but HTML links to the possibilities '
            'are recommended so the user can pick.)'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/300'
    },
    301: {
        'title': 'Moved Permanently',
        'description': (
            'The URL of the requested resource has been changed permanently. '
            'The new URL is given in the response.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301'
    },
    302: {
        'title': 'Found',
        'description': (
            'This response code means that the URI of requested resource '
            'has been changed temporarily. '
            'Further changes in the URI might be made in the future. '
            'Therefore, this same URI should be used '
            'by the client in future requests.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/302'
    },
    303: {
        'title': 'See Other',
        'description': (
            'The server sent this response to direct the client '
            'to get the requested resource at another URI with a GET request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/303'
    },
    304: {
        'title': 'Not Modified',
        'description': (
            'This is used for caching purposes. '
            'It tells the client that the response has not been modified, '
            'so the client can continue to use '
            'the same cached version of the response.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/304'
    },
    305: {
        'title': 'Use Proxy',
        'description': (
            'Defined in a previous version of the HTTP specification to '
            'indicate that a requested response must be accessed by a proxy. '
            'It has been deprecated due to security concerns '
            'regarding in-band configuration of a proxy.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status'
    },
    306: {
        'title': 'unused',
        'description': (
            'This response code is no longer used; it is just reserved. '
            'It was used in a previous version of the HTTP/1.1 specification.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status'
    },
    307: {
        'title': 'Temporary Redirect',
        'description': (
            'The server sends this response to direct the client '
            'to get the requested resource at another URI '
            'with same method that was used in the prior request. '
            'This has the same semantics as the 302 Found HTTP response code, '
            'with the exception that the user agent '
            'must not change the HTTP method used: '
            'If a POST was used in the first request, '
            'a POST must be used in the second request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/307'
    },
    308: {
        'title': 'Permanent Redirect',
        'description': (
            'This means that the resource is now permanently located '
            'at another URI, specified by the Location: HTTP Response header. '
            'This has the same semantics as '
            'the 301 Moved Permanently HTTP response code, '
            'with the exception that the user agent must not change '
            'the HTTP method used: '
            'If a POST was used in the first request, '
            'a POST must be used in the second request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/308'
    },

    # ---------------------------------------------------------------- #
    # Client errors (400–499)

    400: {
        'title': 'Bad Request',
        'description': (
            'The server could not understand the request '
            'due to invalid syntax.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400'
    },
    401: {
        'title': 'Unauthorized',
        'description': (
            'Although the HTTP standard specifies \"unauthorized\", '
            'semantically this response means \"unauthenticated\". '
            'That is, the client must authenticate itself '
            'to get the requested response.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401'
    },
    402: {
        'title': 'Payment Required',
        'description': (
            'This response code is reserved for future use. '
            'The initial aim for creating this code '
            'was using it for digital payment systems, '
            'however this status code is used very rarely '
            'and no standard convention exists.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402'
    },
    403: {
        'title': 'Forbidden',
        'description': (
            'The client does not have access rights to the content; '
            'that is, it is unauthorized, '
            'so the server is refusing to give the requested resource. '
            'Unlike 401, the client\'s identity is known to the server.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403'
    },
    404: {
        'title': 'Not Found',
        'description': (
            'The server can not find the requested resource. '
            'In the browser, this means the URL is not recognized. '
            'In an API, this can also mean that the endpoint is valid '
            'but the resource itself does not exist. '
            'Servers may also send this response instead of 403 '
            'to hide the existence of a resource from an unauthorized client. '
            'This response code is probably the most famous one '
            'due to its frequent occurrence on the web.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404'
    },
    405: {
        'title': 'Method Not Allowed',
        'description': (
            'The request method is known by the server '
            'but has been disabled and cannot be used. '
            'For example, an API may forbid DELETE-ing a resource. '
            'The two mandatory methods, GET and HEAD, '
            'must never be disabled and should not return this error code.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405'
    },
    406: {
        'title': 'Not Acceptable',
        'description': (
            'This response is sent when the web server, '
            'after performing server-driven content negotiation, '
            'doesn\'t find any content that conforms to '
            'the criteria given by the user agent.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/406'
    },
    407: {
        'title': 'Proxy Authentication Required',
        'description': (
            'This is similar to 401 '
            'but authentication is needed to be done by a proxy.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/407'
    },
    408: {
        'title': 'Request Timeout',
        'description': (
            'This response is sent on an idle connection by some servers, '
            'even without any previous request by the client. '
            'It means that the server would like to '
            'shut down this unused connection. '
            'This response is used much more since some browsers, '
            'like Chrome, Firefox 27+, or IE9, '
            'use HTTP pre-connection mechanisms to speed up surfing. '
            'Also note that some servers merely shut down the connection '
            'without sending this message.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408'
    },
    409: {
        'title': 'Conflict',
        'description': (
            'This response is sent when a request conflicts '
            'with the current state of the server.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409'
    },
    410: {
        'title': 'Gone',
        'description': (
            'This response is sent when the requested content '
            'has been permanently deleted from server, '
            'with no forwarding address. '
            'Clients are expected to remove their caches '
            'and links to the resource. '
            'The HTTP specification intends this status code '
            'to be used for \"limited-time, promotional services\". '
            'APIs should not feel compelled to indicate resources '
            'that have been deleted with this status code.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/410'
    },
    411: {
        'title': 'Length Required',
        'description': (
            'Server rejected the request because '
            'the Content-Length header field is not defined '
            'and the server requires it.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/411'
    },
    412: {
        'title': 'Precondition Failed',
        'description': (
            'The client has indicated preconditions in its headers '
            'which the server does not meet.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/412'
    },
    413: {
        'title': 'Payload Too Large',
        'description': (
            'Request entity is larger than limits defined by server; '
            'the server might close the connection '
            'or return an Retry-After header field.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/413'
    },
    414: {
        'title': 'URI Too Long',
        'description': (
            'The URI requested by the client is longer '
            'than the server is willing to interpret.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/414'
    },
    415: {
        'title': 'Unsupported Media Type',
        'description': (
            'The media format of the requested data is not supported by the server, '
            'so the server is rejecting the request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/415'
    },
    416: {
        'title': 'Range Not Satisfiable',
        'description': (
            'The range specified by the Range header field in the request '
            'can\'t be fulfilled; it\'s possible that the range '
            'is outside the size of the target URI\'s data.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/416'
    },
    417: {
        'title': 'Expectation Failed',
        'description': (
            'This response code means the expectation indicated '
            'by the Expect request header field can\'t be met by the server.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/417'
    },
    418: {
        'title': 'I\'m a teapot',
        'description': (
            'The server refuses the attempt '
            'to brew coffee with a teapot.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418'
    },
    419: {
        'title': 'Page Expired (Laravel Framework)',
        'description': (
            'Used by the Laravel Framework '
            'when a CSRF Token is missing or expired.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#419'
    },
    420: {
        'title': 'Method Failure (Spring Framework)',
        'description': (
            'A deprecated response used by the Spring Framework '
            'when a method has failed.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#420'
    },
    421: {
        'title': 'Misdirected Request',
        'description': (
            'The request was directed at a server '
            'that is not able to produce a response. '
            'This can be sent by a server that is not configured '
            'to produce responses for the combination '
            'of scheme and authority that are included in the request URI.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status'
    },
    422: {
        'title': 'Unprocessable Entity (WebDAV)',
        'description': (
            'The request was well-formed '
            'but was unable to be followed due to semantic errors.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422'
    },
    423: {
        'title': 'Locked (WebDAV)',
        'description': (
            'The resource that is being accessed '
            'is locked.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Glossary/WebDAV'
    },
    424: {
        'title': 'Failed Dependency (WebDAV)',
        'description': (
            'The request failed '
            'due to failure of a previous request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Glossary/WebDAV'
    },
    425: {
        'title': 'Too Early',
        'description': (
            'Indicates that the server is unwilling '
            'to risk processing a request that might be replayed.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/425'
    },
    426: {
        'title': 'Upgrade Required',
        'description': (
            'The server refuses to perform the request '
            'using the current protocol but might be willing to do so '
            'after the client upgrades to a different protocol. '
            'The server sends an Upgrade header in a 426 response '
            'to indicate the required protocol(s).'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/426'
    },
    428: {
        'title': 'Precondition Required',
        'description': (
            'The origin server requires the request to be conditional. '
            'This response is intended to prevent the \'lost update\' problem, '
            'where a client GETs a resource\'s state, '
            'modifies it, and PUTs it back to the server, '
            'when meanwhile a third party has modified the state on the server, '
            'leading to a conflict.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/428'
    },
    429: {
        'title': 'Too Many Requests',
        'description': (
            'The user has sent too many requests '
            'in a given amount of time (\"rate limiting\").'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429'
    },
    430: {
        'title': 'Request Header Fields Too Large (Shopify)',
        'description': (
            'Used by Shopify, '
            'instead of the 429 Too Many Requests response code, '
            'when too many URLs are requested within a certain time frame.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes'
    },
    431: {
        'title': 'Request Header Fields Too Large',
        'description': (
            'The server is unwilling to process the request '
            'because its header fields are too large. '
            'The request may be resubmitted '
            'after reducing the size of the request header fields.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/431'
    },
    440: {
        'title': 'Login Time-out (Microsoft IIS)',
        'description': (
            'The client\'s session has expired '
            'and must log in again.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#440'
    },
    444: {
        'title': 'No Response (nginx)',
        'description': (
            'Used internally to instruct the server to return '
            'no information to the client and close the connection immediately.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#444'
    },
    449: {
        'title': 'Retry With (Microsoft IIS)',
        'description': (
            'The server cannot honour the request '
            'because the user has not provided the required information.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#449'
    },
    450: {
        'title': 'Blocked by Windows Parental Controls (Microsoft)',
        'description': (
            'The Microsoft extension code indicated '
            'when Windows Parental Controls are turned on and '
            'are blocking access to the requested webpage.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#450'
    },
    451: {
        'title': 'Unavailable For Legal Reasons',
        'description': (
            'The user-agent requested a resource '
            'that cannot legally be provided, '
            'such as a web page censored by a government.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/451'
    },
    460: {
        'title': '(AWS Elastic Load Balancer)',
        'description': (
            'Client closed the connection with the load balancer '
            'before the idle timeout period elapsed. '
            'Typically when client timeout is sooner '
            'than the Elastic Load Balancer\'s timeout.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#460'
    },
    463: {
        'title': '(AWS Elastic Load Balancer)',
        'description': (
            'The load balancer received an X-Forwarded-For request header '
            'with more than 30 IP addresses.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#463'
    },
    494: {
        'title': 'Request header too large (nginx)',
        'description': (
            'Client sent too large request '
            'or too long header line.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#494'
    },
    495: {
        'title': 'SSL Certificate Error (nginx)',
        'description': (
            'An expansion of the 400 Bad Request response code, '
            'used when the client has provided an invalid client certificate.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#495'
    },
    496: {
        'title': 'SSL Certificate Required (nginx)',
        'description': (
            'An expansion of the 400 Bad Request response code, '
            'used when a client certificate is required but not provided.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#496'
    },
    497: {
        'title': 'HTTP Request Sent to HTTPS Port (nginx)',
        'description': (
            'An expansion of the 400 Bad Request response code, '
            'used when the client has made a HTTP request to a port '
            'listening for HTTPS requests.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#497'
    },
    498: {
        'title': 'Invalid Token (Esri)',
        'description': (
            'Returned by ArcGIS for Server. '
            'Code 498 indicates an expired or otherwise invalid token.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#498'
    },
    499: {
        'title': 'Token Required (Esri) / Client Closed Request (nginx)',
        'description': (
            'Returned by ArcGIS for Server. '
            'Code 499 indicates that a token is required but was not submitted.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#499'
    },

    # ---------------------------------------------------------------- #
    # Server errors (500–599)

    500: {
        'title': 'Internal Server Error',
        'description': (
            'The server has encountered a situation '
            'it doesn\'t know how to handle.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500'
    },
    501: {
        'title': 'Not Implemented',
        'description': (
            'The request method is not supported by the server '
            'and cannot be handled. '
            'The only methods that servers are required to support '
            '(and therefore that must not return this code) are GET and HEAD.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/501'
    },
    502: {
        'title': 'Bad Gateway',
        'description': (
            'This error response means that the server, '
            'while working as a gateway to get a response needed '
            'to handle the request, got an invalid response.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502'
    },
    503: {
        'title': 'Service Unavailable',
        'description': (
            'The server is not ready to handle the request. '
            'Common causes are a server that is down for maintenance '
            'or that is overloaded. '
            'Note that together with this response, '
            'a user-friendly page explaining the problem should be sent. '
            'This responses should be used for temporary conditions '
            'and the Retry-After: HTTP header should, if possible, '
            'contain the estimated time before the recovery of the service. '
            'The webmaster must also take care about '
            'the caching-related headers '
            'that are sent along with this response, '
            'as these temporary condition responses s'
            'hould usually not be cached.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503'
    },
    504: {
        'title': 'Gateway Timeout',
        'description': (
            'This error response is given when the server '
            'is acting as a gateway and cannot get a response in time.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504'
    },
    505: {
        'title': 'HTTP Version Not Supported',
        'description': (
            'The HTTP version used in the request '
            'is not supported by the server.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/505'
    },
    506: {
        'title': 'Variant Also Negotiates',
        'description': (
            'The server has an internal configuration error: '
            'the chosen variant resource is configured '
            'to engage in transparent content negotiation itself, '
            'and is therefore not a proper end point '
            'in the negotiation process.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/506'
    },
    507: {
        'title': 'Insufficient Storage (WebDAV)',
        'description': (
            'The method could not be performed on the resource '
            'because the server is unable to store the representation needed '
            'to successfully complete the request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/507'
    },
    508: {
        'title': 'Loop Detected (WebDAV)',
        'description': (
            'The server detected an infinite loop '
            'while processing the request.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/508'
    },
    509: {
        'title': 'Bandwidth Limit Exceeded (Apache Web Server/cPanel)',
        'description': (
            'The server has exceeded the bandwidth '
            'specified by the server administrator; '
            'this is often used by shared hosting providers '
            'to limit the bandwidth of customers.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#509'
    },
    510: {
        'title': 'Not Extended',
        'description': (
            'Further extensions to the request are required '
            'for the server to fulfill it.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/510'
    },
    511: {
        'title': 'Network Authentication Required',
        'description': (
            'The 511 status code indicates '
            'that the client needs to authenticate to gain network access.'
        ),
        'link': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/511'
    },
    520: {
        'title': 'Web Server Returned an Unknown Error (Cloudflare)',
        'description': (
            'The origin server returned an empty, unknown, '
            'or unexplained response to Cloudflare.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#520'
    },
    521: {
        'title': 'Web Server Is Down (Cloudflare)',
        'description': (
            'Error 521 occurs when the origin web server '
            'refuses connections from Cloudflare. '
            'Security solutions at your origin '
            'may block legitimate connections '
            'from certain Cloudflare IP addresses.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#521'
    },
    522: {
        'title': 'Connection Timed Out (Cloudflare)',
        'description': (
            'Error 522 occurs when Cloudflare times out '
            'contacting the origin web server.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#522'
    },
    523: {
        'title': 'Origin Is Unreachable (Cloudflare)',
        'description': (
            'Cloudflare could not reach the origin server; for example, '
            'if the DNS records for the origin server are incorrect.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#523'
    },
    524: {
        'title': 'A Timeout Occurred (Cloudflare)',
        'description': (
            'Cloudflare was able to complete a TCP connection '
            'to the origin server, '
            'but did not receive a timely HTTP response.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#524'
    },
    525: {
        'title': 'SSL Handshake Failed (Cloudflare)',
        'description': (
            'Cloudflare could not negotiate a SSL/TLS handshake '
            'with the origin server.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#525'
    },
    526: {
        'title': 'Invalid SSL Certificate (Cloudflare)',
        'description': (
            'Cloudflare could not validate the SSL certificate '
            'on the origin web server. '
            'Also used by Cloud Foundry\'s gorouter.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#526'
    },
    527: {
        'title': 'Railgun Error (Cloudflare)',
        'description': (
            'Error 527 indicates an interrupted connection between Cloudflare '
            'and the origin server\'s Railgun server.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#527'
    },
    529: {
        'title': 'Site is overloaded (Qualys)',
        'description': (
            'Used by Qualys in the SSLLabs server testing API '
            'to signal that the site can\'t process the request.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#529'
    },
    530: {
        'title': 'Site is frozen (Pantheon) / [along with a 1xxx] (Cloudflare)',
        'description': (
            'Used by the Pantheon web platform '
            'to indicate a site that has been frozen due to inactivity.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#530'
    },
    561: {
        'title': 'Unauthorized (AWS Elastic Load Balancer)',
        'description': (
            'An error around authentication returned by a server '
            'registered with a load balancer. '
            'You configured a listener rule to authenticate users, '
            'but the identity provider (IdP) returned an error code '
            'when authenticating the user.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#561'
    },
    598: {
        'title': '(Informal convention) Network read timeout error',
        'description': (
            'Used by some HTTP proxies to signal a network read timeout '
            'behind the proxy to a client in front of the proxy.'
        ),
        'link': 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#598'
    }
}

# -------------------------------------------------------------------- #
