'''
creates dictionary of http status numbers, indicating the name of the status code
status codes taken from https://en.wikipedia.org/wiki/List_of_HTTP_status_codes



All HTTP response status codes are separated into five classes (or categories). The first digit of the status code defines the class of response. 
The last two digits do not have any class or categorization role. There are five values for the first digit:
* 1xx (Informational): The request was received, continuing process
* 2xx (Successful): The request was successfully received, understood and accepted
* 3xx (Redirection): Further action needs to be taken in order to complete the request
* 4xx (Client Error): The request contains bad syntax or cannot be fulfilled
* 5xx (Server Error): The server failed to fulfill an apparently valid request
'''

http_status_info = {
	# ==1xx Informational response==
	# An informational response indicates that the request was received and understood. It is issued on a provisional basis while request processing continues. 
	# It alerts the client to wait for a final response. The message consists only of the status line and optional header fields, and is terminated by an empty line. 
	# As the HTTP/1.0 standard did not define any 1xx status codes, servers ''must not'' send a 1xx response to an HTTP/1.0 compliant client except under experimental conditions.
	# <ref>{{cite web|title=10 Status Code Definitions|url=http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html|website=W3|accessdate=16 October 2015}}</ref>

	100: {
		'name':"Continue",
		'desc':"""
			: The server has received the request headers and the client should proceed to send the request body (in the case of a request for which a body needs to be sent; for example, a [[POST (HTTP)|POST]] request). Sending a large request body to a server after a request has been rejected for inappropriate headers would be inefficient. To have a server check the request's headers, a client must send <code>Expect: 100-continue</code> as a header in its initial request and receive a <code>100 Continue</code> status code in response before sending the body. If the client receives an error code such as 403 (Forbidden) or 405 (Method Not Allowed) then it shouldn't send the request's body. The response <code>417 Expectation Failed</code> indicates that the request should be repeated without the <code>Expect</code> header as it indicates that the server doesn't support expectations (this is the case, for example, of HTTP/1.0 servers).<ref>{{cite web|title=Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content - 5.1.1. Expect|url=https://tools.ietf.org/html/rfc7231#section-5.1.1|accessdate=27 September 2017}}</ref>
	"""},
	101: {
		'name':"Switching Protocols",
		'desc':"""
			: The requester has asked the server to switch protocols and the server has agreed to do so.<ref>{{cite web|title=101|url=http://httpstatus.es/101|website=httpstatus|accessdate=16 October 2015}}</ref>
	"""},
	102: {
		'name':"Processing",
		'desc':"""
			([[WebDAV]]; RFC 2518)
			: A WebDAV request may contain many sub-requests involving file operations, requiring a long time to complete the request. This code indicates that the server has received and is processing the request, but no response is available yet.<ref name="RFC_2518">{{cite IETF
			| title       = HTTP Extensions for Distributed Authoring – WEBDAV
			| rfc         = 2518
			| last1       = Goland
			| first1      = Yaronn
			| last2       = Whitehead
			| first2      = Jim
			| authorlink2 = Jim Whitehead (professor)
			| last3       = Faizi
			| first3      = Asad
			| last4       = Carter
			| first4      = Steve R.
			| last5       = Jensen
			| first5      = Del
			|date=February 1999
			| publisher   = [[Internet Engineering Task Force|IETF]]
			| accessdate  = October 24, 2009
			}}</ref> This prevents the client from timing out and assuming the request was lost.
	"""},
	103: [{
		'name':"Early Hints",
		'desc':"""
			(<nowiki>RFC 8297</nowiki>)
			:Used to return some response headers before final HTTP message.<ref name="RFC_8297">{{cite IETF
			| title       = An HTTP Status Code for Indicating Hints
			| rfc         = 8297
			| last1       = Oku
			| first1      = Kazuho
			| authorlink1 = Kazuho Oku
			|date=December 2017
			| publisher   = [[Internet Engineering Task Force|IETF]]
			| accessdate  = December 20, 2017
			}}</ref>
	"""},
		{
		'name':"Checkpoint",
		'desc':"""
			((part of ==Unofficial codes==))
			((The following codes are not specified by any standard.))
			:Used in the resumable requests proposal to resume aborted PUT or POST requests.<ref>{{cite web|url=http://code.google.com/p/gears/wiki/ResumableHttpRequestsProposal |title=ResumableHttpRequestsProposal |archive-url=https://web.archive.org/web/20151013212135/http://code.google.com/p/gears/wiki/ResumableHttpRequestsProposal |archive-date=October 13, 2015 |access-date=2017-03-08 |deadurl=yes |df= }}</ref>
	"""}],
	# ==2xx Success==
	# This class of status codes indicates the action requested by the client was received, understood and accepted.<ref name="iana_status_codes" />

	200: {
		'name':"OK",
		'desc':"""
			: Standard response for successful HTTP requests. The actual response will depend on the request method used. In a GET request, the response will contain an entity corresponding to the requested resource. In a POST request, the response will contain an entity describing or containing the result of the action.<ref name="RFC_2616">{{cite_IETF | title =  Hypertext Transfer Protocol -- HTTP/1.1 | rfc = 2616 |date=June 1999 | sectionname = 200 OK | section= 10.2.1 | publisher   = [[Internet Engineering Task Force|IETF]] | accessdate  = August 30, 2016 }}</ref>
	"""},
	201: {
		'name':"Created",
		'desc':"""
			: The request has been fulfilled, resulting in the creation of a new resource.<ref>{{cite web|last1=Stewart|first1=Mark|last2=djna|title=Create request with POST, which response codes 200 or 201 and content|url=https://stackoverflow.com/questions/1860645/create-request-with-post-which-response-codes-200-or-201-and-content|website=Stack Overflow|accessdate=16 October 2015}}</ref>
	"""},
	202: {
		'name':"Accepted",
		'desc':"""
			: The request has been accepted for processing, but the processing has not been completed. The request might or might not be eventually acted upon, and may be disallowed when processing occurs.<ref>{{cite web|title=202|url=http://httpstatus.es/202|website=httpstatus|accessdate=16 October 2015}}</ref>
	"""},
	203: {
		'name':"Non-Authoritative Information",
		'desc':"""
			(since HTTP/1.1)
			: The server is a transforming proxy (e.g. a ''[[Web accelerator]]'') that received a 200 OK from its origin, but is returning a modified version of the origin's response.<ref>{{cite web|title = RFC 7231, Section 6.3.4.|url = https://tools.ietf.org/html/rfc7231#section-6.3.4|website = |accessdate = }}</ref><ref>{{cite web|title = RFC 7230, Section 5.7.2.|url = https://tools.ietf.org/html/rfc7230#section-5.7.2}}</ref>
	"""},
	204: {
		'name':"No Content",
		'desc':"""
			: The server successfully processed the request and is not returning any content.<ref>{{cite web|last1=Simmance|first1=Chris|title=Server Response Codes And What They Mean|url=http://www.koozai.com/blog/analytics/server-response-codes-and-what-they-mean/|website=koozai|accessdate=16 October 2015}}</ref>
	"""},
	205: {
		'name':"Reset Content",
		'desc':"""
			: The server successfully processed the request, but is not returning any content. Unlike a 204 response, this response requires that the requester reset the document view.<ref>{{cite web|url=https://tools.ietf.org/html/rfc7231#section-6.3.6|title=IETF RFC7231 section 6.3.6. - 205 Reset Content|last1=|first=|last2=|date=|website=IETF.org|archive-url=|archive-date=|dead-url=|accessdate=6 September 2018}}</ref>
	"""},
	206: {
		'name':"Partial Content",
		'desc':"""
			(RFC 7233)
			: The server is delivering only part of the resource ([[byte serving]]) due to a range header sent by the client. The range header is used by HTTP clients to enable resuming of interrupted downloads, or split a download into multiple simultaneous streams.<ref>{{cite web|title=diff --git a/linkchecker.module b/linkchecker.module|url=https://www.drupal.org/files/issues/linkchecker-report-descriptions-2403161-1.patch|website=Drupal|accessdate=16 October 2015}}</ref>
	"""},
	207: {
		'name':"Multi-Status",
		'desc':"""
			(WebDAV; RFC 4918)
			: The message body that follows is by default an [[XML]] message and can contain a number of separate response codes, depending on how many sub-requests were made.<ref name="RFC_4918"/>
	"""},
	208: {
		'name':"Already Reported",
		'desc':"""
			(WebDAV; RFC 5842)
			: The members of a DAV binding have already been enumerated in a preceding part of the (multistatus) response, and are not being included again.
	"""},
	226: {
		'name':"IM Used",
		'desc':"""
			(RFC 3229)
			: The server has fulfilled a request for the resource, and the response is a representation of the result of one or more instance-manipulations applied to the current instance.<ref name="RFC_3229">{{cite IETF
			| title       = Delta encoding in HTTP
			| rfc         = 3229
			|date=January 2002
			| publisher   = [[Internet Engineering Task Force|IETF]]
			| accessdate  = February 25, 2011
			}}</ref>
	"""},
	# ==3xx Redirection==
	# This class of status code indicates the client must take additional action to complete the request. Many of these status codes are used in [[URL redirection]].<ref name="iana_status_codes" />
	# A user agent may carry out the additional action with no user interaction only if the method used in the second request is GET or HEAD. A user agent may automatically redirect a request. 
	# A user agent should detect and intervene to prevent cyclical redirects.
	# <ref>{{cite web|url=http://tools.ietf.org/html/rfc7231#section-6.4|title=Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content|website=IETF|accessdate=13 February 2016}}</ref>

	300: {
		'name':"Multiple Choices",
		'desc':"""
			: Indicates multiple options for the resource from which the client may choose (via [[content negotiation#Agent-driven|agent-driven content negotiation]]). For example, this code could be used to present multiple video format options, to list files with different [[filename extension]]s, or to suggest [[word-sense disambiguation]].<ref>{{cite web|title=300|url=http://httpstatus.es/300|website=httpstatus|accessdate=16 October 2015}}</ref>
	"""},
	301: {
		'name':"Moved Permanently",
		'desc':"""
			: This and all future requests should be directed to the given [[Uniform resource identifier|URI]].<ref>{{cite web|title=301|url=http://httpstatus.es/301|website=httpstatus|accessdate=16 October 2015}}</ref>
	"""},
	302: {
		'name':"Found",
		'desc':"""
			(Previously "Moved temporarily")]]
			: Tells the client to look at (browse to) another URL. 302 has been superseded by 303 and 307. This is an example of industry practice contradicting the standard. The HTTP/1.0 specification (<nowiki>RFC 1945</nowiki>) required the client to perform a temporary redirect (the original describing phrase was "Moved Temporarily"),<ref name="RFC_1945">{{cite IETF
			| title       = Hypertext Transfer Protocol – HTTP/1.0
			| rfc         = 1945
			| last1       = Berners-Lee
			| first1      = Tim
			| authorlink1 = Tim Berners-Lee
			| last2       = Fielding
			| first2      = Roy T.
			| authorlink2 = Roy Fielding
			| last3       = Nielsen
			| first3      = Henrik Frystyk
			| authorlink3 = Henrik Frystyk Nielsen
			|date=May 1996
			| publisher   = [[Internet Engineering Task Force|IETF]]
			| accessdate  = October 24, 2009
			}}</ref> but popular browsers implemented 302 with the functionality of a 303 See Other. Therefore, HTTP/1.1 added status codes 303 and 307 to distinguish between the two behaviours.<ref name="RFC7230-10">{{cite web
			| url = http://tools.ietf.org/html/rfc7231#section-6.4
			| title = Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content, Section 6.4
			| publisher = [[IETF]]
			| accessdate = June 12, 2014
			}}</ref> However, some Web applications and frameworks use the 302 status code as if it were the 303.<ref name="ruby-on-rails-ActionController-Redirecting-redirect_to">{{cite web
			| url = http://api.rubyonrails.org/classes/ActionController/Redirecting.html#method-i-redirect_to
			| title = Reference of method redirect_to in Ruby Web Framework "Ruby on Rails". It states: The redirection happens as a "302 Moved" header unless otherwise specified.
			| accessdate = June 30, 2012
			}}</ref>
	"""},
	303: {
		'name':"See Other",
		'desc':"""
			(since HTTP/1.1)
			: The response to the request can be found under another [[Uniform Resource Identifier|URI]] using the GET method. When received in response to a POST (or PUT/DELETE), the client should presume that the server has received the data and should issue a new GET request to the given URI.<ref>{{cite web|title=303|url=http://httpstatus.es/303|website=httpstatus|accessdate=16 October 2015}}</ref>
	"""},
	304: {
		'name':"Not Modified",
		'desc':"""
			(RFC 7232)
			: Indicates that the resource has not been modified since the version specified by the [[List of HTTP header fields#Request Headers|request headers]] If-Modified-Since or If-None-Match. In such case, there is no need to retransmit the resource since the client still has a previously-downloaded copy.<ref>{{Cite web|url=https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/304|title=304 Not Modified|website=Mozilla Developer Network|language=en-US|access-date=2017-07-06}}</ref>
	"""},
	305: {
		'name':"Use Proxy",
		'desc':"""
			(since HTTP/1.1)
			:The requested resource is available only through a proxy, the address for which is provided in the response. For security reasons, many HTTP clients (such as [[Firefox|Mozilla Firefox]] and [[Internet Explorer]]) do not obey this status code.<ref name="mozilla bugzilla bug 187996 comment 13">{{cite web | url = https://bugzilla.mozilla.org/show_bug.cgi?id=187996#c13 | title = Mozilla Bugzilla Bug 187996: Strange behavior on 305 redirect, comment 13 | date = March 3, 2003 | accessdate = May 21, 2009}}</ref>
	"""},
	306: {
		'name':"Switch Proxy",
		'desc':"""
			: No longer used. Originally meant "Subsequent requests should use the specified proxy."<ref>{{cite web
			|last=Cohen
			|first=Josh
			|title=HTTP/1.1 305 and 306 Response Codes
			|url=https://tools.ietf.org/html/draft-cohen-http-305-306-responses-00
			|publisher=HTTP Working Group
			}}</ref>
	"""},
	307: {
		'name':"Temporary Redirect",
		'desc':"""
			(since HTTP/1.1)
			: In this case, the request should be repeated with another URI; however, future requests should still use the original URI. In contrast to how 302 was historically implemented, the request method is not allowed to be changed when reissuing the original request. For example, a POST request should be repeated using another POST request.<ref name="SemanticsAndContent">{{cite web
			| url = https://tools.ietf.org/html/rfc7231#section-6.4.7
			| title = Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content, Section 6.4.7 307 Temporary Redirect
			| year = 2014
			| publisher=[[IETF]]
			| accessdate= September 20, 2014
			}}</ref>
	"""},
	308: {
		'name':"Permanent Redirect",
		'desc':"""
			(RFC 7538)
			: The request and all future requests should be repeated using another URI. 307 and 308 parallel the behaviors of 302 and 301, but ''do not allow the HTTP method to change''. So, for example, submitting a form to a permanently redirected resource may continue smoothly.<ref name="rfc7238">{{cite web
			| url = https://tools.ietf.org/html/rfc7538
			| title = The Hypertext Transfer Protocol Status Code 308 (Permanent Redirect)
			| date = April 2015
			| publisher = Internet Engineering Task Force
			| accessdate = 2015-04-06
			}}</ref>
	"""},
	# ==4xx Client errors==
	# [[File:Wikipedia Not Found Page.png|alt=A 404 error on Wikipedia.|thumb|404 error on Wikipedia]]
	# This class of status code is intended for situations in which the error seems to have been caused by the client. 
	# Except when responding to a HEAD request, the server ''should'' include an entity containing an explanation of the error situation, and whether it is a temporary or permanent condition. 
	# These status codes are applicable to any request method. User agents ''should'' display any included entity to the user.
	# <ref>{{cite web|title=E Explanation of Failure Codes|url=https://docs.oracle.com/cd/E14269_01/doc.451/e14266/result_codes.htm|website=Oracle|accessdate=16 October 2015}}</ref>

	400: {
		'name':"Bad Request",
		'desc':"""
			: The server cannot or will not process the request due to an apparent client error (e.g., malformed request syntax, size too large, invalid request message framing, or deceptive request routing).<ref name="rfc7231-400">{{cite web|url=https://tools.ietf.org/html/rfc7231#section-6.5.1 |title=RFC7231 on code 400|publisher=Tools.ietf.org|accessdate=January 8, 2015}}</ref>
	"""},
	401: {
		'name':"Unauthorized",
		'desc':"""
			(RFC 7235)
			: Similar to ''403 Forbidden'', but specifically for use when authentication is required and has failed or has not yet been provided. The response must include a WWW-Authenticate header field containing a challenge applicable to the requested resource. See [[Basic access authentication]] and [[Digest access authentication]].<ref>{{cite web|title=401|url=http://httpstatus.es/401|website=httpstatus|accessdate=16 October 2015}}</ref> 401 semantically means "unauthorised"<ref name="rfc7235-401">{{cite web|url=https://tools.ietf.org/html/rfc7235#section-3.1 |title=RFC7235 on code 401|publisher=Tools.ietf.org|accessdate=February 8, 2015}}</ref>, the user does not have valid authentication credentials for the target resource.
			: Note: Some sites incorrectly issue HTTP 401 when an [[IP address]] is banned from the website (usually the website domain) and that specific address is refused permission to access a website.
	"""},
	402: {
		'name':"Payment Required",
		'desc':"""
			: Reserved for future use. The original intention was that this code might be used as part of some form of [[digital cash]] or [[micropayment]] scheme, as proposed, for example, by [[GNU Taler]],<ref>{{Cite web|url=https://docs.taler.net/merchant/frontend/php/html/tutorial.html#Headers-for-HTTP-402|title=The GNU Taler tutorial for PHP Web shop developers 0.4.0|website=docs.taler.net|access-date=2017-10-29}}</ref> but that has not yet happened, and this code is not usually used. [[Google Developers]] API uses this status if a particular developer has exceeded the daily limit on requests.<ref name="GoogleDevelopersErrorCode">
			{{cite web
			| url = https://developers.google.com/doubleclick-search/v2/standard-error-responses#PAYMENT_REQUIRED
			| title = Google API Standard Error Responses
			| year = 2016
			| accessdate=June 21, 2017
			}}</ref> Sipgate uses this code if an account does not have sufficient funds to start a call.<ref>{{cite web|url=https://api.sipgate.com/v2/doc/#/sessions/newCall|title=Sipgate API Documentation|accessdate=July 10, 2018}}</ref> [[Shopify]] uses this code when the store has not paid their fees and is temporarily disabled.<ref>{{cite web|url=https://help.shopify.com/en/api/getting-started/response-status-codes|title=Shopify Documentation|accessdate=July 25, 2018}}</ref>
	"""},
	403: {
		'name':"Forbidden",
		'desc':"""
			: The request was valid, but the server is refusing action. The user might not have the necessary permissions for a resource, or may need an account of some sort. This code is also typically used if the request provided authentication via the WWW-Authenticate header field, but the server did not accept that authentication.
	"""},
	404: {
		'name':"Not Found",
		'desc':"""
			: The requested resource could not be found but may be available in the future. Subsequent requests by the client are permissible.
	"""},
	405: {
		'name':"Method Not Allowed",
		'desc':"""
			: A request method is not supported for the requested resource; for example, a GET request on a form that requires data to be presented via [[POST (HTTP)|POST]], or a PUT request on a read-only resource.
	"""},
	406: {
		'name':"Not Acceptable",
		'desc':"""
			: The requested resource is capable of generating only content not acceptable according to the Accept headers sent in the request.<ref>{{cite web|last1=Singh|first1=Prabhat|last2=user1740567|title=Spring 3.x JSON status 406 "characteristics not acceptable according to the request "accept" headers ()"|url=https://stackoverflow.com/questions/12865093/spring-3-x-json-status-406-characteristics-not-acceptable-according-to-the-requ|website=Stack Overflow|accessdate=16 October 2015}}</ref> See [[Content negotiation]].
	"""},
	407: {
		'name':"Proxy Authentication Required",
		'desc':"""
			(RFC 7235)
			:The client must first authenticate itself with the [[Proxy server|proxy]].<ref>{{cite web|title=407|url=http://httpstatus.es/407|website=httpstatus|accessdate=16 October 2015}}</ref>
	"""},
	408: {
		'name':"Request Timeout",
		'desc':"""
			: The server timed out waiting for the request. According to HTTP specifications: "The client did not produce a request within the time that the server was prepared to wait. The client MAY repeat the request without modifications at any later time."<ref>{{cite web|title=408|url=http://httpstatus.es/408|website=httpstatus|accessdate=16 October 2015}}</ref>
	"""},
	409: {
		'name':"Conflict",
		'desc':"""
			: Indicates that the request could not be processed because of conflict in the current state of the resource, such as an [[edit conflict]] between multiple simultaneous updates.
	"""},
	410: {
		'name':"Gone",
		'desc':"""
			: Indicates that the resource requested is no longer available and will not be available again. This should be used when a resource has been intentionally removed and the resource should be purged. Upon receiving a 410 status code, the client should not request the resource in the future. Clients such as search engines should remove the resource from their indices.<ref name="HTTP_410">
			{{cite web
			| url = https://www.youtube.com/watch?v=xp5Nf8ANfOw
			| title = Does Google treat 404 and 410 status codes differently? (Youtube)
			| year = 2014
			| accessdate=February 4, 2015
			}}</ref> Most use cases do not require clients and search engines to purge the resource, and a "404 Not Found" may be used instead.
	"""},
	411: {
		'name':"Length Required",
		'desc':"""
			: The request did not specify the length of its content, which is required by the requested resource.<ref>{{cite web|title=List of HTTP status codes|url=https://books.google.com/?id=J1gb2eb-NuEC&pg=PA197&lpg=PA197&dq=The+request+did+not+specify+the+length+of+its+content,+which+is+required+by+the+requested+resource.#v=onepage&q=The%20request%20did%20not%20specify%20the%20length%20of%20its%20content%2C%20which%20is%20required%20by%20the%20requested%20resource.&f=false|website=Google Books|accessdate=16 October 2015}}</ref>
	"""},
	412: {
		'name':"Precondition Failed",
		'desc':"""
			(RFC 7232)
			: The server does not meet one of the preconditions that the requester put on the request header fields.<ref>https://tools.ietf.org/html/rfc7232#section-4.2</ref> <ref>{{cite web|last1=Kowser|last2=Patel|first2=Amit|title=REST response code for invalid data|url=https://stackoverflow.com/questions/6123425/rest-response-code-for-invalid-data|website=Stack Overflow|accessdate=16 October 2015}}</ref>
	"""},
	413: {
		'name':"Payload Too Large",
		'desc':"""
			(RFC 7231)
			: The request is larger than the server is willing or able to process. Previously called "Request Entity Too Large".<ref>{{cite web|url=https://tools.ietf.org/html/rfc2616#section-10.4.14 |title=RFC2616 on status 413|publisher=Tools.ietf.org|accessdate=November 11, 2015}}</ref>
	"""},
	414: {
		'name':"URI Too Long",
		'desc':"""
			(RFC 7231)
			: The [[URI]] provided was too long for the server to process. Often the result of too much data being encoded as a query-string of a GET request, in which case it should be converted to a POST request.<ref>{{cite web|last1=user27828|title=GET Request - Why is my URI so long?|url=https://stackoverflow.com/questions/20157706/get-request-why-is-my-uri-so-long|website=Stack Overflow|accessdate=16 October 2015}}</ref> Called "Request-URI Too Long" previously.<ref>{{cite web|url=https://tools.ietf.org/html/rfc2616#section-10.4.15 |title=RFC2616 on status 414|publisher=Tools.ietf.org|accessdate=November 11, 2015}}</ref>
	"""},
	415: {
		'name':"Unsupported Media Type",
		'desc':"""
			(RFC 7231)
			: The request entity has a [[Internet media type|media type]] which the server or resource does not support.  For example, the client uploads an image as [[Scalable Vector Graphics|image/svg+xml]], but the server requires that images use a different format.<ref>{{cite web|url=https://tools.ietf.org/html/rfc7231#section-6.5.13 |title=RFC7231 on status 415|publisher=Tools.ietf.org|accessdate=May 2, 2019}}</ref>
	"""},
	416: {
		'name':"Range Not Satisfiable",
		'desc':"""
			(RFC 7233)
			: The client has asked for a portion of the file ([[byte serving]]), but the server cannot supply that portion. For example, if the client asked for a part of the file that lies beyond the end of the file.<ref>{{cite web|last1=Sigler|first1=Chris|title=416 Requested Range Not Satisfiable|url=http://getstatuscode.com/416|website=GetStatusCode|accessdate=16 October 2015|deadurl=yes|archiveurl=https://web.archive.org/web/20151022220744/http://getstatuscode.com/416|archivedate=October 22, 2015|df=mdy-all}}</ref> Called "Requested Range Not Satisfiable" previously.<ref>{{cite web|url=https://tools.ietf.org/html/rfc2616#section-10.4.17 |title=RFC2616 on status 416|publisher=Tools.ietf.org|accessdate=November 11, 2015}}</ref>
	"""},
	417: {
		'name':"Expectation Failed",
		'desc':"""
			: The server cannot meet the requirements of the Expect request-header field.<ref>{{cite web|last1=TheDeadLike|title=HTTP/1.1 Status Codes 400 and 417, cannot choose which|url=http://serverfault.com/questions/433470/http-1-1-status-codes-400-and-417-cannot-choose-which|website=serverFault|accessdate=16 October 2015}}</ref>
			<!-- The following code is under discussion on the talk page. Please discuss there before removing this entry. -->
	"""},
	418: {
		'name':"I'm a teapot",
		'desc':"""
			(RFC 2324, RFC 7168)
			:This code was defined in 1998 as one of the traditional [[Internet Engineering Task Force|IETF]] [[April Fools' Day RFC|April Fools' jokes]], in RFC 2324, ''[[Hyper Text Coffee Pot Control Protocol]]'', and is not expected to be implemented by actual HTTP servers.  The RFC specifies this code should be returned by teapots requested to brew coffee.<ref>{{cite IETF |rfc=2324 |author=Larry Masinter |date=1 April 1998 |title=Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0)|quote= Any attempt to brew coffee with a teapot should result in the error code "418 I'm a teapot". The resulting entity body MAY be short and stout.}}</ref> This HTTP status is used as an [[Easter egg (media)|Easter egg]] in some websites, including [[Google.com]].<ref>{{cite news |url=http://searchengineland.com/new-google-easter-egg-seo-geeks-server-status-418-im-teapot-201739 |author=Barry Schwartz |date=26 August 2014 |title=New Google Easter Egg For SEO Geeks: Server Status 418, I’m A Teapot |work=Search Engine Land }}</ref><ref>[https://www.google.com/teapot Google's Teapot]</ref>
	"""},
	421: {
		'name':"Misdirected Request",
		'desc':"""
			(RFC 7540)
			: The request was directed at a server that is not able to produce a response<ref >{{cite web
			| url = https://http2.github.io/http2-spec/#MisdirectedRequest
			| title = Hypertext Transfer Protocol version 2
			| authorlink1 = M. Belshe
			| authorlink2 = R. Peon
			| authorlink3 = M. Thomson, Editor
			|date=March 2015
			| accessdate  = April 25, 2015
			}}</ref>  (for example because of connection reuse).<ref >{{Cite web
			|title=9.1.1. Connection Reuse
			|date=May 2015
			|work=RFC7540
			|url=https://tools.ietf.org/html/rfc7540#section-9.1.1
			}}</ref>
	"""},
	422: {
		'name':"Unprocessable Entity",
		'desc':"""
			(WebDAV; RFC 4918)
			: The request was well-formed but was unable to be followed due to semantic errors.<ref name="RFC_4918">{{cite IETF
			| title       = HTTP Extensions for Web Distributed Authoring and Versioning (WebDAV)
			| rfc         = 4918
			| editor-last = Dusseault
			| editor-first = Lisa
			| editor-link =
			|date=June 2007
			| publisher   = [[Internet Engineering Task Force|IETF]]
			| accessdate  = October 24, 2009
			}}</ref>
	"""},
	423: {
		'name':"Locked",
		'desc':"""
			(WebDAV; RFC 4918)
			: The resource that is being accessed is locked.<ref name="RFC_4918"/>
	"""},
	424: {
		'name':"Failed Dependency",
		'desc':"""
			(WebDAV; RFC 4918)
			: The request failed because it depended on another request and that request failed (e.g., a PROPPATCH).<ref name="RFC_4918"/>
	"""},
	425: {
		'name':"Too Early",
		'desc':"""
			(RFC 8470)
			:Indicates that the server is unwilling to risk processing a request that might be replayed.
	"""},
	426: {
		'name':"Upgrade Required",
		'desc':"""
			: The client should switch to a different protocol such as [[Transport Layer Security|TLS/1.0]], given in the [[Upgrade header]] field.<ref>{{cite web|last1=Khare|first1=R|last2=Lawrence|first2=S|title=Upgrading to TLS Within HTTP/1.1|url=https://tools.ietf.org/html/rfc2817|website=IETF|publisher=Network Working Group|accessdate=16 October 2015}}</ref>
	"""},
	428: {
		'name':"Precondition Required",
		'desc':"""
			(RFC 6585)
			:The origin server requires the request to be conditional. Intended to prevent the 'lost update' problem, where a client GETs a resource's state, modifies it, and PUTs it back to the server, when meanwhile a third party has modified the state on the server, leading to a conflict.<ref name="rfc6585">{{cite web
			|url=http://tools.ietf.org/html/rfc6585
			|title=RFC 6585 – Additional HTTP Status Codes
			|first1=M.
			|last1=Nottingham
			|first2=R.
			|last2=Fielding
			|date=April 2012
			|work=Request for Comments
			|publisher=[[Internet Engineering Task Force]]
			|accessdate=May 1, 2012}}</ref>
	"""},
	429: {
		'name':"Too Many Requests",
		'desc':"""
			(RFC 6585)
			:The user has sent too many requests in a given amount of time. Intended for use with [[rate limiting|rate-limiting]] schemes.<ref name="rfc6585"/>
	"""},
	431: {
		'name':"Request Header Fields Too Large",
		'desc':"""
			(RFC 6585)
			:The server is unwilling to process the request because either an individual header field, or all the header fields collectively, are too large.<ref name="rfc6585"/>
			;{{anchor|451}}[[HTTP 451|451 Unavailable For Legal Reasons]] (RFC 7725)
			: A server operator has received a legal demand to deny access to a resource or to a set of resources that includes the requested resource.<ref>{{cite web|title=An HTTP Status Code to Report Legal Obstacles|url=https://tools.ietf.org/html/rfc7725|date=February 2016|last=Bray|first=T.|accessdate=7 March 2015|website=ietf.org}}</ref> The code 451 was chosen as a reference to the novel ''[[Fahrenheit 451]]'' (see the Acknowledgements in the RFC).
	"""},
	# ==<span id="5xx Server Error">5xx Server errors</span>==
	# The [[server (computing)|server]] failed to fulfill a request.<ref>{{cite web|title=Server Error Codes|url=http://www.csgnetwork.com/servererrors.html|website=CSGNetwork.com|accessdate=16 October 2015}}</ref>
	# Response status codes beginning with the digit "5" indicate cases in which the server is aware that it has encountered an error or is otherwise incapable of performing the request. 
	# Except when responding to a HEAD request, the server ''should'' include an entity containing an explanation of the error situation, and indicate whether it is a temporary or permanent condition. 
	# Likewise, user agents ''should'' display any included entity to the user. These response codes are applicable to any request method.
	# <ref>{{cite web|last1=mrGott|title=HTTP Status Codes To Handle Errors In Your API|url=http://blog.mrgott.com/misc/5-http-status-codes-to-handle-errors-in-your-api|website=mrGott|accessdate=16 October 2015|
	# 	deadurl=yes|archiveurl=https://web.archive.org/web/20150930030217/http://blog.mrgott.com/misc/5-http-status-codes-to-handle-errors-in-your-api|archivedate=September 30, 2015|df=mdy-all}}</ref>

	500: {
		'name':"Internal Server Error",
		'desc':"""
			: A generic error message, given when an unexpected condition was encountered and no more specific message is suitable.<ref>{{cite web|last1=Fisher|first1=Tim|title=500 Internal Server Error|url=https://www.lifewire.com/500-internal-server-error-explained-2622938|website=Lifewire|accessdate=22 February 2017}}</ref>
	"""},
	501: {
		'name':"Not Implemented",
		'desc':"""
			: The server either does not recognize the request method, or it lacks the ability to fulfil the request. Usually this implies future availability (e.g., a new feature of a web-service API).<ref>{{cite web|title=HTTP Error 501 Not implemented|url=http://www.checkupdown.com/status/E501.html|website=Check Up Down|accessdate=22 February 2017}}</ref>
	"""},
	502: {
		'name':"Bad Gateway",
		'desc':"""
			: The server was acting as a [[gateway (telecommunications)|gateway]] or proxy and received an invalid response from the upstream server.<ref>{{cite web|last1=Fisher|first1=Tim|title=502 Bad Gateway|url=https://www.lifewire.com/502-bad-gateway-error-explained-2622939|website=Lifewire|accessdate=22 February 2017}}</ref>
	"""},
	503: {
		'name':"Service Unavailable",
		'desc':"""
			: The server cannot handle the request (because it is overloaded or down for maintenance). Generally, this is a temporary state.<ref>{{cite web|last1=alex|title=What is the correct HTTP status code to send when a site is down for maintenance?|url=https://stackoverflow.com/questions/2786595/what-is-the-correct-http-status-code-to-send-when-a-site-is-down-for-maintenance|website=Stack Overflow|accessdate=16 October 2015}}</ref>
	"""},
	504: {
		'name':"Gateway Timeout",
		'desc':"""
			: The server was acting as a gateway or proxy and did not receive a timely response from the upstream server.<ref>{{cite web|title=HTTP Error 504 Gateway timeout|url=http://www.checkupdown.com/status/E504.html|website=Check Up Down|accessdate=16 October 2015}}</ref>
	"""},
	505: {
		'name':"HTTP Version Not Supported",
		'desc':"""
			: The server does not support the HTTP protocol version used in the request.<ref>{{cite web|title=HTTP Error 505 - HTTP version not supported|url=http://www.checkupdown.com/status/E505.html|website=Check Up Down|accessdate=16 October 2015}}</ref>
	"""},
	506: {
		'name':"Variant Also Negotiates",
		'desc':"""
			(RFC 2295)
			: Transparent [[content negotiation]] for the request results in a [[circular reference]].<ref name="RFC_2295">{{cite IETF| title = Transparent Content Negotiation in HTTP| rfc    = 2295| last1 = Holtman| first1 = Koen| authorlink1 =| last2       = Mutz| first2      = Andrew H.| authorlink2 =|date=March 1998| publisher   = [[Internet Engineering Task Force|IETF]]| accessdate  = October 24, 2009}}</ref>
	"""},
	507: {
		'name':"Insufficient Storage",
		'desc':"""
			(WebDAV; RFC 4918)
			: The server is unable to store the representation needed to complete the request.<ref name="RFC_4918"/>
	"""},
	508: {
		'name':"Loop Detected",
		'desc':"""
			(WebDAV; RFC 5842)
			: The server detected an infinite loop while processing the request (sent instead of [[#208|208 Already Reported]]).
	"""},
	510: {
		'name':"Not Extended",
		'desc':"""
			(RFC 2774)
			: Further extensions to the request are required for the server to fulfil it.<ref name="RFC_2774">{{cite IETF| title       = An HTTP Extension Framework| rfc         = 2774|last1= Nielsen| first1= Henrik Frystyk| authorlink1 = Henrik Frystyk Nielsen| last2       = Leach| first2      = Paul| authorlink2 =| last3       = Lawrence| first3      =Scott| authorlink3 =|date=February 2000| publisher   = [[Internet Engineering Task Force|IETF]]| accessdate  = October 24, 2009}}</ref>
	"""},
	511: {
		'name':"Network Authentication Required",
		'desc':"""
			(RFC 6585)
			:The client needs to authenticate to gain network access. Intended for use by intercepting proxies used to control access to the network (e.g., "[[captive portal]]s" used to require agreement to Terms of Service before granting full Internet access via a [[Hotspot (Wi-Fi)|Wi-Fi hotspot]]).<ref name="rfc6585"/>
			:{{Anchor|unofficial}}
	"""},
	# ==Unofficial codes==
	# The following codes are not specified by any standard.
	218: {
		'name':"This is fine",
		'desc':"""
			([[Apache Web Server]])
			:Used as a catch-all error condition for allowing response bodies to flow through Apache when ProxyErrorOverride is enabled. When ProxyErrorOverride is enabled in Apache, response bodies that contain a status code of 4xx or 5xx are automatically discarded by Apache in favor of a generic response or a custom response specified by the ErrorDocument directive.<ref name="ThisIsFine">{{cite web | url = https://httpd.apache.org/docs/2.4/mod/mod_proxy.html#ProxyErrorOverride | title = Apache ProxyErrorOverride | accessdate=7 June 2018}}</ref>
	"""},
	419: {
		'name':"Page Expired",
		'desc':"""
			([[Laravel|Laravel Framework]])
			:Used by the Laravel Framework when a CSRF Token is missing or expired.
	"""},
	420: [{
		'name':"Method Failure",
		'desc':"""
			([[Spring Framework]])
			:A deprecated response used by the Spring Framework when a method has failed.<ref>{{cite web|title=Enum HttpStatus|url=https://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/http/HttpStatus.html|website=Spring Framework|publisher=org.springframework.http|accessdate=16 October 2015}}</ref>
	"""},
		{
		'name':"Enhance Your Calm",
		'desc':"""
			([[Twitter]])
			:Returned by version 1 of the Twitter Search and Trends API when the client is being rate limited; versions 1.1 and later use the [[#429|429 Too Many Requests]] response code instead.<ref name="TwitterErrorCodes">{{cite web| url = https://developer.twitter.com/en/docs/basics/response-codes | title = Twitter Error Codes & Responses | year = 2014 | publisher=[[Twitter]] | accessdate=January 20, 2014}}</ref>
	"""}],
	450: {
		'name':"Blocked by Windows Parental Controls",
		'desc':"""
			(Microsoft)
			:The Microsoft extension code indicated when Windows Parental Controls are turned on and are blocking access to the requested webpage.<ref>{{cite web | url = https://public.bn1.livefilestore.com/y1pJXeg_sNOONKwMraE-xmZFWAfZF6COAKnyfgc-2ykUof743pV4XuRqm14pj-b_yK8Km4sfSR6mU5OhLrupZ8dFg | title = Screenshot of error page | format = bmp |accessdate = October 11, 2009}}</ref>
	"""},
	498: {
		'name':"Invalid Token",
		'desc':"""
			(Esri)
			:Returned by [[ArcGIS Server|ArcGIS for Server]]. Code 498 indicates an expired or otherwise invalid token.<ref name="arcgis">{{cite web
			| url = http://help.arcgis.com/en/arcgisserver/10.0/apis/soap/index.htm#Using_token_authentication.htm
			| title = Using token-based authentication
			|website = ArcGIS Server SOAP SDK}}</ref>
	"""},
	499: [{
		'name':"Token Required",
		'desc':"""
			(Esri)
			:Returned by [[ArcGIS Server|ArcGIS for Server]]. Code 499 indicates that a token is required but was not submitted.<ref name="arcgis" />
	"""},
		{
		'name':"Client Closed Request",
		'desc':"""
			((part of ===nginx===))
			(( The [[nginx]] web server software expands the 4xx error space to signal issues with the client's request.<ref>{{cite web|url=http://lxr.nginx.org/source/src/http/ngx_http_request.h|title=ngx_http_request.h|work=nginx 1.9.5 source code|publisher=nginx inc.|accessdate=2016-01-09}}</ref><ref>{{cite web|url=http://lxr.nginx.org/source/src/http/ngx_http_special_response.c|title=ngx_http_special_response.c|work=nginx 1.9.5 source code|publisher=nginx inc.|accessdate=2016-01-09}}</ref>))
			:Used when the client has closed the request before the server could send a response.
	"""}],
	509: {
		'name':"Bandwidth Limit Exceeded",
		'desc':"""
			([[Apache Web Server]]/[[cPanel]])
			:The server has exceeded the bandwidth specified by the server administrator; this is often used by shared hosting providers to limit the bandwidth of customers.<ref>{{cite web|url=https://documentation.cpanel.net/display/CKB/HTTP+Error+Codes+and+Quick+Fixes#HTTPErrorCodesandQuickFixes-509BandwidthLimitExceeded|title=HTTP Error Codes and Quick Fixes|publisher=Docs.cpanel.net|accessdate=October 15, 2015}}</ref>
	"""},
	526: [{
		'name':"Invalid SSL",
		'desc':"""
			Certificate
			:Used by [[Cloudflare]] and [[Cloud Foundry]]'s gorouter to indicate failure to validate the SSL/TLS certificate that the origin server presented.
	"""},
		{
		'name':"Invalid SSL Certificate",
		'desc':"""
			((part of ===Cloudflare===))
			(( [[Cloudflare]]'s reverse proxy service expands the 5xx series of errors space to signal issues with the origin server.<ref>{{cite web|url=https://support.cloudflare.com/hc/en-us/sections/200820298-Error-Pages|title=Troubleshooting: Error Pages|publisher=[[Cloudflare]]|accessdate=2016-01-09}}</ref>))
			:Cloudflare could not validate the SSL certificate on the origin web server.
	"""}],
	530: [{
		'name':"Site is frozen",
		'desc':"""
			:Used by the [[Pantheon (software)|Pantheon]] web platform to indicate a site that has been frozen due to inactivity.<ref>{{cite web |url=https://pantheon.io/docs/platform-considerations/ |title=Platform Considerations {{!}} Pantheon Docs |website=pantheon.io}}</ref>
	"""},
		{
		'name':"Origin DNS Error",
		'desc':"""
			((part of ===Cloudflare===))
			(( [[Cloudflare]]'s reverse proxy service expands the 5xx series of errors space to signal issues with the origin server.<ref>{{cite web|url=https://support.cloudflare.com/hc/en-us/sections/200820298-Error-Pages|title=Troubleshooting: Error Pages|publisher=[[Cloudflare]]|accessdate=2016-01-09}}</ref>))
			:Error 530 indicates that the requested host name could not be resolved on the Cloudflare network to an origin server.<ref>{{cite web|url=https://support.cloudflare.com/hc/en-us/articles/234979888-Error-1016-Origin-DNS-error|title=Error 1016 - Origin DNS error|publisher=[[Cloudflare]]}}</ref>
	"""}],
	598: {
		'name':"Network read timeout error",
		'desc':"""
			(Informal convention)
			:Used by some HTTP proxies to signal a network read timeout behind the proxy to a client in front of the proxy.<ref>{{Cite web|url=http://www.ascii-code.com/http-status-codes.php|title=HTTP status codes - ascii-code.com|last=http://www.injosoft.se|first=Injosoft AB|website=www.ascii-code.com|access-date=2016-12-23}}</ref>
	"""},
	# ===Internet Information Services===
	# Microsoft's [[Internet Information Services]] web server expands the 4xx error space to signal errors with the client's request.
	440: {
		'name':"Login Time-out",
		'desc':"""
			:The client's session has expired and must log in again.<ref name="MS_KB941201">
			{{cite web| url = https://support.microsoft.com/en-us/help/941201/ | title = Error message when you try to log on to Exchange 2007 by using Outlook Web Access: "440 Login Time-out" | year = 2010 | publisher=[[Microsoft]] | accessdate=November 13, 2013 }}</ref>
	"""},
	449: {
		'name':"Retry With",
		'desc':"""
			:The server cannot honour the request because the user has not provided the required information.<ref name="MS_DD891478">{{cite web | url = http://msdn.microsoft.com/en-us/library/dd891478(PROT.10).aspx | title = 2.2.6 449 Retry With Status Code | year = 2009 | publisher=[[Microsoft]] | accessdate=October 26, 2009}}</ref>
	"""},
	451: {
		'name':"Redirect",
		'desc':"""
			:Used in [[Exchange ActiveSync]] when either a more efficient server is available or the server cannot access the users' mailbox.<ref>{{cite web | title = MS-ASCMD, Section 3.1.5.2.2 | url = http://msdn.microsoft.com/en-us/library/gg651019 |publisher=Msdn.microsoft.com|accessdate=January 8, 2015 }}</ref> The client is expected to re-run the HTTP AutoDiscover operation to find a more appropriate server.<ref>{{cite web | title = Ms-oxdisco | url = http://msdn.microsoft.com/en-us/library/cc433481 |publisher=Msdn.microsoft.com|accessdate=January 8, 2015 }}</ref>
	"""},
	# ===nginx===
	# The [[nginx]] web server software expands the 4xx error space to signal issues with the client's request.
	# <ref>{{cite web|url=http://lxr.nginx.org/source/src/http/ngx_http_request.h|title=ngx_http_request.h|work=nginx 1.9.5 source code|publisher=nginx inc.|accessdate=2016-01-09}}</ref>
	# <ref>{{cite web|url=http://lxr.nginx.org/source/src/http/ngx_http_special_response.c|title=ngx_http_special_response.c|work=nginx 1.9.5 source code|publisher=nginx inc.|accessdate=2016-01-09}}</ref>
	444: {
		'name':"No Response",
		'desc':"""
			:Used internally<ref>[http://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return "return" directive]  (http_rewrite module) documentation.</ref> to instruct the server to return no information to the client and close the connection immediately.
	"""},
	494: {
		'name':"Request header too large",
		'desc':"""
			:Client sent too large request or too long header line.
	"""},
	495: {
		'name':"SSL Certificate Error",
		'desc':"""
			:An expansion of the [[#400|400 Bad Request]] response code, used when the client has provided an invalid [[client certificate]].
	"""},
	496: {
		'name':"SSL Certificate Required",
		'desc':"""
			:An expansion of the [[#400|400 Bad Request]] response code, used when a client certificate is required but not provided.
	"""},
	497: {
		'name':"HTTP Request Sent to HTTPS Port",
		'desc':"""
			:An expansion of the [[#400|400 Bad Request]] response code, used when the client has made a HTTP request to a port listening for HTTPS requests.
	"""},
	# ===Cloudflare===
	# [[Cloudflare]]'s reverse proxy service expands the 5xx series of errors space to signal issues with the origin server.
	# <ref>{{cite web|url=https://support.cloudflare.com/hc/en-us/sections/200820298-Error-Pages|title=Troubleshooting: Error Pages|publisher=[[Cloudflare]]|accessdate=2016-01-09}}</ref>

	520: {
		'name':"Unknown Error",
		'desc':"""
			:The 520 error is used as a "catch-all response for when the origin server returns something unexpected", listing connection resets, large headers, and empty or invalid responses as common triggers.
	"""},
	521: {
		'name':"Web Server Is Down",
		'desc':"""
			:The origin server has refused the connection from Cloudflare.
	"""},
	522: {
		'name':"Connection Timed Out",
		'desc':"""
			:Cloudflare could not negotiate a [[TCP handshake]] with the origin server.
	"""},
	523: {
		'name':"Origin Is Unreachable",
		'desc':"""
			:Cloudflare could not reach the origin server; for example, if the [[DNS record]]s for the origin server are incorrect.
	"""},
	524: {
		'name':"A Timeout Occurred",
		'desc':"""
			:Cloudflare was able to complete a TCP connection to the origin server, but did not receive a timely HTTP response.
	"""},
	525: {
		'name':"SSL Handshake Failed",
		'desc':"""
			:Cloudflare could not negotiate a [[Transport Layer Security#TLS handshake|SSL/TLS handshake]] with the origin server.
	"""},
	527: {
		'name':"Railgun Error",
		'desc':"""
			:Error 527 indicates that the request timed out or failed after the WAN connection had been established.<ref>{{cite web|url=https://support.cloudflare.com/hc/en-us/articles/217891268-527-Railgun-Listener-to-Origin-Error|title=Railgun Listener to Origin Error|publisher=[[Cloudflare]]|accessdate=2016-10-12}}</ref>
	"""},
}
def get_name(v):
	'''helper function for getting the name for the http_status_codes dictionary'''
	if isinstance(v, dict):
		return v["name"]
	else:
		return get_name(v[0])
http_status_codes = dict([(k,get_name(v)) for k,v in http_status_info.items()])
