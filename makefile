all: service server tests alg

alg:
	python algorithm_factory.py

service:
	python trafficmon_service.py

server:
	python traffic_server.py

tests:
	python tests.py
