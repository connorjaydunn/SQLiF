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

import aiohttp

class HttpClient:
    def __init__(self, user_agent=None, proxy=None, timeout=30):
        """
        Initializes the HTTPClient with optional user-agent, proxy, and timeout settings.

        Parameters:
            user_agent (str): The User-Agent string to include in requests.
            proxy (str): The proxy URL to use for requests.
            timeout (int): The timeout in seconds for HTTP requests.
        """
        self.user_agent = user_agent
        self.proxy = proxy
        self.timeout = timeout
        self.session = None

    async def _create_session(self):
        """
        Asynchronously creates a ClientSession if it doesn't already exist.
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers={'User-Agent': self.user_agent} if self.user_agent else {})

    async def get(self, url, params=None):
        """
        Sends a GET request.

        Parameters:
            url (str): The URL to send the GET request to.
            params (dict): Optional dictionary of query parameters to include in the request.

        Returns:
            str: The response text, or None if the request fails.
        """
        await self._create_session()
        async with self.session.get(url, params=params, proxy=self.proxy, timeout=self.timeout) as response:
            return await response.text()

    async def post(self, url, data=None):
        """
        Sends a POST request.

        Parameters:
            url (str): The URL to send the POST request to.
            data (dict): Optional dictionary of data to include in the request body.

        Returns:
            str: The response text, or None if the request fails.
        """
        await self._create_session()
        async with self.session.post(url, data=data, proxy=self.proxy, timeout=self.timeout) as response:
            return await response.text()

    async def close(self):
        """
        Closes the ClientSession.
        """
        if self.session:
            await self.session.close()
            self.session = None
