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

from src.search_engines.engines import *

supported_engines = ["aol", "ask", "bing", "brave", "dogpile", "duckduckgo", "google", "metager", "mojeek", "qwant", "startpage", "torch", "yahoo"]

def is_engine_supported(engine):
    """
    Checks if the specified search engine is supported.

    Parameters:
        engine (str): The name of the search engine to check.

    Returns:
        bool: True if the engine is supported, False otherwise.
    """
    if engine.lower() in supported_engines:
        return True
    print(f"[SQLiF] {engine} is not supported")
    return False

def search(engine, query, pages=1):
    """
    Performs a search using the specified search engine.

    Parameters:
        engine (str): The search engine to use.
        query (str): The search query string.
        pages (int): Number of pages to search.

    Returns:
        tuple: A tuple containing:
            - list: A list of URLs from the search results.
            - bool: A boolean indicating if the user is blocked or not.

        Returns (None, False) if the engine is not supported.
    """
    match engine.lower():
        case "aol":
            engine = Aol()
        case "ask":
            engine = Ask()
        case "bing":
            engine = Bing()
        case "brave":
            engine = Brave()
        case "dogpile":
            engine = Dogpile()
        case "duckduckgo":
            engine = Duckduckgo()
        case "google":
            engine = Google()
        case "metager":
            engine = Metager()
        case "mojeek":
            engine = Mojeek()
        case "qwant":
            engine = Qwant()
        case "startpage":
            engine = Startpage()
        case "torch":
            engine = Torch()
        case "yahoo":
            engine = Yahoo()
        case _:
            print(f"[SQLiF] {engine} is not supported")
            return None, False
    engine.disable_console()
    results = engine.search(query, pages=pages)
    return results.links(), engine.is_banned
