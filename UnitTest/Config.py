#!/usr/bin/env python

HASS_LISTENPORT = 61209
RPC_AUTH_URL = "http://user:0928759204@127.0.0.1:61209"
INSTANCE_NAME = "unit_test"
IMAGE_ID = "72b06226-cd39-4ece-9ed0-11b0d3271ba6"  # cirror
HOST = "compute1"
AVAILABILITY_ZONE = "nova:%s" % HOST
VOLUME_ID = "7a7230ed-58d4-41a0-b4ff-e8642eda2a3b"  # unit-test-volume
BLOCK_DEVICE_MAPPING = {'vda': VOLUME_ID}
NETWORK_PROVIDER_ID = "974bd689-28da-44cf-9332-9e7a0ac1c8f3"  # provider
NETWORK_SELFSERVICE_ID = ""  # selfservice
FLAVOR_ID = "0"  # m1.nano
