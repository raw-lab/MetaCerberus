# -*- coding: utf-8 -*-

"""metacerberus_mpp.py: Module to replace Ray MPP library
"""


import psutil
from pathlib import Path


# GLOBAL VARIABLES
CURR_ID = 0
NODES = list()
QUEUE = dict()

# CLASS
class MPP:
	def __init__(self, func):
		self.func = func
		return
	
	def options(self, num_cpus=1):
		return self

	def remote(self, *args, **kwargs):
		return put(self.func(*args, **kwargs))


# METHODS
def init(address="local", num_cpus=None, log_to_driver=False):
	if not num_cpus:
		num_cpus = psutil.cpu_count()
	global NODES
	NODES = [dict(ObjectStoreSocketName="tmp/current/objects")]
	#Path("tmp/current/objects").mkdir(parents=True, exist_ok=True)
	return

def nodes():
	return NODES

def get(id:int):
	return QUEUE.pop(id)

def put(obj):
	global CURR_ID
	CURR_ID += 1
	QUEUE[CURR_ID] = obj
	return CURR_ID

def wait(objects:list, timeout=0):
	ready = [objects.pop(0)]
	return ready, objects

def remote(func):
	return MPP(func)

def shutdown():
	return
