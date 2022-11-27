#!/usr/bin/env python
import os
import pprint
import pathlib
import random
import requests
import ConvertData

# AUX INFO #

api_url = 'http://dockerhost:5000/api/3/action/'
nmea_dataset_folder = '/path/to/SAIL_SD_GNSS_NMEA'
gnss_dataset_folder = '/path/to/SAIL_SHIP_NS'
csv_dataset_folder = '/path/to/SAIL_PD_CSV'
api_token = 'api_token'
header = {
    "X-CKAN-API-Key": api_token,
}
csv_description = """###### This dataset contains CSV files with information about
- Gama radiation (GA)
- Atmospheric electric field (E1 and E2)
- Visibility (VI)
- Solar radiation (inSL and outSL)
"""
nmea_description = "###### This dataset contains GNSS_NMEA_yyyymmdd_hh files (where yyyy is the year, mm the month, dd the day, and HH the hour), each including the hourly logs from the antennas composign the GNSS system, in the NMEA (National Marine Electronics Association) standard format."
gnss_description = """###### This dataset contains GNSS_type_yyyyymmdd__hh files (where type is the resource format, yyyy is the year, mm the month, dd the day, and HH the hour), each including the hourly logs from the antennas composing the GNSS system, in different formats:
- binary format (described in Novatel OEM4 Volume 2 Command and Log Reference User manual)
- RAWIMUX format (IMU data extended log for post-processing)
###### There is also another format for representing the GNSS system, the best known, NMEA (National Marine Electronics Association), but this is available in individual datasets.
"""
csv_title = "Structured atmospheric measurements of the SAIL campaign"
nmea_title = "Raw NMEA measurements of the SAIL campaign"
gnss_title = "Raw GNSS measurements of the SAIL campaign"


# DATA OBJECTS #

# Metadata to update dataset
def up_data(folder_path, file_name, file_type):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    data = {
        "match__name": folder_name,
        "update__resources__extend": '[{"name": "' + file_name + ' "}]' if file_type == "csv" else '[{"name": "' + file_name + ' ", "format": "txt"}]'
    }
    return data


# Metadata to create dataset
def new_data(folder_path, type_of):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    if type_of == "gnss" or type_of == "nmea":
        date = folder_path.rpartition('/')[-1].split("_")[-1]
    data = {
        "name": folder_name,
        "notes": csv_description if type_of == "csv" else nmea_description if type_of == "nmea" else gnss_description,
        "title": csv_title if type_of == "csv" else nmea_title + " (" + date[:4] + "/" + date[4:6] + "/" + date[
                                                                                                          6:] + ")" if type_of == "nmea" else gnss_title + " (" + date[
                                                                                                                                                                  :4] + "/" + date[
                                                                                                                                                                              4:6] + "/" + date[
                                                                                                                                                                                           6:] + ")",
        "private": False,
        "tags": [{"name": "research"}],
        "owner_org": "inesctec",
        "groups": [{"name": "sail-project"}],
        "extras": [{"key": "year", "value":date[:4]}, {"key": "month", "value": date[4:6]}, {"key": "day", "value": date[6:]}] if type_of != "csv" else []
    }
    return data

# Metadata with spatial field
def add_spatial_data(folder_path, type_of, coordinates):
    folder_name = (folder_path.rpartition('/')[-1]).lower()
    data = {
        "name": folder_name,
        "notes": csv_description if type_of == "csv" else nmea_description if type_of == "nmea" else gnss_description,
        "title": csv_title if type_of == "csv" else nmea_title + " (" + date[:4] + "/" + date[4:6] + "/" + date[
                                                                                                          6:] + ")" if type_of == "nmea" else gnss_title + " (" + date[

                                            :4] + "/" + date[

                                                        4:6] + "/" + date[
                                                                                                                                                                                           6:] + ")",
        "private": False,
        "tags": [{"name": "research"}],
        "owner_org": "inesctec",
        "groups": [{"name": "sail-project"}],
        "extras": [{"key": "year", "value":date[:4]}, {"key": "month", "value": date[4:6]}, {"key": "day", "value": date[6:]}] if type_of != "csv" else [{"key": "year", "value":date[:4]}, {"key": "month", "value": date[4:6]}, {"key": "day", "value": date[6:]}, {"key":"spatial","value":'{"type":"Polygon","coordinates":' + coordinates + '}'}]
    }
    return data



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
    return get_request.json()["result"]


# Return the resources of a dataset
def get_resources(dataset_name):
    get_request = requests.get(api_url + 'package_show', json={'id': dataset_name})
    if get_request.json()["success"]:
        return get_request.json()["result"]["resources"]
    else:
        return -1


# Return a list of the site’s datasets (packages) and their resources.
def get_dataset_names():
    get_request = requests.get(api_url + 'package_list', json={'limit': 100})
    assert get_request.ok
    assert get_request.json()["success"]
    if get_request.json()["result"]:
        return get_request.json()["result"]
    else:
        return -1


# Return a list of the site’s datasets (packages) and their resources.
def get_datasets():
    get_request = requests.get(api_url + 'current_package_list_with_resources', json={'limit': 100})
    assert get_request.ok
    assert get_request.json()["success"]
    if get_request.json()["result"]:
        return get_request.json()["result"]
    else:
        return -1

# Delete dataset
def delete_datasets(dataset_names):
    for dataset_name in dataset_names:
       requests.post(api_url + 'package_delete', json={'id': dataset_name},headers=header)


# Import datasets
def import_datasets(type_of):
    if type_of == "nmea":
        root, dirs, empty = next(os.walk(nmea_dataset_folder))
    else if type_of == "gnss":
        root, dirs, empty = next(os.walk(gnss_dataset_folder)) 
    else:
        root, empty, empty = next(os.walk(csv_dataset_folder))

    for dir_aux in dirs:
        if type_of != "csv":
            dataset_folder_path = os.path.join(root, dir_aux)
            json_data = new_data(dataset_folder_path, type_of)
        else:
            dataset_folder_path = os.path.join(root, dir_aux)
            coordinates = ConvertData.choose_bbox(dataset_folder_path)
            json_data = add_spatial_data(dataset_folder_path, type_of, coordinates)
        requests.post(api_url + "package_create", json=json_data,
                         headers={
                             'Authorization': api_token})
        resources = next(os.walk(dataset_folder_path))[2]
        for resource_name in resources:
            json_data = up_data(dataset_folder_path, resource_name, type_of)
            filepath = pathlib.Path(os.path.join(dataset_folder_path, resource_name))
            fd = filepath.open("rb")
            update_request = requests.post(api_url + "package_revise", data=json_data,
                                              files=[("update__resources__-1__upload", (resource_name, fd))],
                                              headers={
                                                  'Authorization': api_token})
            new_resource = update_request.json()["result"]["package"]["resources"][-1]
            requests.post(api_url + "resource_create_default_resource_views",
                             json={"resource": new_resource},
                             headers={
                                 'Authorization': api_token})
            requests.post(api_url + "datastore_create",
                             json={"resource": new_resource},
                             headers={
                                 'Authorization': api_token})