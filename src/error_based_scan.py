import re
from src.http_handler import HTTPHandler
from src.sqli_scanner import SQLiScanner
from src.print_handler import PrintHandler

dbms_errors = {
    "MySQL": (
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_.*",
        r"MySQL Query fail.*",
        r"SQL syntax.*MariaDB server",
    ),
    "PostgreSQL": (
        r"PostgreSQL.*ERROR",
        r"Warning.*\Wpg_.*",
        r"Warning.*PostgreSQL",
    ),
    "Microsoft SQL Server": (
        r"OLE DB.* SQL Server",
    #    r"(\W|\A)SQL Server.*Driver",
    #    r"Warning.*odbc_.*",
    #    r"Warning.*mssql_",
    #    r"Msg \d+, Level \d+, State \d+",
        r"Unclosed quotation mark after the character string",
        r"Microsoft OLE DB Provider for ODBC Drivers",
    ),
    "Microsoft Access": (
        r"Microsoft Access Driver",
        r"Access Database Engine",
        r"Microsoft JET Database Engine",
    #    r".*Syntax error.*query expression",
    ),
    "Oracle": (
    #    r"\bORA-[0-9][0-9][0-9][0-9]",
        r"Oracle error",
    #    r"Warning.*oci_.*",
        "Microsoft OLE DB Provider for Oracle",
    ),
    "IBM DB2": (
    #    r"CLI Driver.*DB2",
        r"DB2 SQL error",
    ),
    "SQLite": (
        r"SQLite/JDBCDriver",
        r"System.Data.SQLite.SQLiteException",
    ),
    "Informix": (
    #    r"Warning.*ibase_.*",
        r"com.informix.jdbc",
    ),
    "Sybase": (
    #    r"Warning.*sybase.*",
        r"Sybase message",
    )
}

payloads = [
    "'",
    '"',
    "%27",
    "%22"
]

class ErrorBasedScan(SQLiScanner):
    def query_scan(self, target):
        """
        Scans query parameters for error-based SQL injection vulnerabilities.

        Parameters:
            target (object): The target object containing the URL and query parameters.
        """
        target.get_parsed_url()
        target.get_query_parameters()

        for query_param in target.query_params:
            for payload in payloads:
                
                # inject query_param with payload
                injected_url = self._inject_query(target.url, query_param, payload)
                
                # send malicious request
                response = HTTPHandler.send_request(url=injected_url, method="get", timeout=10)
                if response == None:
                    break

                # scan response for dbms error
                html_response = response.content.decode("utf-8", errors="ignore")
                if self._has_dbms_error(html_response):
                    PrintHandler.print_message("Query ~ Error-Based SQL Injection Detected!", "DETECTION", "green")
                    self._log_injection(
                        target=target,
                        vuln_param=query_param,
                        payload=payload,
                        inject_type="query",
                        inject_method="error"
                    )
                    return
                
    def body_scan(self, target):
        """
        Scans the request body for error-based SQL injection vulnerabilities.

        Parameters:
            target (object): The target object containing the URL and body.
        """
        if target.body:
            for param, value in target.body.items():
                for payload in payloads:

                    # inject parameter with payload
                    injected_body = self._inject_body(target.body, param, payload)
                    
                    # send malicious request
                    response = HTTPHandler.send_request(url=target.url, body=injected_body, method="post", timeout=10)
                    if response == None:
                        break

                    # scan response for dbms error
                    html_response = response.content.decode("utf-8", errors="ignore")
                    if self._has_dbms_error(html_response):
                        PrintHandler.print_message("Body ~ Error-Based SQL Injection Detected!", "DETECTION", "green")
                        self._log_injection(
                            target=target,
                            vuln_param=param,
                            payload=payload,
                            inject_type="body",
                            inject_method="error"
                        )
                        return

    def header_scan(self, target):
        """
        Scans HTTP headers for error-based SQL injection vulnerabilities.

        Parameters:
            target (object): The target object containing the URL and headers.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }

        for payload in payloads:
            for header, value in headers.items():

                # inject payload into header
                injected_headers = self._inject_header(headers, header, payload)
                
                # send malicious request
                response = None
                if target.body:
                    response = HTTPHandler.send_request(url=target.url, body=target.body, headers=injected_headers, method="post", timeout=10)
                else:
                    response = HTTPHandler.send_request(url=target.url, headers=injected_headers, method="get", timeout=10)
                if response == None:
                    break

                # scan response for dbms error
                html_response = response.content.decode("utf-8", errors="ignore")
                if self._has_dbms_error(html_response):
                    PrintHandler.print_message("Header ~ Error-Based SQL Injection Detected!", "DETECTION", "green")
                    self._log_injection(
                        target=target,
                        vuln_param=header,
                        headers=injected_headers,
                        payload=payload,
                        inject_type="header",
                        inject_method="error"
                    )
                    return

    def cookie_scan(self, target):
        """
        Scans cookies for error-based SQL injection vulnerabilities.

        Parameters:
            target (object): The target object containing the URL and cookies.
        """
        cookies = target.get_cookies()
        
        for cookie, _ in cookies.items():
            for payload in payloads:
                
                # inject payload into cookie
                injected_cookies = self._inject_cookie(cookies, cookie, payload)
                
                # send malicious request
                response = None
                if target.body:
                    response = HTTPHandler.send_request(url=target.url, body=target.body, cookies=injected_cookies, method="post", timeout=10)
                else:
                    response = HTTPHandler.send_request(url=target.url, cookies=injected_cookies, method="get", timeout=10)
                if response == None:
                    break

                # scan response for dbms error
                html_response = response.content.decode("utf-8", errors="ignore")
                if self._has_dbms_error(html_response):
                    PrintHandler.print_message("Cookie ~ Error-Based SQL Injection Detected!", "DETECTION", "green")
                    self._log_injection(
                        target=target,
                        vuln_param=cookie,
                        cookies=cookies,
                        payload=payload,
                        inject_type="cookie",
                        inject_method="error"
                    )
                    return

    def detect_false_positive(self, target):
        """
        Checks for false positives by sending an unmodified request.

        Parameters:
            target (object): The target object containing the URL and request data.

        Returns:
            bool: True if a false positive is detected, False otherwise.
        """
        # send request without any modification
        response = target.send_request()
        if response == None:
            return False

        # if dbms error is detected in an umodified request, target will likely raise a false positive
        html_response = response.content.decode("utf-8", errors="ignore")
        if self._has_dbms_error(html_response):
            PrintHandler.print_message("False Positive Detected!", "WARNING", "red")
            return True
        return False

    def _has_dbms_error(self, text):
        """
        Checks if the provided text contains any DBMS error messages.

        Parameters:
            text (str): The response text to analyze.

        Returns:
            bool: True if a DBMS error message is found, False otherwise.
        """
        for db, errors in dbms_errors.items():
            for error in errors:
                if re.compile(error).search(text):
                    return True
        return False
