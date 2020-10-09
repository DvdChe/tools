#! /usr/bin/env python

import requests
import argparse
import json
from pprint import pprint
import re
import os


def export_dashboards(args):

    r = re.compile("/")  # To workaround the / in folder or dashboard name

    if not os.path.exists("dashboards"):
        os.makedirs("dashboards")

    req_search_dashobards = requests.get(
        f"{args.host}/api/search/?query=",
        headers={"Authorization": f"Bearer {args.key}", "Accept": "application/json",},
    )
    dashboards = json.loads(req_search_dashobards.text)

    for i in dashboards:
        req = requests.get(
            f"{args.host}/api/dashboards/uid/{i['uid']}",
            headers={
                "Authorization": f"Bearer {args.key}",
                "Accept": "application/json",
            },
        )
        dashboard = json.loads(req.text)
        filename = r.sub("-", i["title"])
        print(f"Exporting dashboard {i['title']} to {filename}.json")
        folder = r.sub("-", dashboard["meta"]["folderTitle"])
        if not os.path.exists(f"dashboards/{folder}"):
            os.makedirs(f"dashboards/{folder}")
            print(f"created folder dashboards/{folder}")
        if not dashboard["meta"]["isFolder"]:
            with open(f"dashboards/{folder}/{filename}.json", "w+") as f:
                json.dump(dashboard, f, indent=4)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(help="sub-command help")

    parser_export = subparser.add_parser("export", help="export dashboards")
    parser_export.set_defaults(func=export_dashboards)
    parser_export.add_argument(
        "-k", "--key", required=True, help="Bearer token API", dest="key"
    )
    parser_export.add_argument(
        "-H", "--host", required=True, help="Grafana host", dest="host"
    )

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        print(
            f"No subcommand found. please, use {__file__} --help for more infromation"
        )
