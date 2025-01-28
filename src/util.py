from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

def normalise_url(url):
    """
    Normalises the url by removing query parameter values.

    Parameters:
        url (str): The url to be normalised.
        
    Returns:
        str: The normalised url.
    """
    parsed_url = urlparse(url)
    
    cleared_query_string = urlencode({key: '' for key in parse_qs(parsed_url.query)})
    
    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        cleared_query_string,
        parsed_url.fragment,
    ))

def filter_duplicate_urls(urls):
    """
    Removes duplicate urls from input list.

    Parameters:
        urls (list): List that contains urls with potential duplicates.

    Returns:
        list: List with all duplicate urls removed.
    """
    seen_cleared_urls = set()
    unique_urls = []

    for url in urls:
        cleared_url = normalise_url(url)
        if cleared_url not in seen_cleared_urls:
            seen_cleared_urls.add(cleared_url)
            unique_urls.append(url)

    return unique_urls
