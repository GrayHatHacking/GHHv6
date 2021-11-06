#!/bin/bash
kubectl delete -f badperms.yml
kubectl delete -f bash.yml
kubectl delete -f ncat.yml
kubectl delete -f ncat-svc.yml

cd microservices-demo/deploy/kubernetes/manifests-monitoring/
kubectl delete -f 23-grafana-import-dash-batch.yaml
kubectl delete $(ls *-grafana-*.yaml | awk ' { print " -f " $1 }'  | grep -v grafana-import) 
kubectl delete $(ls *-prometheus-*.yaml | awk ' { print " -f " $1 } ')
kubectl delete -f 00-monitoring-ns.yaml

kubectl delete -n sock-shop svc/front-end
cd ../
kubectl delete -f complete-demo.yaml

eksctl delete cluster --name=ghh --wait --profile ghh
