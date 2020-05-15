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

def get_kube_data(name):
    data = {}
    try:
        from kubernetes import client, config
        try: config.load_incluster_config()
        except: config.load_kube_config()
        version = client.VersionApi()
        v1 = client.CoreV1Api()
    except Exception as x:
        print("ERROR: Could not connect to kubernetes: {0}".format(x))
    else:
        data.update({"datetime": datetime.datetime.utcnow()})
        data.update({"k8s_name": name})
        data.update({"k8s_version": version.get_code().git_version})

        nodes = v1.list_node().items
        cpu = 0; mem = 0 
        for node in nodes:
            try:
                cpu += int(node.status.capacity["cpu"])
                mem += int(node.status.capacity["memory"][:-2])
            except Exception:
                continue
        
        data.update({"k8s_cpu": cpu})
        data.update({"k8s_memory": int(mem/1024/1024)})
        data.update({"k8s_nodes": len(v1.list_node().items)})
        data.update({"k8s_pods": len(v1.list_pod_for_all_namespaces().items)})
        data.update({"k8s_pvcs": len(v1.list_persistent_volume_claim_for_all_namespaces().items)})
        #data.update({"k8s_secrets": len(v1.list_secret_for_all_namespaces().items)})
        data.update({"k8s_services": len(v1.list_service_for_all_namespaces().items)})

    return data

def get_docker_data():
    data = {}
    try:
        import docker
        client = docker.from_env()
    except Exception as x:
        print("ERROR: Could not connect to docker daemon: {0}".format(x))
    else:
        data.update({"dck_version": client.version()["Components"][0]["Version"]})
        data.update({"dck_containers": len(client.containers.list())})
        data.update({"dck_images": len(client.images.list())})

    return data

def get_system_data():
    print("INFO: getting system data")
    data = {}
    data.update({"server": platform.uname()[1]})
    data.update({"datetime": datetime.datetime.utcnow()})
    data.update({"os": platform.uname()[2]})
    data.update({"uptime": datetime.datetime.fromtimestamp(psutil.boot_time())})
    data.update({"cpu_prc": round(psutil.cpu_percent(interval=1), 2)})
    data.update({"mem_prc": round(psutil.virtual_memory()[2], 2)})
    data.update({"disc_prc": round(psutil.disk_usage('/')[3], 2)})
    data.update({"net_in": psutil.net_io_counters()[1]})
    data.update({"net_out": psutil.net_io_counters()[0]})

    sensors = ("bcm2835_thermal", "acpitz", "cpu-thermal", "radeon")
    data.update({"temp": 0})
    for sensor in sensors:
        try: data.update({"temp": psutil.sensors_temperatures()[sensor][0][1]})
        except: continue
        else: break

    try:
        load = psutil.getloadavg()
    except Exception:
        load = (0, 0, 0)
    data.update({"load1": load[0]})
    data.update({"load5": load[1]})
    data.update({"load15": load[2]})

    # special case
    data.update({"work": "wfica" in (p.name() for p in psutil.process_iter())})

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

def update_client():
    if datetime.datetime.utcnow().minute == 59:
        print("INFO: updating repo")
        os.system("git pull")

if __name__ == '__main__':
    config = read_config()
    pp.pprint(config)

    # configure backend and send data
    try:
        url = config["elastic"]["url"]
        username = config["elastic"]["user"] 
        password = config["elastic"]["pass"]
    except Exception as x:
        print("ERROR: found no database credentials: {0}".format(x))
    else:
        data = {}
        print("INFO: collecting data ...")
        if config["monitor"]["system"]["enabled"]:
            data.update(get_system_data())
            if config["monitor"]["system"]["updater"]: update_client()
        if config["monitor"]["docker"]["enabled"]:
            data.update(get_docker_data())
        if config["monitor"]["kube"]["enabled"]:
            data.update(get_kube_data(config["monitor"]["kube"]["name"]))

        print("INFO: sending data to elastic ...")
        pp.pprint(data)

        if url and username and password:
            client = elastic(url, username, password)
            client.push_data(data)
        else:
            print("ERROR: credentials are missing values")


