import random
from locust import HttpUser, task, between
import ImportData
import pathlib
import os


class QuickStartUser(HttpUser):
    # wait_time = between(1, 5)

    @task(5)
    def get_datasets(self):
        self.client.get("/api/3/action/current_package_list_with_resources")

    @task(4)
    def get_dataset(self):
        datasets = ImportData.get_datasets()
        if datasets != -1:
            index = random.randint(0, len(datasets) - 1)
            self.client.get("/api/3/action/package_show", json={'id': datasets[index]["name"]})

    @task(3)
    def get_resource(self):
        datasets = ImportData.get_datasets()
        if datasets != -1:
            index_dataset = random.randint(0, len(datasets) - 1)
            resources = ImportData.get_resources(datasets[index_dataset]["id"])
            if resources != -1:
                index_resource = random.randint(0, len(resources) - 1)
                self.client.get("/api/3/action/resource_show", json={'id': resources[index_resource]["id"]})

    @task(1)
    def get_groups(self):
        self.client.get("/api/3/action/group_list")

    @task(1)
    def get_organizations(self):
        self.client.get("/api/3/action/organization_list")

    @task(2)
    def post_resource(self):
        dataset_folder, resource_name, type_of = ImportData.pick_random()
        existence = ImportData.exists(dataset_folder, resource_name)
        if existence == -1 or existence == 0:
            if existence == -1:
                json_data = ImportData.new_data(dataset_folder, type_of)
                self.client.post("/api/3/action/package_create", json=json_data, headers={
                                 'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})
            json_data = ImportData.up_data(dataset_folder, resource_name, type_of)
            filepath = pathlib.Path(os.path.join(dataset_folder, resource_name))
            fd = filepath.open("rb")
            update_request = self.client.post("/api/3/action/package_revise", data=json_data,
                                              files=[("update__resources__-1__upload", (resource_name, fd))], headers={
                                              'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})
            new_resource = update_request.json()["result"]["package"]["resources"][-1]
            self.client.post("/api/3/action/resource_create_default_resource_views", json={"resource": new_resource}, headers={
                             'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})
            self.client.post("/api/3/action/datastore_create", json={"resource": new_resource}, headers={
                             'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})

    def on_start(self):
        self.client.get("/api/3/action/package_show?id=teste")
