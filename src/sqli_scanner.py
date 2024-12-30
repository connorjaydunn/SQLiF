import urllib.parse
import json
import logging
import requests
import os

class SQLiScanner:
    def __init__(self, output_file=None):
        """
        Initialises the SQLiScanner object.

        Parameters:
            output_file (str, optional): The file where scan logs are stored.
        """
        if output_file:
            self.output_file = output_file
        else:
            self.output_file = os.path.join(os.getcwd(), "sqlif_output.txt")
            
        logging.basicConfig(
            filename=self.output_file,
            level=logging.INFO,
            format='%(message)s'
        )
        self.logger = logging.getLogger("SQLiScanner")

    def _log_injection(self, target, vuln_param, payload, inject_type, inject_method, headers=None, cookies=None):        
        """
        Logs details of successful SQL injections to the output file.

        Parameters:
            target (str): The Target object.
            vuln_param (str): The name of the vulnerable parameter.
            payload (str): The payload used to detect the injection.
            inject_type (str): The type of injection (i.e. header, query, body, cookies).
            inject_method (str): The method of injection (i.e. error, time).
            headers (dict, optional): The headers used during the injection request.
            cookies (RequestCookieJar, optional): The cookies used during the injection request.
        """
        log = {
            "url": target.url,
            "inject_type": inject_type,
            "inject_method": inject_method,
            "vuln_param": vuln_param,
            "payload": payload,
        }

        # insert any optional information
        if target.body:
            log["body"] = target.body
        if headers:
            log["headers"] = headers
        if cookies:
            log["cookies"] = cookies.get_dict()
            
        self.logger.info(json.dumps(log, indent=4))

    def query_scan(self, target):
        raise NotImplementedError()

    def body_scan(self, target):
        raise NotImplementedError()

    def header_scan(self, target):
        raise NotImplementedError()

    def cookie_scan(self, target):
        raise NotImplementedError()

    def path_scan(self, target):
        raise NotImplementedError()

    def _inject_query(self, url, param_name, payload):
        """
        Injects a payload into a specified query parameter.

        Parameters:
            url (str): The target URL to modify.
            param_name (str): The name of the query parameter to inject into.
            payload (str): The SQL injection payload to insert.

        Returns:
            str: The modified URL with the injected payload.
        """
        url_parts = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(url_parts.query)

        # append the payload to the specified query parameter
        query_params[param_name][0] += payload

        # rebuild the url with the modified query parameters
        new_query = '&'.join([f"{key}={value[0]}" for key, value in query_params.items()])
        new_url = url_parts._replace(query=new_query).geturl()
        return new_url

    def _inject_body(self, body, body_name, payload):
        """
        Injects a payload into a specified field in the request body.

        Parameters:
            body (dict): The request body to modify.
            body_name (str): The name of the body field to inject into.
            payload (str): The SQL injection payload to insert.

        Returns:
            dict: The modified body with the injected payload.
        """
        # copy the body to avoid modifying the orignial
        body_copy = body.copy()

        # append the payload to the specified body parameter
        body_copy[body_name] += payload

        return body_copy

    def _inject_header(self, headers, header_name, payload):
        """
        Injects a payload into a specified header.

        Parameters:
            headers (dict): The headers to modify.
            header_name (str): The name of the header to inject into.
            payload (str): The SQL injection payload to insert.

        Returns:
            dict: The modified headers with the injected payload.
        """
        # copy the headers to avoid modifying the original
        headers_copy = headers.copy()

        # append the payload to the specified header
        headers_copy[header_name] += payload
        return headers_copy

    def _inject_cookie(self, cookies, cookie_name, payload):
        """
        Injects a payload into a specified cookie.

        Parameters:
            cookies (list): A list of cookies to modify.
            cookie_name (str): The name of the cookie to inject into.
            payload (str): The SQL injection payload to insert.

        Returns:
            list: The modified list of cookies with the injected payload.
        """
        # create a copy of the cookies to avoid modifying the original
        cookies_copy = cookies.copy()

        # find and inject payload into the specified cookie
        for cookie in cookies_copy:
            if cookie.name == cookie_name:
                if cookie.value == None:
                    cookie.value = ""
                cookie.value += payload
                break
                
        return cookies_copy

    #def inject_path(self, payload):
    #    pass # todo

    def detect_false_positive(self, target):
        raise NotImplementedError()
