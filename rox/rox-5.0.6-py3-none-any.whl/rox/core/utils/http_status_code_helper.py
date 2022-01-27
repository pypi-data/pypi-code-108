def is_success_status_code(response):
    return 200 <= response.status_code < 300