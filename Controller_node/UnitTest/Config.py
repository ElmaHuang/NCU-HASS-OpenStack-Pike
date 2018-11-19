#!/usr/bin/env python

HASS_LISTENPORT = 61209
RPC_AUTH_URL = "http://user:openstack1234!@127.0.0.1:61209"
INSTANCE_NAME = "unit_test"
IMAGE_ID = "66e04c13-646c-4470-a4ba-26160a6e076d"  # cirror
HOST = "compute2"
AVAILABILITY_ZONE = "nova:%s" % HOST
VOLUME_ID = "55922843-c077-48c4-88a9-82893f2dd3fe"  # unit-test-volume
BLOCK_DEVICE_MAPPING = {'vda': VOLUME_ID}
NETWORK_PROVIDER_ID = "d2e8a76c-c2aa-4e60-82ef-9ea7e297c86c"  # provider
NETWORK_SELFSERVICE_ID = ""  # selfservice
FLAVOR_ID = "0"  # m1.nano
