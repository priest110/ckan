#!/usr/bin/env python
import os
import pprint
api_url = 'http://dockerhost:5000/api/3/action/'
txt_dataset_folder = '/home/ruizinho/Desktop/Universidade/Tese/gsd/SAIL_SD_GNSS_NMEA'
csv_dataset_folder = '/home/ruizinho/Desktop/Universidade/Tese/gsd/preprocessed'

# HEADERS #

import pathlib
import requests

# AUX INFO #

api_token_local = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NDg2MDI0OTUsImp0aSI6IkYza2k1eWZfZ0JWQTdENG5nOXNKSXh5SW9wSzk1SmowS1g0ckNCR1U0bGloRy1FcGRuYUpRYW5kME5GLXA5Ql9qd2FMUEtfWV8xckg5N0lpIn0.mvGhowtnwa2eIB-IfVLVky18coMWvZHh9Fsb66vNZcs'
api_token_docker = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'
header = {
    "X-CKAN-API-Key": api_token_docker,
}


# DATA #

# Dataset to update (files .txt)
def up_data_txt(folder_path, file_name, file_type):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    data = {
        "match__name": folder_name,
        "update__resources__extend": '[{"name": "' + file_name + ' ", "format": "' + file_type + '"}]'
    }
    return data


def up_data_csv(folder_path, file_name):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    data = {
        "match__name": folder_name,
        "update__resources__extend": '[{"name": "' + file_name + ' "}]'
    }
    return data


def new_data_txt(folder_path):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    data = {
        "name": folder_name,
        "notes": "This dataset contains GNSS_NMEA_yyyymmdd_hh files (where yyyy is the year, mm the month, dd the day, and HH the hour), each including the hourly logs from the antennas composign the GNSS system, in the NMEA (National Marine Electronics Association) standard format.",
        "title": "SAIL Project - GNSS_NMEA_" + folder_name.rpartition('_')[-1],
        "private": False,
        "tags": [{"name": "research"}],
        "owner_org": "inesctec",
        "groups": [{"name": "sail-project"}]
    }
    return data


def new_data_csv(dataset_name):
    dataset_name_lower = dataset_name.lower()
    data = {
        "name": dataset_name_lower,
        "notes": "This dataset contains CSV files with information about stuff like gamma or solar radiation",
        "title": "SAIL Project - " + dataset_name.split("_", 1)[1],
        "private": False,
        "tags": [{"name": "research"}],
        "owner_org": "inesctec",
        "groups": [{"name": "sail-project"}]
    }
    return data


# REQUEST FUNCTIONS #

# Update multiple datasets
def import_txt_datasets():
    for root, dirs, files in os.walk(txt_dataset_folder):
        if root != txt_dataset_folder:
            create_dataset(root, "txt")
            for name in files:
                update_dataset(root, name, "txt")


def import_csv_datasets():
    for root, dirs, files in os.walk(csv_dataset_folder):
        create_dataset("SAIL_PD_CSV", "csv")
        for name in files:
            update_dataset(root, name, "csv")


# Create new dataset
def create_dataset(folder_path, type_of):
    if type_of == 'csv':
        create_request = requests.post(api_url + 'package_create', json=new_data_csv(folder_path), headers=header)
    else:
        create_request = requests.post(api_url + 'package_create', json=new_data_txt(folder_path), headers=header)
    print(create_request.json())
    assert create_request.ok
    assert create_request.json()["success"]
    pprint.pprint(create_request.json()["result"])


# Update specific dataset
def update_dataset(folder_path, file_name, type_of):
    filepath = pathlib.Path(os.path.join(folder_path, file_name))
    fd = filepath.open("rb")
    if type_of == "csv":
        update_request = requests.post(api_url + 'package_revise', data=up_data_csv("sail_pd_csv", file_name),
                                       files=[("update__resources__-1__upload", (file_name, fd))],
                                       headers=header)
    else:
        aux, file_type = os.path.splitext(os.path.join(folder_path, file_name))
        if not file_type:
            file_type = "txt"
        update_request = requests.post(api_url + 'package_revise',
                                       data=up_data_txt(folder_path, file_name, file_type),
                                       files=[("update__resources__-1__upload", (file_name, fd))],
                                       headers=header)
    print(update_request.json())
    assert update_request.ok
    assert update_request.json()["success"]
    pprint.pprint(update_request.json()["result"])
    update_resource_views(update_request.json()["result"]["package"]["resources"][-1])
    push_resource(update_request.json()["result"]["package"]["resources"][-1])


# Update views of specific resource
def update_resource_views(resource):
    update_request = requests.post(api_url + 'resource_create_default_resource_views',
                                   json={"resource": resource},
                                   headers=header)
    print(update_request.json())
    assert update_request.ok
    assert update_request.json()["success"]
    pprint.pprint(update_request.json()["success"])


# Push resource to DataStore
def push_resource(resource):
    push_request = requests.post(api_url + 'datastore_create',
                                 json={"resource": resource},
                                 headers=header)
    print(push_request.json())
    assert push_request.ok
    assert push_request.json()["success"]
    pprint.pprint(push_request.json()["success"])


# Return the metadata of a resource
def get_resource():
    get_request = requests.get(api_url + 'resource_show', {'id': 'bd005382-204c-44ad-8160-e4d99bdfc663'})
    assert get_request.ok
    assert get_request.json()["success"]
    pprint.pprint(get_request.json()["result"])


# MAIN #

import_csv_datasets()
# import_txt_datasets()
# get_resource()
