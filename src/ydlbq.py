#!/usr/bin/env python3

import controller
import sys
from urllib.parse import urlparse

YOUTUBE_CNAME = "youtube.com"

def usage():
    """Prints how to use the script to stdout"""
    print("Usage: ./ydlbq.py <URL>")

def main():
    args = sys.argv
    if len(args) < 2:
        usage()
        return -1
    try:
        urlparse(args[1])
        if args[1].find(YOUTUBE_CNAME) == -1:
            raise ValueError

        _controller = controller.Controller(args[1])
        print(_controller.get_command_for_best_quality())

    except ValueError as ve:
        print(f"Malformed URL or the domain is not {YOUTUBE_CNAME}!")
        print(ve)
        usage()
        return -2

if __name__ == "__main__":
    main()
