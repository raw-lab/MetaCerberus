#!/usr/bin/env python

import json

# read file
f = open('ko00001.json')
data = json.load(f)
f.close()

count = 0
for key, value in data.items():
   print("Key:", key, "Value:", value)
   count += 1
   if count > 10:
       break
