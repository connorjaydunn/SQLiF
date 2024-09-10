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
import argparse
import datetime
import os

from src.target import Target
from src import search

def logo():
    print(r"""
    _____ _____ __    _ _____ 
   |   __|     |  |  |_|   __|
   |__   |  |  |  |__| |   __|
   |_____|__  _|_____|_|__|   
            |__|            v1.1 ~ https://github.com/connorjaydunn/SQLiF

[*] The developer is not responsible for any illegal use, including unauthorised attacks
    on websites or databases. By using this software, you agree to use it responsibly 
    and legally, and you assume full responsibility for any consequences that may arise.
    """)

def get_args():
    parser = argparse.ArgumentParser(description="SQL injection Finder (SQLiF)")

    parser.add_argument("-e", "--engine", type=str, help="Search engine")
    parser.add_argument("-t", "--target", type=str, help="Target website to scan")
    parser.add_argument("-q", "--query", type=str, help="Query to search")
    parser.add_argument("-p", "--pages", default=1, type=int, help="Number of pages for the search engine to scan")
    parser.add_argument("-o", "--output-file", type=str, help="Output file")
    parser.add_argument("--timeout", default=15, type=int, help="Timeout for target(s)")
    parser.add_argument("--user-agent", default="Mozilla/5.0 (Windows; U; Windows NT 6.0;) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/53.0.2345.233 Safari/534",
                        type=str, help="User-agent for requests to target(s)")

    return parser.parse_args()

def output_to_file(targets, output_file=None):
    if not output_file:
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
    try:
        print(f"[SQLiF] Saving output to {output_file}")
        with open(output_file, "a") as file:
            for target in targets:
                for payload in target.payloads:
                    if payload["detected"]:
                        file.write(payload["url"] + "\n")
                        if payload["data"]:
                            file.write(str(payload["data"]) + "\n")
                        file.write("\n")
    except IOError:
        print(f"[SQLiF] Failed to open file {output_file}.")
    except Exception as e:
        print(f"[SQLiF] Failed to write data to output file: {e}")   

async def sqlif(engine, target, pages, query, output_file, timeout, user_agent):
    targets = []
    if target:
        targets.append(Target(target))
        
    if query:
        if not engine or not search.is_engine_supported(engine):
            if input("[SQLiF] No search engine provided (--engine). Do you want to search with Google? [Y/N] ").lower() == "y":
                engine = "google"
            else:
                print("[SQLiF] No engine provided (--engine)")
                return
            
        print(f"[SQLiF] Scanning {pages} page(s) of {engine} search results...")
        urls, is_blocked = search.search(engine, query, pages)
        
        if is_blocked:
            print(f"[SQLiF] You have likely been blocked by {engine}. Use a different search engine (--engine), or a proxy")
        
        targets.extend(Target(url) for url in urls)
        
    if not targets:
        print("[SQLiF] Zero targets to scan")
        return
    
    Target.init_http_client(user_agent=user_agent, proxy=None, timeout=timeout)
    
    print(f"[SQLiF] Scanning {len(targets)} targets...")
    await Target.scan_targets(targets)
    
    output_to_file(targets, output_file)
    
    await Target.close_http_client()

def main():
    logo()
    args = get_args()
    asyncio.run(sqlif(**vars(args)))

if __name__ == "__main__":
    main()
