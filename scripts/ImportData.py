#!/usr/bin/env python
import os
import pprint
import pathlib
import random

import requests

# AUX INFO #

api_url = 'http://dockerhost:5000/api/3/action/'
txt_dataset_folder = '/home/ruizinho/Desktop/Universidade/Tese/gsd/SAIL_SD_GNSS_NMEA'
csv_dataset_folder = '/home/ruizinho/Desktop/Universidade/Tese/gsd/SAIL_PD_CSV'
api_token_local = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NDg2MDI0OTUsImp0aSI6IkYza2k1eWZfZ0JWQTdENG5nOXNKSXh5SW9wSzk1SmowS1g0ckNCR1U0bGloRy1FcGRuYUpRYW5kME5GLXA5Ql9qd2FMUEtfWV8xckg5N0lpIn0.mvGhowtnwa2eIB-IfVLVky18coMWvZHh9Fsb66vNZcs'
api_token_docker = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'
header = {
    "X-CKAN-API-Key": api_token_docker,
}


# DATA OBJECTS #

# Metadata to update dataset
def up_data(folder_path, file_name, file_type):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    data = {
        "match__name": folder_name,
        "update__resources__extend": '[{"name": "' + file_name + ' "}]' if file_type == "csv" else '[{"name": "' + file_name + ' ", "format": "' + file_type + '"}]'
    }
    return data


# Metadata to create dataset
def new_data(folder_path, type_of):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    data = {
        "name": folder_name,
        "notes": "This dataset contains CSV files with information about stuff like gamma or solar radiation." if type_of == "csv" else "This dataset contains GNSS_NMEA_yyyymmdd_hh files (where yyyy is the year, mm the month, dd the day, and HH the hour), each including the hourly logs from the antennas composign the GNSS system, in the NMEA (National Marine Electronics Association) standard format.",
        "title": "SAIL Project - " + folder_path.rpartition('/')[-1].split("_", 1)[1],
        "private": False,
        "tags": [{"name": "research"}],
        "owner_org": "inesctec",
        "groups": [{"name": "sail-project"}]
    }
    return data


# AUX FUNCTIONS

# Check if dataset and resource exists
#   -1 dataset (and, consequently, resource) don't exist, so we have to create dataset and its resources
#   0 resource don't exist, so we have to update dataset resources
#   1 resource exists
def exists(dataset_folder, resource_name):
    resources = get_resources((dataset_folder.rpartition('/')[-1]).lower())
    if resources != -1:
        for root, dirs, files in os.walk(dataset_folder):
            if resource_name in files:
                return 1
            else:
                return 0
    else:
        return -1


# Choose random dataset and resource from local to upload
def pick_random():
    types = ["csv", "txt"]
    type_of = random.choice(types)
    dataset_folder = ""
    resource_name = ""
    if type_of == "csv":
        for root, dirs, files in os.walk(csv_dataset_folder):
            dataset_folder = root
            index_file = random.randint(0, len(files) - 1)
            resource_name = files[index_file]
    else:
        for root, dirs, files in os.walk(txt_dataset_folder):
            if root == txt_dataset_folder:
                index_dir = random.randint(0, len(dirs) - 1)
                dataset_folder = os.path.join(root, dirs[index_dir])
                break
        for root, dirs, files in os.walk(txt_dataset_folder + "/" + dataset_folder.rpartition('/')[-1]):
            index_file = random.randint(0, len(files) - 1)
            resource_name = files[index_file]
    return dataset_folder, resource_name, type_of


# MAIN FUNCTION #

# Upload multiple datasets
def import_datasets(dataset_folder):
    for root, dirs, files in os.walk(dataset_folder):
        if root == csv_dataset_folder:
            create_dataset(root, "csv")
            for name in files:
                update_dataset(root, name, "csv")
        elif root != txt_dataset_folder:
            create_dataset(root, "txt")
            for name in files:
                update_dataset(root, name, "txt")


# POST REQUESTS #

# Create new dataset
def create_dataset(folder_path, type_of):
    create_request = requests.post(api_url + 'package_create', json=new_data(folder_path, type_of), headers=header)
    print(create_request.json())
    assert create_request.ok
    assert create_request.json()["success"]
    pprint.pprint(create_request.json()["result"])


# Update specific dataset with new resource
def update_dataset(folder_path, file_name, type_of):
    filepath = pathlib.Path(os.path.join(folder_path, file_name))
    fd = filepath.open("rb")
    update_request = requests.post(api_url + 'package_revise',
                                       data=up_data(folder_path, file_name, type_of),
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


# GET REQUESTS #

# Return the metadata of a resource
def get_resource(resource_id):
    get_request = requests.get(api_url + 'resource_show', json={'id': resource_id})
    assert get_request.ok
    assert get_request.json()["success"]
    # pprint.pprint(get_request.json()["result"])
    return get_request.json()["result"]


# Return the resources of a dataset
def get_resources(dataset_name):
    get_request = requests.get(api_url + 'package_show', json={'id': dataset_name})
    if get_request.json()["success"]:
        return get_request.json()["result"]["resources"]
    else:
        return -1


# Return a list of the site’s datasets (packages) and their resources.
def get_datasets():
    get_request = requests.get(api_url + 'package_search?fq=groups:sail-project')
    assert get_request.ok
    assert get_request.json()["success"]
    # pprint.pprint(get_request.json()["result"])
    if get_request.json()["result"]["count"] != 0:
        return get_request.json()["result"]["results"]
    else:
        return -1

# MAIN #

# import_datasets(csv_dataset_folder)
# import_datasets(txt_dataset_folder)
