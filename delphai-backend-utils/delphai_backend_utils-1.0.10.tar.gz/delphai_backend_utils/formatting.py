
def clean_url(url, keep_www=False):
  """
  Format and clean and url to be saved or checked.
  Args:
      url: url to be formatted
      keep_www: keep the 'www' part of the url
  Returns: formatted url
  """

  url = url.strip()
  url = url.replace('https://', '').replace('http://', '').rstrip('/')
  if not keep_www:
    url = url.replace('www.', '')
  split_url = url.split('/')
  split_url[0] = split_url[0].lower()
  return '/'.join(split_url)
