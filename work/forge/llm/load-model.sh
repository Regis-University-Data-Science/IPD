#!/bin/bash
# LLM Cluster Configuration Map - Used by start-cluster.sh
# Format: hostname|model-tag|keep-alive|cuda-devices

nickel|mixtral-multi|24h|0,1,2
zinc|codellama-multi|24h|0,1
copper|mistral:7b-instruct-q5_K_M|24h|0
iron|llama3:8b-instruct-q5_K_M|24h|0
platinum|phi3-mini-utility|24h|0

