from __future__ import annotations

import argparse
import functools
import http.server
import sys

from .models import ContentError, Site
from .render import Builder


def build(site: Site) -> int:
    try:
        written = Builder(site).build()
    except ContentError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"built {len(written)} pages into {site.dist_dir}")
    return 0


def serve(site: Site, port: int) -> int:
    status = build(site)
    if status:
        return status
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=site.dist_dir)
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"serving on http://127.0.0.1:{port}/ (Ctrl+C to stop)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sitegen")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="build the site into dist/")
    serve_parser = sub.add_parser("serve", help="build and serve locally")
    serve_parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    site = Site()
    if args.command == "serve":
        return serve(site, args.port)
    return build(site)


if __name__ == "__main__":
    sys.exit(main())
