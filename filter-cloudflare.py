#!/usr/bin/env python
import argparse
import ipaddress
import multiprocessing
import shutil
import socket
import sys
import urllib
from email.utils import formatdate
from functools import lru_cache, partial
from pathlib import Path
from urllib.request import Request, urlopen

__copyright__ = "Copyright 2024, Sergey M"
__license__ = "MIT"
__maintainer__ = "Sergey M"

RESET = "\x1b[m"
BLACK = "\x1b[30m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
PURPLE = "\x1b[35m"
CYAN = "\x1b[36m"
WHITE = "\x1b[37m"

CLOUD_CACHE_PATH = Path.home() / ".cache" / "clowdflare"
CLOUD_IPSV4_PATH = CLOUD_CACHE_PATH / "ips-v4"
CLOUD_IPSV6_PATH = CLOUD_CACHE_PATH / "ips-v6"
CLOUD_IPSV4_URL = "https://www.cloudflare.com/ips-v4/"
CLOUD_IPSV6_URL = "https://www.cloudflare.com/ips-v6/"


stderr = partial(print, file=sys.stderr)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-H",
        "--host",
        help="target host",
        dest="hosts",
        default=[],
        nargs="*",
    )
    parser.add_argument(
        "-l",
        "--list",
        help="hosts list",
        default="-",
        type=argparse.FileType(),
    )
    parser.add_argument(
        "-p",
        "--proc",
        help="max number of parallel processes",
        default=max(multiprocessing.cpu_count() - 1, 2),
        type=int,
    )
    parser.add_argument(
        "-F",
        "--force-download-ips",
        "--force-download",
        "--force",
        help="force download cloudflare servers ip lists",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-S",
        "--skip-download-ips",
        "--skip-download",
        help="skip download cloudflare servers ip lists",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    return parser.parse_args()


def main(argv=None):
    args = parse_args(argv=argv)

    hosts = args.hosts.copy()

    if not args.list.isatty():
        hosts.extend(map(str.strip, args.list))

    if not args.skip_download_ips:
        for url, path in [
            (CLOUD_IPSV4_URL, CLOUD_IPSV4_PATH),
            (CLOUD_IPSV6_URL, CLOUD_IPSV6_PATH),
        ]:
            download_file(url, path, args.force_download_ips)

    proc_num = min(args.proc, len(hosts))

    stderr(
        YELLOW,
        "total hosts: ",
        len(hosts),
        "; parallel processes: ",
        proc_num,
        RESET,
        sep="",
    )
    with multiprocessing.Pool(proc_num) as pool:
        try:
            for host, checked in pool.imap_unordered(check_host, hosts):
                if checked:
                    print(host)
                else:
                    stderr(PURPLE + "skip host:", host + RESET)
            stderr(YELLOW + "Finished!" + RESET)
        except KeyboardInterrupt:
            stderr(YELLOW + "Program interrupted by user..." + RESET)


@lru_cache
def get_cloudflare_subnets():
    rv = []
    for path, ip_net in [
        (CLOUD_IPSV4_PATH, ipaddress.IPv4Network),
        (CLOUD_IPSV6_PATH, ipaddress.IPv6Network),
    ]:
        for ip_mask in filter(None, map(str.strip, path.open())):
            rv.append(ip_net(ip_mask))
    return rv


def get_ip4(host, port=0):
    return next(
        filter(
            lambda x: x[0] == socket.AF_INET,
            socket.getaddrinfo(host, port),
        )
    )[4][0]


def check_cloudflare(host):
    ip = ipaddress.IPv4Address(get_ip4(host))
    for subnet in get_cloudflare_subnets():
        stderr(
            CYAN
            + "check {} ({}) in cloudflare subnet {}: {}".format(
                host, ip.compressed, subnet.compressed, ["-", "+"][ip in subnet]
            )
            + RESET
        )
        if ip in subnet:
            return True
    return False


def check_host(host):
    try:
        if not check_cloudflare(host):
            return host, True
        stderr(PURPLE + "detected cloudflare: " + host + RESET)
    except socket.gaierror:
        stderr(PURPLE + "host ip address not found: " + host + RESET)
    return host, False


def download_file(url, path, force=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    }
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since
    if not force and path.exists():
        # Дата может быть только в GMT, например, 'Fri, 19 Jan 2024 22:22:03 GMT'
        headers |= {
            "If-Modified-Since": formatdate(path.stat().st_mtime, usegmt=True),
        }

    req = Request(url, headers=headers)
    try:
        with urlopen(req) as resp:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb+") as fp:
                shutil.copyfileobj(resp, fp)
            stderr(GREEN + "url " + url + " retrieved as " + str(path) + RESET)
            return True
    except urllib.error.URLError as err:
        # Если файл на сервере не был модифицирован
        if err.code == 304:
            stderr(
                PURPLE + "skip download: resource",
                url,
                "is not modified" + RESET,
            )
        else:
            stderr(RED + str(err) + RESET)
        return False


if "__main__" == __name__:
    sys.exit(main())
