#!/bin/bash
# LLM Cluster Configuration Map - Used by start-cluster.sh
# Format: hostname|model-tag|keep-alive|cuda-devices

nickel|llama3:8b-instruct-q5_K_M|168h|0,1,2
zinc|llama3:8b-instruct-q5_K_M|168h|0,1
copper|llama3:8b-instruct-q5_K_M|168h|0
platinum|phi3-mini-utility|168h|0
iron|llama3:8b-instruct-q5_K_M|168h|0
tungsten|llama3:8b-instruct-q5_K_M|168h|0
