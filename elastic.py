#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

class elastic():

    def __init__(self, url="", username="", password=""):
        self.url = url
        self.username = username
        self.password = password
        self.es = None
        try:
            from elasticsearch import Elasticsearch
            self.es = Elasticsearch(self.url,
                      http_auth=(self.username, self.password),
                      scheme="https", port=443)
        except Exception as x:
            print("ERROR: could not connect to database: %s", x)
        else:
            self.create_system_index()


    def create_system_index(self):
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
                }
            }
        }
        self.es.indices.create(index="system", ignore=400, body=settings)


    def push_data(self, index, data):
        try:
            self.es.index(index=index, body=data)
        except Exception:
            print("ERROR: could not send data (connection issue)")
