from src.thirdparty.search_engines.engines import *

supported_engines = ["aol", "ask", "bing", "brave", "dogpile", "duckduckgo", "google", "metager", "mojeek", "qwant", "startpage", "torch", "yahoo"]

class SearchHandler:
    @staticmethod
    def search(engine, query, pages=1):
        """
        Fetches results from specified search engine using specified query.

        Parameters:
            engine (str): The search engine to search with.
            query (str): The query to search for.
            pages (int): The number of pages to gather results from (default: 1)
        Returns:
            list, bool: A list of results, and a boolean value if blocked by the search engine.
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
                print(f"{engine} is not supported")
                return None, False
        engine.disable_console()
        results = engine.search(query, pages=pages)
        return results.links(), engine.is_banned
