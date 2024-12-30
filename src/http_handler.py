import requests

class HTTPHandler:
    @staticmethod
    def send_request(url="", body=None, headers=None, cookies=None, timeout=None, method=""):
        """
        Sends HTTP request.

        Unless told otherwise, will overwrite the default Python User-Agent
        to avoid being blocked.

        Parameters:
            url (str): The URL to send the request to.
            body (dict): Post body data.
            headers (dict): Headers to be used in the request.
            cookies (dict): Cookies to be send in the request.
            timeout (int): Max amount of seconds to wait for a response before
                           closing the connection.

        Returns:
            Response: The response object returned by the requests library.
        """

        # if headers is not set, set one to remove the default Python header
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            }
        
        if body is None:
            body = {}

        # send request & return response object
        response = ""
        try:
            if method.lower() == "get":
                response = requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
            elif method.lower() == "post":
                response = requests.post(url, headers=headers, cookies=cookies, data=body, timeout=timeout)
            else:
                raise NotImplementedError()
        except:
            return None

        return response
