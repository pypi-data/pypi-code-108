GOOGLE_BACKEND = """
backend google_host {{
    .between_bytes_timeout = 10s;
    .connect_timeout = 1s;
    .dynamic = true;
    .first_byte_timeout = 15s;
    .host = "www.google.com";
    .max_connections = 200;
    .port = "443";
    .share_key = "{SERVICE_ID}";
    .ssl = true;
    .ssl_cert_hostname = "www.google.com";
    .ssl_check_cert = always;
    .ssl_sni_hostname = "www.google.com";
    .probe = {{
        .dummy = true;
        .initial = 5;
        .request = "HEAD / HTTP/1.1"  "Host: www.google.com" "Connection: close";
        .threshold = 1;
        .timeout = 2s;
        .window = 5;
      }}
}}
"""

CAPTCHA_RECV_VCL = """

declare local var.captcha_token STRING;

if(req.http.origURL != req.http.origURL){{
  set req.http.origURL = req.url; 
  set req.http.origHost = req.http.host ;
}}

if(req.http.origIP != req.http.origIP){{
  set req.http.origIP = req.http.Fastly-Client-IP; 
}}


if (std.strlen(querystring.get(req.url, "g-recaptcha-response")) > 0){{  # This is captcha response
  set req.backend = google_host /* www.google.com */ ; 
  set var.captcha_token = querystring.get(req.url, "g-recaptcha-response"); 
  set req.url = "/recaptcha/api/siteverify" ; 
  set req.url = querystring.add(req.url, "secret", "{RECAPTCHA_SECRET}"); 
  set req.url = querystring.add(req.url, "response", var.captcha_token); 
  set req.http.host = "www.google.com" ;
  return(pass);
}}


if(!req.http.Cookie:captchaAuth){{
  error 676 ; 
}} else{{
    if (req.http.Cookie:captchaAuth !~ "^([a-zA-Z0-9\-_]+)?\.([a-zA-Z0-9\-_]+)?\.([a-zA-Z0-9\-_]+)?$") {{
        // JWT doesn't match signature
        error 676;
    }}

    declare local var.X-UUID STRING ;
    declare local var.X-JWT-Issued STRING ;
    declare local var.X-JWT-Expires STRING ;
    declare local var.X-JWT-Header STRING ;
    declare local var.X-JWT-Payload STRING ;
    declare local var.X-JWT-Signature STRING ;
    declare local var.X-JWT STRING ;
    declare local var.X-JWT-Valid-Signature STRING ; 
    declare local var.JWT-IP STRING ; 

    set var.X-JWT-Header = re.group.1;
    set var.X-JWT-Payload = re.group.2;
    set var.X-JWT-Signature = digest.base64url_nopad_decode(re.group.3);
    set var.X-JWT-Valid-Signature = digest.hmac_sha256("{JWT_SECRET}", var.X-JWT-Header "." var.X-JWT-Payload);

    // Validate signature
    if(digest.secure_is_equal(var.X-JWT-Signature, var.X-JWT-Valid-Signature)) {{
        // Decode payload
        set var.X-JWT-Payload = digest.base64url_nopad_decode(var.X-JWT-Payload);
        set var.X-JWT-Expires = regsub(var.X-JWT-Payload, {{"^.*?"exp"\s*?:\s*?([0-9]+).*?$"}}, "\\1");

        if(req.http.origIP ~ ":"){{
          set var.JWT-IP = regsub(var.X-JWT-Payload, {{"^.*?"ip"\s*?:\s*?(([0-9a-fA-F]{{1,4}}:){{7,7}}[0-9a-fA-F]{{1,4}}|([0-9a-fA-F]{{1,4}}:){{1,7}}:|([0-9a-fA-F]{{1,4}}:){{1,6}}:[0-9a-fA-F]{{1,4}}|([0-9a-fA-F]{{1,4}}:){{1,5}}(:[0-9a-fA-F]{{1,4}}){{1,2}}|([0-9a-fA-F]{{1,4}}:){{1,4}}(:[0-9a-fA-F]{{1,4}}){{1,3}}|([0-9a-fA-F]{{1,4}}:){{1,3}}(:[0-9a-fA-F]{{1,4}}){{1,4}}|([0-9a-fA-F]{{1,4}}:){{1,2}}(:[0-9a-fA-F]{{1,4}}){{1,5}}|[0-9a-fA-F]{{1,4}}:((:[0-9a-fA-F]{{1,4}}){{1,6}})|:((:[0-9a-fA-F]{{1,4}}){{1,7}}|:)|fe80:(:[0-9a-fA-F]{{0,4}}){{0,4}}%[0-9a-zA-Z]{{1,}}|::(ffff(:0{{1,4}}){{0,1}}:){{0,1}}((25[0-5]|(2[0-4]|1{{0,1}}[0-9]){{0,1}}[0-9])\.){{3,3}}(25[0-5]|(2[0-4]|1{{0,1}}[0-9]){{0,1}}[0-9])|([0-9a-fA-F]{{1,4}}:){{1,4}}:((25[0-5]|(2[0-4]|1{{0,1}}[0-9]){{0,1}}[0-9])\.){{3,3}}(25[0-5]|(2[0-4]|1{{0,1}}[0-9]){{0,1}}[0-9])).*?$"}}, "\\1") ;
        }} else {{
          set var.JWT-IP = regsub(var.X-JWT-Payload, {{"^.*?"ip"\s*?:\s*?([0-9]{{1,3}}\.[0-9]{{1,3}}\.[0-9]{{1,3}}\.[0-9]{{1,3}}).*?$"}}, "\\1");
        }}
        if( var.JWT-IP != req.http.origIP){{
          error 676;
        }}

        // Validate expiration
        if (time.is_after(now, std.integer2time(std.atoi(var.X-JWT-Expires)))) {{
            // Expired Token
            error 676;
        }}

    }} else {{
        // Invalid JWT
        error 676;
    }}
  }}

set req.backend = F_Host_1 ;
set req.http.host = req.http.origHost ;
"""


CAPTCHA_RENDER_VCL = """
if (obj.status == 676){{
    set obj.status = 200 ;
    set obj.response = "OK";
    set obj.http.Cache-Control = "private, no-store";
    set obj.http.Content-Type = "text/html";
  
    synthetic {{"
      <html>
        <head>
          <title>reCAPTCHA</title>
          <script src="https://www.google.com/recaptcha/api.js" async defer></script>
        </head>
        <body>
          <form action="" method="GET">
            <div class="g-recaptcha" data-sitekey="{RECAPTCHA_SITE_KEY}"></div>
            <br/>
            <input type="submit" value="Submit">
          </form>
        </body>
      </html>
    "}};
    return(deliver);
  }}
"""

CAPTCHA_VALIDATOR_VCL = """
if (req.http.Host ~ "google.com"){{
  if(resp.status == 200){{
    set req.http.origURL =querystring.filter(req.http.origURL, "g-recaptcha-response");
    set resp.status = 307;
    set resp.response = "Temporary redirect";

    declare local var.X-UUID STRING ;
    declare local var.X-JWT-Issued STRING ;
    declare local var.X-JWT-Expires STRING ;
    declare local var.X-JWT-Header STRING ;
    declare local var.X-JWT-Payload STRING ;
    declare local var.X-JWT-Signature STRING ;
    declare local var.X-JWT  STRING ;

    set var.X-UUID = randomstr(8, "0123456789abcdef") "-" randomstr(4, "0123456789abcdef") "-4" randomstr(3, "0123456789abcdef") "-" randomstr(1, "89ab") randomstr(3, "0123456789abcdef") "-" randomstr(12, "0123456789abcdef");
    set var.X-JWT-Issued = now.sec;
    set var.X-JWT-Expires = strftime({{"%s"}}, time.add(now, {COOKIE_EXPIRY_DURATION}s));
    set var.X-JWT-Header = digest.base64url_nopad({{"{{"alg":"HS256","typ":"JWT""}}{{"}}"}});
    set var.X-JWT-Payload = digest.base64url_nopad({{"{{"sub":""}} var.X-UUID {{"","exp":"}} var.X-JWT-Expires {{","ip":"}} req.http.origIP {{","iat":"}} var.X-JWT-Issued {{","iss":"Fastly""}}{{"}}"}});
    set var.X-JWT-Signature = digest.base64url_nopad(digest.hmac_sha256("{JWT_SECRET}", var.X-JWT-Header "." var.X-JWT-Payload));
    set var.X-JWT = var.X-JWT-Header "." var.X-JWT-Payload "." var.X-JWT-Signature;

    set resp.http.Set-Cookie = "captchaAuth=" var.X-JWT  "; path=/; max-age=3600";
    set resp.http.Cache-Control = "private, no-store";
    set resp.http.Location = req.http.origURL ;
  }}
  restart;
}}
"""
