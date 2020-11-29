#! /usr/bin/env python

import argparse

from json import load
from aiohttp.web import run_app
from app import create_app

with open('utils/secret.json') as json_file:
    data: dict = load(json_file)


def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path')
    parser.add_argument('--port')
    return parser.parse_args()


if __name__ == '__main__':
    if data['debug']:
        app = create_app()
        run_app(app)
    else:
        args = get_opts()
        app = create_app()
        run_app(app, path=args.path, port=args.port)
