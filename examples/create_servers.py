"""
Script to create multiple agentless connection with a credential ID and groups
"""

import os
from configparser import ConfigParser
from cbw_api_toolbox.cbw_api import CBWApi

ADDRESSES = [] # List of addresses to create agentless connection ( ["adress1","adress2"]...)
CREDENTIALS_ID = '' # Set of stored credentials to use for agentless connection
GROUP_NAMES = '' # Groups to be added to the assets ("group" or "groupA, groupB, groupC"...)

def connect_api():
    '''Connect to the API and test connection'''
    conf = ConfigParser()
    conf.read(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), '..', 'api.conf'))
    client = CBWApi(conf.get('cyberwatch', 'url'), conf.get(
        'cyberwatch', 'api_key'), conf.get('cyberwatch', 'secret_key'))

    client.ping()
    return client

def create_servers(addresses, credential_id, groups, client):
    '''Create agentless connection with credential id and groups'''
    for address in addresses:
        print("INFO: Creating agentless connection for {}".format(address))
        params = {
        "type": "CbwRam::RemoteAccess::Ssh::WithKey",
        "address": address,
        "port": "22",
        "credential_id": credential_id,
        "node_id": "1",
        "server_groups": groups
        }
        client.create_remote_access(params)

def launch_script():
    '''Launch script'''
    client = connect_api()
    create_servers(ADDRESSES, CREDENTIALS_ID, GROUP_NAMES, client)

launch_script()
