#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime

class elastic():

    def __init__(self, url="", username="", password=""):
        self.url = url
        self.username = username
        self.password = password
        self.suffix = ""
        self.index = "system"
        self.es = None
        try:
            from elasticsearch import Elasticsearch
            self.es = Elasticsearch(self.url,
                      http_auth=(self.username, self.password),
                      scheme="https", port=443)
        except Exception as x:
            print("ERROR: could not connect to database:", x)
        else:
            self.check_index()


    def check_index(self):
        # needed for long term runs
        if not self.suffix == self.create_suffix():
            self.suffix = self.create_suffix()
            self.create_index()
            self.update_index()


    def create_suffix(self):
        # create daily index
        now = datetime.datetime.utcnow()
        year = str(now.year)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        return "-%s%s%s" % (year, month, day)


    def update_index(self):
        settings = {
            "settings": { "number_of_replicas": 0 }
        }
        self.es.indices.put_settings(index=self.index+self.suffix, ignore=404, body=settings)


    def create_index(self):
        settings = {
            "settings": {
                "number_of_shards": 1, 
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "server": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "datetime": {"type": "datetime"},
                    "uptime": {"type": "datetime"},
                    "os": {"type": "text"},
                    "cpu_prc": {"type": "float"},
                    "mem_prc": {"type": "float"},
                    "disc_prc": {"type": "float"},
                    "net_in": {"type": "float"},
                    "net_out": {"type": "float"},
                    "temp": {"type": "float"},
                    "load1": {"type": "float"},
                    "load5": {"type": "float"},
                    "load15": {"type": "float"},
                    "work": {"type": "bool"},
                    "dck_version": {"type": "text"},
                    "dck_containers": {"type": "integer"},
                    "dck_images": {"type": "integer"},
                    "k8s_name": {"type": "text"},
                    "k8s_version": {"type": "text"},
                    "k8s_cpu": {"type": "integer"},
                    "k8s_memory": {"type": "integer"},
                    "k8s_nodes": {"type": "integer"},
                    "k8s_pods": {"type": "integer"},
                    "k8s_pvcs": {"type": "integer"},
                    "k8s_secrets": {"type": "integer"},
                    "k8s_services": {"type": "integer"},
                }
            }
        }
        self.es.indices.create(index=self.index+self.suffix, ignore=400, body=settings)

    def push_data(self, data):
        self.check_index()
        try:
            print("INFO: Using index: %s" % (self.index+self.suffix))
            self.es.index(index=self.index+self.suffix, body=data)
        except Exception as x:
            print("ERROR: could not send data to index %s:" % (self.index+self.suffix), x)
