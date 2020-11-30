#! /usr/bin/env python

import argparse
import yaml

from aiohttp.web import run_app
from app import create_app

with open('utils/configs_sample.yaml') as f:
    data: dict = yaml.load(f, Loader=yaml.FullLoader)

DEBUG: bool = data['APP']['global_configs']['debug']


def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path')
    parser.add_argument('--port')
    return parser.parse_args()


if __name__ == '__main__':
    if DEBUG:
        app = create_app()
        run_app(app)
    else:
        args = get_opts()
        app = create_app()
        run_app(app, path=args.path, port=args.port)
