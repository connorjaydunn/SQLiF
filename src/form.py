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

import asyncio
import aiohttp
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

class Form:
    def __init__(self, form):
        self.form = form
        self.details = None
        self.data = None

    def _get_form_details(self):
        """
        Extracts details about the form's inputs, action, and method.
        """
        inputs = []
        for input_tag in self.form.find_all("input"):
            input_detail = {
                "type": input_tag.get("type", ""),
                "name": input_tag.get("name", ""),
                "value": input_tag.get("value", "")
            }
            inputs.append(input_detail)
        
        form_details = {
            "action": self.form.get("action"),
            "method": self.form.get("method", "get"),
            "inputs": inputs
        }
        self.details = form_details

    def _get_input_data(self):
        """
        Prepares a dictionary of input data to be submitted with the form.

        Returns:
            dict: A dictionary where keys are input names and values are input values.
        """
        data = {}
        for input_tag in self.details["inputs"]:
            if input_tag["type"] == "hidden" or input_tag["value"]:
                data[input_tag["name"]] = input_tag["value"]
            elif input_tag["type"] != "submit":
                data[input_tag["name"]] = ""
        return data

    @staticmethod
    def get_forms(html):
        """
        Parses an HTML page and extracts all forms.

        Parameters:
            html (str): The HTML content of the page.

        Returns:
            list: A list of Form objects, each representing an HTML form found on the page.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            soup = BeautifulSoup(html, "html.parser")
        forms = []
        for form_element in soup.find_all("form"):
            form = Form(form_element)
            form._get_form_details()
            form.data = form._get_input_data()
            forms.append(form)
        return forms
