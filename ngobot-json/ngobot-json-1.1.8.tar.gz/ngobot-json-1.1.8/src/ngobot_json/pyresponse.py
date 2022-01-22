import json


class JsonResponse:

    data = "Successful"
    category = "success"

    def __init__(self, data=data, category=category):
        self.data = data
        self.category = category

    def set_data(self, status, message):
        try:
            success = {
                "status": 200,
                "message": "ok",
                "reason": self.data
            }
            error = {
                "status": 422,
                "message": "Unprocessable Entity",
                "reason": self.data
            }
            if self.category == "error":
                data = {
                    "status": status,
                    "message": message,
                    "data": error
                }
                return json.dumps(data)
            elif self.category == "success":
                data = {
                    "status": status,
                    "message": message,
                    "data": success
                }
                return json.dumps(data)
            else:
                data = {
                    "status": status,
                    "message": message,
                    "data": self.data
                }
                return json.dumps(data)
        except Exception as e:
            data = {
                "status": 500,
                "message": e,
                "data": self.data
            }
        return json.dumps(data)

    # Information responses - 1xx

    def Continue(self):
        try:
            data = self.set_data(100, "Continue")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def SwitchingProtocol(self):
        try:
            data = self.set_data(101, "Switching Protocol")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Processing(self):
        try:
            data = self.set_data(102, "Processing")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def EarlyHints(self):
        try:
            data = self.set_data(103, "Early Hints")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    # Successful responses - 2xx

    def Success(self):
        try:
            data = self.set_data(200, "Successful")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Created(self):
        try:
            data = self.set_data(201, "Created Successfully")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Accepted(self):
        try:
            data = self.set_data(202, "Accepted")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NonAuthoritativeInformation(self):
        try:
            data = self.set_data(203, "Non-Authoritative Information")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NoContent(self):
        try:
            data = self.set_data(204, "No Content")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def ResetContent(self):
        try:
            data = self.set_data(205, "Reset Content")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def PartialContent(self):
        try:
            data = self.set_data(206, "Partial Content")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def MultiStatus(self):
        try:
            data = self.set_data(207, "Multi Status")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def AlreadyReported(self):
        try:
            data = self.set_data(208, "Already Reported")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def IMUsed(self):
        try:
            data = self.set_data(226, "IM Used")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    # Redirection messages - 3xx

    def MultipleChoices(self):
        try:
            data = self.set_data(300, "Multiple Choices")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def MovedPermanently(self):
        try:
            data = self.set_data(301, "Moved Permanently")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Found(self):
        try:
            data = self.set_data(302, "Found")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def SeeOther(self):
        try:
            data = self.set_data(303, "See Other")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NotModified(self):
        try:
            data = self.set_data(304, "Not Modified")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def UseProxy(self):
        try:
            data = self.set_data(305, "Use Proxy")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Unused(self):
        try:
            data = self.set_data(306, "Unused")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def TemporaryRedirect(self):
        try:
            data = self.set_data(307, "Temporary Redirect")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def PermanentRedirect(self):
        try:
            data = self.set_data(308, "Permanent Redirect")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    # Client error responses - 4xx

    def BadRequest(self):
        try:
            data = self.set_data(400, "Bad Request")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Unauthorized(self):
        try:
            data = self.set_data(401, "Unauthorized")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def PaymentRequired(self):
        try:
            data = self.set_data(402, "Payment Required")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Forbidden(self):
        try:
            data = self.set_data(403, "Forbidden")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NotFound(self):
        try:
            data = self.set_data(404, "Not Found")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def MethodNotAllowed(self):
        try:
            data = self.set_data(405, "Method Not Allowed")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NotAcceptable(self):
        try:
            data = self.set_data(406, "Not Acceptable")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def ProxyAuthenticationRequired(self):
        try:
            data = self.set_data(407, "Proxy Authentication Required")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def RequestTimeout(self):
        try:
            data = self.set_data(408, "Request Timeout")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Conflict(self):
        try:
            data = self.set_data(409, "Conflict")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Gone(self):
        try:
            data = self.set_data(410, "Gone")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def LengthRequired(self):
        try:
            data = self.set_data(411, "Length Required")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def PreconditionFailed(self):
        try:
            data = self.set_data(412, "Precondition Failed")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def RequestEntityTooLarge(self):
        try:
            data = self.set_data(413, "Request Entity Too Large")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def RequestURITooLong(self):
        try:
            data = self.set_data(414, "Request-URI Too Long")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def UnsupportedMediaType(self):
        try:
            data = self.set_data(415, "Unsupported Media Type")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def RequestedNotSatisfiable(self):
        try:
            data = self.set_data(416, "Requested Range Not Satisfiable")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def ExpectationFailed(self):
        try:
            data = self.set_data(417, "Expectation Failed")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Teapot(self):
        try:
            data = self.set_data(418, "Teapot")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def EnhanceYourCalm(self):
        try:
            data = self.set_data(420, "Enhance Your Calm")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def UnprocessableEntity(self):
        try:
            data = self.set_data(422, "Unprocessable Entity")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def Locked(self):
        try:
            data = self.set_data(423, "Locked")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def FailedDependency(self):
        try:
            data = self.set_data(424, "Failed Dependency")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def TooEarly(self):
        try:
            data = self.set_data(425, "Too Early")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def UpgradeRequired(self):
        try:
            data = self.set_data(426, "Upgrade Required")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def PreconditionRequired(self):
        try:
            data = self.set_data(428, "Precondition Required")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def TooManyRequests(self):
        try:
            data = self.set_data(429, "Too Many Requests")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def HeaderTooLarge(self):
        try:
            data = self.set_data(431, "Request Header Fields Too Large")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NoResponse(self):
        try:
            data = self.set_data(444, "No Response")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def ActionRetry(self):
        try:
            data = self.set_data(449, "Retry With appropriate action")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def ParentalControls(self):
        try:
            data = self.set_data(450, "Blocked by Windows Parental Controls")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def UnavailableForReasons(self):
        try:
            data = self.set_data(451, "Unavailable For Legal Reasons")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def ClientClosedRequest(self):
        try:
            data = self.set_data(451, "Client Closed Request")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data


    # Server error responses

    def InternalServerError(self):
        try:
            data = self.set_data(500, "Internal Server Error")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NotImplemented(self):
        try:
            data = self.set_data(501, "Not Implemented")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def BadGateway(self):
        try:
            data = self.set_data(502, "Bad Gateway")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def ServiceUnavailable(self):
        try:
            data = self.set_data(503, "Service Unavailable")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def GatewayTimeout(self):
        try:
            data = self.set_data(504, "Gateway Timeout")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def VersionNotSupported(self):
        try:
            data = self.set_data(505, "HTTP Version Not Supported")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def VariantNegotiates(self):
        try:
            data = self.set_data(506, "Variant Also Negotiates")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def InsufficientStorage(self):
        try:
            data = self.set_data(507, "Insufficient Storage")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def LoopDetected(self):
        try:
            data = self.set_data(508, "Loop Detected")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NotExtended(self):
        try:
            data = self.set_data(510, "Not Extended")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data

    def NetworkAuthentication(self):
        try:
            data = self.set_data(511, "Network Authentication Required")
            return data
        except Exception as e:
            data = self.set_data(500, e)
            return data