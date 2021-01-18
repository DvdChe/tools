#! /usr/bin/env python

import requests
import argparse
import json
from pprint import pprint
import re
import os


def export_dashboards(args):

    r = re.compile("/")  # To workaround the / in folder or dashboard name

    req_search_dashobards = requests.get(
        f"{args.host}/api/search/?query=",
        headers={
            "Authorization": f"Bearer {args.key}",
            "Accept": "application/json",
        },
    )
    dashboards = json.loads(req_search_dashobards.text)
    for i in dashboards:
        if args.export_folder:
            if i["type"] == "dash-folder" and i["title"] != args.export_folder:
                continue
            if i["type"] == "dash-db" and (
                "folderTitle" not in i or i["folderTitle"] != args.export_folder
            ):
                continue
        req = requests.get(
            f"{args.host}/api/dashboards/uid/{i['uid']}",
            headers={
                "Authorization": f"Bearer {args.key}",
                "Accept": "application/json",
            },
        )
        dashboard = json.loads(req.text)
        filename = r.sub("-", i["title"])
        folder = r.sub("-", dashboard["meta"]["folderTitle"])
        output_dir = args.output_dir if args.output_dir else "./dashboards"
        folder_path = f"{output_dir}/{folder}"
        print(f"Exporting dashboard {i['title']} to {folder_path}/{filename}.json")
        if not os.path.exists(f"{folder_path}"):
            os.makedirs(f"{folder_path}")
            print(f"created folder {folder_path}")
        if dashboard["meta"]["type"] == "db":
            with open(f"{folder_path}/{filename}.json", "w+") as f:
                json.dump(dashboard, f, indent=4, sort_keys=True)


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
    # Pay attention to the default folder (TODO: handle default folder)
    parser_export.add_argument(
        "-F", "--folder", required=False, help="Folder to export", dest="export_folder"
    )
    parser_export.add_argument(
        "-o", "--output-dir", required=False, help="Output directory", dest="output_dir"
    )

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        print(
            f"No subcommand found. please, use {__file__} --help for more infromation"
        )
