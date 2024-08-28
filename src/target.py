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

from src import form
from src import payload
from src import error
from src import http_client

class Target:
    http_client = None
    
    def __init__(self, url):
        """
        Initializes the Target object with a URL.

        Parameters:
            url (str): The URL of the target to be scanned.
        """
        self.url = url
        self.html = None
        self.forms = []
        self.payloads = []
        self.responses = []

    async def _get_html(self):
        """
        Fetches the HTML content of the target URL.
        """
        try:
            self.html = await self.http_client.get(self.url)
        except:
            return

    def _get_forms(self):
        """
        Parses target URL's html for forms.
        """
        if self.html:
            self.forms = form.Form.get_forms(self.html)

    def _create_payloads(self):
        """
        Creates payloads for testing based on form data and URL parameters.
        """
        for payload_char in payload.payload_chars:
            injected_urls = payload.create_injected_urls(self.url, payload_char)
            for injected in injected_urls:
                self.payloads.append({"url": injected, "data": None, "method": "get", "detected": False})

        for form in self.forms:
            for payload_char in payload.payload_chars:
                if form.details["method"].lower() == "get":
                    full_url = payload.get_full_url(self.url, form.data)
                    injected_urls = payload.create_injected_urls(full_url, payload_char)
                    for injected in injected_urls:
                        self.payloads.append({"url": injected, "data": None, "method": "get", "detected": False})
                elif form.details["method"].lower() == "post":
                    injected_data = payload.create_injected_data(form.data, payload_char)
                    for injected in injected_data:
                        self.payloads.append({"url": self.url, "data": injected, "method": "post", "detected": False})

    async def _send_payload(self, payload):
        """
        Sends a payload to the target URL and returns the server's response.

        Parameters:
            payload (dict): The payload to be sent, including URL, data, and method.

        Returns:
            str: The server's response, or None if the request fails.
        """
        try:
            if payload["method"] == "get":
                return await self.http_client.get(payload["url"], params=payload["data"])
            elif payload["method"] == "post":
                return await self.http_client.post(payload["url"], data=payload["data"])
        except:
            return None

    async def _send_payloads(self):
        """
        Sends payload(s) to the target URL.
        """
        tasks = [self._send_payload(payload) for payload in self.payloads]
        self.responses = await asyncio.gather(*tasks)

    def _detect_error_based_injection(self):
        """
        Checks if payload caused DBMS error message.
        """
        for payload, response in zip(self.payloads, self.responses):
            if response and error.detect_dbms_error(response):
                print("[SQLiF] DBMS error detected!")
                payload["detected"] = True

    @classmethod
    def init_http_client(cls, user_agent=None, proxy=None, timeout=15):
        """
        Initialises the http client.
        """
        cls.http_client = http_client.HttpClient(user_agent=user_agent, proxy=proxy, timeout=timeout)

    @classmethod
    async def close_http_client(cls):
        """
        Closes the http client.
        """
        if cls.http_client:
            await cls.http_client.close()
            cls.http_client = None

    @classmethod
    async def scan_targets(cls, targets):
        """
        Scans multiple targets concurrently.

        Parameters:
            targets (list): A list of Target objects to be scanned.
        """
        if not http_client:
            cls.init_http_client()

        print("[SQLiF] Getting target(s) HTML...")
        tasks = [target._get_html() for target in targets]
        await asyncio.gather(*tasks)

        print("[SQLiF] Scanning HTML for forms...")
        for target in targets:
            target._get_forms()

        print("[SQLiF] Crafting payload(s)...")
        for target in targets:
            target._create_payloads()

        print("[SQLiF] Sending payload(s)...")
        tasks = [target._send_payloads() for target in targets]
        await asyncio.gather(*tasks)

        print("[SQLiF] Scanning response(s) for DBMS errors...")
        for target in targets:
            target._detect_error_based_injection()
