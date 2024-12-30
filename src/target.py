from src.http_handler import HTTPHandler
from src.form_handler import FormHandler
import urllib.parse

class Target:
    def __init__(self, url, body=None):
        """
        Initilises the Target object.

        Parameters:
            url (str): The target's URL.
            body (dict, optional): The target's POST body data.
        """
        self.url = url
        self.parsed_url = ""
        self.query_params = None
        self.body = body
        self.initial_response = None

    def get_parsed_url(self):
        """
        Parses the target URL.
        """
        self.parsed_url = urllib.parse.urlparse(self.url)

    def get_query_parameters(self):
        """
        Gets URL query parameters.
        """
        self.query_params = urllib.parse.parse_qs(self.parsed_url.query)

    def get_cookies(self):
        """
        Parses the target URL.

        Returns:
            RequestsCookieJar: The RequestsCookieJar object returned by the HTTP request.
        """
        response = self.send_request()
        if response == None:
            return {}
        return response.cookies

    def send_request(self):
        """
        Sends a request to the target URL.

        If a request has already been sent, the stored response instead
        of sending another.

        Returns:
            Request: The response object returned from the HTTP request.
        """
        # if we already sent the unmodified request, don't send it again
        if self.initial_response:
            return self.initial_response

        # send unmodified request
        if not self.body:
            self.initial_response = HTTPHandler.send_request(url=self.url, timeout=10, method="get")
            return self.initial_response
        else:
            self.initial_response = HTTPHandler.send_request(url=self.url, body=self.body, timeout=10, method="post")
            return self.initial_response

    def test_connection(self):
        """
        Tests connection to the target URL.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        response = self.send_request
        if response == None:
            return False
        return True

    def form_to_target(self, form):
        """
        Converts a Form to a Target object.

        Parameters:
            form (dict): A dictionary that respresents a form.

        Returns:
            Target: A Target object.
            None: If the form's method is neither GET nor POST.
        """
        if form["method"].lower() == "get":
            
            # construct full url (incase action is relative)
            url = FormHandler.get_full_url(self.url, form["action"])

            # convert query parameters into a useable url
            url = FormHandler.input_to_url(url, form["inputs"])
            return Target(url=url)
        elif form["method"].lower() == "post":

            # construct full url (incase action is relative)
            url = FormHandler.get_full_url(self.url, form["action"])

            # convert post body parameters into a useable dictionary
            body = FormHandler.input_to_dict(form["inputs"])
            return Target(url=url, body=body)
        else:
            return None

    def crawl_forms(self):
        """
        Crawls a page to extract and convert forms into Target objects.

        Returns:
            list: A list of Target objects representing the forms found on the page.
            If no forms are found, an empty list is returned.
        """
        sub_targets = []
        
        response = self.send_request()
        if response == None:
            return []

        # extract forms from html content
        html_response = response.content.decode("utf-8", errors="ignore")
        forms = FormHandler.extract_forms(html_response)

        # convert forms into Target objects
        for form in forms:
            sub_target = self.form_to_target(form)
            if sub_target:
                sub_targets.append(sub_target)

        return sub_targets
