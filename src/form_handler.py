import urllib.parse
from bs4 import BeautifulSoup

class FormHandler:
    @staticmethod
    def input_to_dict(inputs):
        """
        Converts form inputs into a useable dictionary.

        Parameters:
            inputs (dict): The dictionary to be converted.
            
        Returns:
            dict: The now converted form inputs as a dictionary.
        """
        body = {}
        for input_tag in inputs:
            if input_tag["type"] == "hidden" or input_tag["value"]:
                body[input_tag["name"]] = input_tag["value"]
            elif input_tag["type"] != "submit":
                body[input_tag["name"]] = ""
        return body

    @staticmethod
    def get_full_url(base_url, action):
        """
        Constructs the full URL using a base url and a relative action.

        Parameters:
            base_url (str): The base url.
            action (str): The relative address / file.

        Returns:
            str: The full URL.
        """
        return urllib.parse.urljoin(base_url, action)

    @staticmethod
    def input_to_url(url, inputs):
        """
        Convers form inputs into a URL with query parameters.

        Parameters:
            url (str): The base URL to which the query parameters will
                       be appended to.
            inputs (dict): A dictionary containing form input data.
            
        Returns:
            str: The entire URL with the query parameters.
        """
        parsed_inputs = FormHandler.input_to_dict(inputs)    
        parsed_url = urllib.parse.urlparse(url)

        # encode the inputs as a query string
        query_string = urllib.parse.urlencode(parsed_inputs, doseq=True)

        # combinds the query parameters and url
        updated_parsed_url = parsed_url._replace(query=query_string)
        full_url = urllib.parse.urlunparse(updated_parsed_url)
        return full_url

    @staticmethod
    def extract_forms(html):
        """
        Extracts forms from an HTML string.

        Parameters:
            html (str): The HTML content from which forms will be extracted.

        Returns:
            list: A list of dictionaries, each representing a form.
        """
        forms = []
        soup = None
        try:
            soup = BeautifulSoup(html, "html.parser")
        except:
            return forms

        for form in soup.find_all("form"):

            # extract important information about form
            form_data = {
                "action": form.get("action"),
                "method": form.get("method", "get").lower(),
                "inputs": []
            }

            for input_tag in form.find_all("input"):

                # extract important information about inputs
                input_data = {
                    "name": input_tag.get("name"),
                    "type": input_tag.get("type", "text"),
                    "value": input_tag.get("value", "")
                }

                form_data["inputs"].append(input_data)
                
            forms.append(form_data)
            
        return forms
