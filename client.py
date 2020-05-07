#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import psutil
import pprint
import datetime
import platform
import warnings
from elastic import elastic

pp = pprint.PrettyPrinter(indent=4)
warnings.filterwarnings("ignore")

def get_system_data():
    print("INFO: getting system data")
    data = {}
    data.update({"server": platform.uname()[1]})
    data.update({"datetime": datetime.datetime.now()})
    data.update({"os": platform.uname()[2]})
    data.update({"uptime": datetime.datetime.fromtimestamp(psutil.boot_time())})
    data.update({"cpu_prc": psutil.cpu_percent(interval=1)})
    data.update({"mem_prc": 100 - psutil.virtual_memory()[2]})
    data.update({"disc_prc": psutil.disk_usage('/')[3]})
    data.update({"net_in": psutil.net_io_counters()[1]})
    data.update({"net_out": psutil.net_io_counters()[0]})
    data.update({"temp": psutil.sensors_temperatures()["acpitz"][0][1]})
    try:
        load = psutil.getloadavg()
    except Exception:
        load = (0, 0, 0)
    data.update({"load1": load[0]})
    data.update({"load5": load[1]})
    data.update({"load15": load[2]})

    # special case
    data.update({"work": "wfica" in (p.name() for p in psutil.process_iter())})

    pp.pprint(data)
    return data

def read_config():
    directory = os.path.dirname(os.path.realpath(__file__))
    filename = "config.yaml"
    print("INFO: using config: %s/%s" % (directory, filename))
    with open(r'%s/%s' % (directory, filename)) as file:
        documents = yaml.full_load(file)
    config = {}
    for item, doc in documents.items():
        config.update({item: doc})
    return config

if __name__ == '__main__':
    config = read_config()
    pp.pprint(config)

    if config["monitor"][0]["system"]:
        system_data = get_system_data()

    # configure backend and send data
    try:
        url = config["elastic"][0]["url"]
        username = config["elastic"][0]["user"] 
        password = config["elastic"][0]["pass"]
    except Exception as x:
        print("ERROR: found no database credentials: {0}".format(x))
    else:
        if url and username and password:
            print("INFO: sending data to elastic")
            client = elastic(url, username, password)
            client.push_data("system", system_data)
        else:
            print("ERROR: credentials are missing values")


