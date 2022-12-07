CKAN: The Open Source Data Portal Software
==========================================

.. image:: https://img.shields.io/badge/license-AGPL-blue.svg?style=flat
    :target: https://opensource.org/licenses/AGPL-3.0
    :alt: License

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
    :target: http://docs.ckan.org
    :alt: Documentation
.. image:: https://img.shields.io/badge/support-StackOverflow-yellowgreen.svg?style=flat
    :target: https://stackoverflow.com/questions/tagged/ckan
    :alt: Support on StackOverflow

.. image:: https://circleci.com/gh/ckan/ckan.svg?style=shield
    :target: https://circleci.com/gh/ckan/ckan
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/ckan/ckan/badge.svg?branch=master
    :target: https://coveralls.io/github/ckan/ckan?branch=master
    :alt: Coverage Status

.. image:: https://badges.gitter.im/gitterHQ/gitter.svg
    :target: https://gitter.im/ckan/chat
    :alt: Chat on Gitter

**CKAN is the world’s leading open-source data portal platform**.
CKAN makes it easy to publish, share and work with data. It's a data management
system that provides a powerful platform for cataloging, storing and accessing
datasets with a rich front-end, full API (for both data and catalog), visualization
tools and more. Read more at `ckan.org <http://ckan.org/>`_.

Installation and Deployment
------------

For the installation of the system it is necessary to meet certain prerequisites, which
are listed below:

- Unrestricted access to external domains, such as GitHub or DockerHub
- Have docker, docker-compose and git installed

Once the prerequisites listed above are met, you need to download the software as well
as some custom images to run certain docker containers. For this, you need to run the
following commands:

- Clone CKAN into a directory of choice:

```
cd /path/to/directory
git clone https://github.com/priest110/ckan.git
```

- Pull the required docker images from the DockerHub:

```
docker pull priest110/docker_db:1.0.0
docker pull priest110/docker_ckan:1.0.0
```

Reaching this point, you have a working system, however, the Docker installation has a
problem regarding the recognition of localhost as a valid address (where the main service
CKAN is running) for other services, in this case for the Datapusher, which makes it
impossible to run well. As such, some changes need to be made to the hosts file:

1. First, find the IP 0f the docker0 bridge:

```
ip addr show | grep docker0
```

2. An example of the possible output:

```
10: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state
DOWN group default
inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0:
```

3. Next, you can then edit /etc/hosts/ file:

```
172.17.0.1 dockerhost
```

4. Restart the Docker daemon:

```
sudo service docker restart
```

5. Run:

```
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

After this, you have all the services working well, just navigate to http://dockerhost:5000
and explore.

If you want full access to the platform I developed, such as the CKAN's extensions added to the software and other configurations, you need to contact me because the docker volumes that have that information are on a local server.
