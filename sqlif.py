from src.error_based_scan import ErrorBasedScan
from src.time_based_scan import TimeBasedScan
from src.print_handler import PrintHandler
from src.target import Target
from src.googlesearch import search
from src.util import filter_duplicate_urls
import colorama
import threading
import math
import os
import argparse
import sys

def print_banner():
    print(colorama.Fore.LIGHTYELLOW_EX + r"""
 _____ _____ __    _ _____ 
|   __|     |  |  |_|   __|
|__   |  |  |  |__| |   __|
|_____|__  _|_____|_|__|   
         |__|             """ + colorama.Style.RESET_ALL + "v2.3.0 <https://github.com/connorjaydunn/SQLiF>")

def print_disclaimer():
    print(colorama.Fore.LIGHTRED_EX + """
[*] The developer is not responsible for any illegal use, including unauthorized attacks
    on websites or databases. By using this software, you agree to use it responsibly 
    and legally, and you assume full responsibility for any consequences that may arise.
    """ + colorama.Style.RESET_ALL)

def scan(targets, cookies_scan, headers_scan, crawl, error_scan, time_scan, body_scan, query_scan, output_dir=None):
    """
    Uses SQLiScanners to scan the target(s) for SQL injection vulnerabilities.

    Parameters:
        targets (list): List of Target objects to be scanned.
        cookies_scan (bool): Toggle for scanning of cookie-based injections.
        headers_scan (bool): Toggle for scanning of header-based injections.
        crawl (bool): Toggle for crawling targets for forms.
        error_scan (bool): Toggle for scanning of error-based injections.
        time_scan (bool): Toggle for scanning of time-based injections.
        body_scan (bool): Toggle for scanning of body-based injections.
        query_scan (bool): Toggle for scanning of query-based injections.
        output_dir (str, optional): Output file directory.
    """
    scan_types = []
    if error_scan:
        scan_types.append(ErrorBasedScan(output_dir))
    if time_scan:
        scan_types.append(TimeBasedScan(output_dir))

    for target in targets:
        if not target.test_connection():
            continue

        # crawl URL for forms & scan them
        if crawl:
            for sub_target in target.crawl_forms():
                for scan_type in scan_types:
                    if not scan_type.detect_false_positive(sub_target):
                        if query_scan:
                            scan_type.query_scan(sub_target)
                        if body_scan:
                            scan_type.body_scan(sub_target)
                        if headers_scan:
                            scan_type.header_scan(sub_target)
                        if cookies_scan:
                            scan_type.cookie_scan(sub_target)

        # iterate over scan types and scan target
        for scan_type in scan_types:
            if not scan_type.detect_false_positive(target):
                if query_scan:
                    scan_type.query_scan(target)
                if body_scan:
                    scan_type.body_scan(target)
                if headers_scan:
                    scan_type.header_scan(target)
                if cookies_scan:
                    scan_type.cookie_scan(target)

def parse_args():
    """
    Parses command-line arguments.

    Returns:
        dict: Dictionary of the parsed arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Query to search"
    )

    parser.add_argument(
        "-s", "--start-result",
        type=int,
        default=0,
        help="Starting index of results to scan (default: 0)"
    )

    parser.add_argument(
        "-n", "--num-results",
        type=int,
        default=30,
        help="Number of results to retrieve starting from the start index (default: 30)"
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help=f"Number of threads to use (default: 1)"
    )

    parser.add_argument(
        "-t", "--target",
        type=str,
        help=f"Specific target to scan"
    )

    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        help="File to save scan results (default: current working directory)"
    )

    parser.add_argument(
        "--no-error-scan",
        action="store_false",
        help=f"Disable error-based injection scanning"
    )

    parser.add_argument(
        "--no-time-scan",
        action="store_false",
        help=f"Disable time-based injection scanning"
    )

    parser.add_argument(
        "--no-query-scan",
        action="store_false",
        help=f"Disable query-based injection scanning"
    )

    parser.add_argument(
        "--no-body-scan",
        action="store_false",
        help=f"Disable body-based injection scanning"
    )

    parser.add_argument(
        "--cookies-scan",
        action="store_true",
        help=f"Enable cookie-based injection scanning"
    )

    parser.add_argument(
        "--headers-scan",
        action="store_true",
        help=f"Enable header-based injection scanning"
    )

    parser.add_argument(
        "--crawl",
        action="store_true",
        help=f"Enable crawling for forms"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    colorama.init()
    args = parse_args()

    print_banner()
    print_disclaimer()
    
    threads = []
    targets = []

    # if target specified, add it to the targets array
    if args.target:
        targets.append(Target(args.target))

    # if query specified, execute & collect targets
    if args.query:
        PrintHandler.print_message(f"Fetching URL(s)...", "INFO", "blue")

        # search for query & filter duplicate urls
        search_results = filter_duplicate_urls(list(search(query=args.query, start=args.start_result, stop=args.start_result+args.num_results)))
        
        for url in search_results:
            targets.append(Target(url))

    # check for at least one target, exit if not
    if len(targets) == 0:
        PrintHandler.print_message("No Targets Found. If Using -q, The Search Engine May Have Blocked You!", "WARNING", "red")
        sys.exit()

    PrintHandler.print_message(f"Scanning {len(targets)} Target(s)...", "INFO", "blue")

    # calculate the number of targets to handle per thread
    num_jobs_per_thread = math.ceil(len(targets) / args.threads)

    for i in range(args.threads):

        # assign a portion of the targets to this thread
        thread_targets = targets[i * num_jobs_per_thread:(i + 1) * num_jobs_per_thread]

        # ensure thread_targets is not empty before creating the thread
        if not thread_targets:
            continue

        # define the thread and assign it a scanning task
        thread = threading.Thread(
            target=scan,
            args=(
                thread_targets,
                args.cookies_scan,
                args.headers_scan,
                args.crawl,
                args.no_error_scan,
                args.no_time_scan,
                args.no_body_scan,
                args.no_query_scan,
                args.output_dir
            )
        )

        threads.append(thread)
        thread.start()

    # wait for all threads to complete their scanning
    for thread in threads:
        thread.join()

    PrintHandler.print_message("Scan Completed!", "INFO", "blue")

    if args.output_dir:
        log_path = args.output_dir
    else:
        log_path = os.path.join(os.getcwd(), "sqlif_output.txt")

    PrintHandler.print_message(f"Results @ {log_path}", "INFO", "blue")
