"""Upload script result to Cyberwatch for Importer"""

import os
import sys
import json
import argparse
from argparse import RawTextHelpFormatter
from configparser import ConfigParser
from datetime import datetime
import requests
from cbw_api_toolbox.cbw_api import CBWApi

WEBHOOK_URL = ""

def connect_api():
    '''Connect to the API and test connection'''
    conf = ConfigParser()
    conf.read(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), '../', 'api.conf'))
    client = CBWApi(conf.get('cyberwatch', 'url'), conf.get(
        'cyberwatch', 'api_key'), conf.get('cyberwatch', 'secret_key'))
    client.ping()
    return client


def get_cyberwatch_url():
    '''Get the Cyberwatch instance URL from api.conf'''
    conf = ConfigParser()
    conf.read(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), '../', 'api.conf'))
    return conf.get('cyberwatch', 'url')


def get_group(client, param):
    """Find group details by using a name or id with Cyberwatch api"""
    print("INFO: Looking for group details with name or id = '{}'".format(param))

    if param.isdigit():
        return client.group(str(param))

    for group in client.groups():
        if group.name == param:
            return group

    print("No group found with name or id = '{}'".format(param))
    sys.exit()

def get_servers_details(client, group):
    """Find all servers details with a specific group"""
    print("INFO: Looking for assets with group name '{}'".format(group.name))

    servers_details = []
    servers = client.servers({"group_id": group.id})

    for server in servers:
        servers_details.append(client.server(str(server.id)))

    return servers_details


def build_text(servers_details, cyberwatch_url, group):
    """Build message to send to Teams webhook"""
    print("INFO: Building webhook message")

    messages = [{
        "name": "Cyberwatch",
        "value": "Current scan of servers in group '{group}' on {time}".format(time=(datetime.now()).strftime("%B %d"),
        group=group.name)
    }]

    for server in servers_details:
        if server.cve_announcements:
            cve_links = []
            for cve in server.cve_announcements:
                cve_links.append(
                    "[{code}]({url}/cve_announcements/{code})".format(code=cve.cve_code, url=cyberwatch_url))

        messages.append({
            "name": "{server_name}".format(server_name=server.hostname),
            "value": "CVEs count: {number_of_cve} | {cve_links}".format(number_of_cve=server.cve_announcements_count,
            cve_links=str(cve_links))
        })
    return messages


def teams_webhook(webhook_url, payload_texts):
    '''Build final payload and send it to Teams Webhook'''
    for text in payload_texts:
        payload = json.dumps({
            "@type": 'MessageCard',
            "@context": 'http://schema.org/extensions',
            "summary": 'CVE',
            "themeColor": '0076D7',
            "sections": [
                {
                        "facts": [text]
                }
            ], "markdown": "true"
        })
        requests.post(webhook_url, data=payload)


def launch_script(args):
    '''Launch script'''
    client = connect_api()
    cyberwatch_url = get_cyberwatch_url()

    if args.param:
        group = get_group(client, args.param)
    else:
        raise ValueError("Please provide valid `group` argument")

    servers_details = get_servers_details(client, group)
    text = build_text(servers_details, cyberwatch_url, group)
    teams_webhook(WEBHOOK_URL, text)
    print("INFO: Done.")


def main(args=None):
    '''Main function'''

    parser = argparse.ArgumentParser(
        description="""Script using Cyberwatch API to find all current vulnerabilities of
         servers from specific group and send them to a Teams webhook""", formatter_class=RawTextHelpFormatter)

    parser.add_argument('param', metavar='group ID or group name', type=str,
                        help='Group ID or name to use in script')

    args = parser.parse_args(args)
    launch_script(args)


if __name__ == '__main__':
    main()
