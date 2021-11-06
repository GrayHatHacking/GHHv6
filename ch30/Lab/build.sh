#!/bin/bash
echo "[+] Download eksctl"

if [[ ! -f "/usr/local/bin/aws-iam-authenticator" ]]
then
    curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.21.2/2021-07-05/bin/linux/amd64/aws-iam-authenticator
    sudo mv aws-iam-authenticator /usr/local/bin
    sudo chmod a+x /usr/local/bin/aws-iam-authenticator
fi

if [[ ! -f "/usr/local/bin/eksctl" ]]
then
    curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
    sudo mv /tmp/eksctl /usr/local/bin
    sudo chmod a+x /usr/local/bin/eksctl
fi

if [[ ! -f "/usr/local/bin/kfctl" ]]
then
    curl --silent --location "https://github.com/kubeflow/kfctl/releases/download/v1.2.0/kfctl_v1.2.0-0-gbc038f9_linux.tar.gz" | tar -xz -C /tmp
    sudo mv /tmp/kfctl /usr/local/bin
    sudo chmod a+x /usr/local/bin/kfctl
fi

if [[ ! -f "/usr/local/bin/kubectl" ]]
then
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
fi

echo "[+] Running eksctl to build a cluster"
eksctl create cluster --profile ghh -f eksctl.yml

kubectl apply -f container.yml
kubectl apply -f badperms.yml

echo "[+] Cloning Sockshop"
git clone https://github.com/microservices-demo/microservices-demo

echo "[+] Installing SockShop"
kubectl create namespace sock-shop
kubectl apply -f microservices-demo/deploy/kubernetes/complete-demo.yaml
sleep 10
kubectl delete -n sock-shop svc/front-end
sleep 10
kubectl expose deployment front-end -n sock-shop --type=LoadBalancer --name=front-end

cd microservices-demo/deploy/kubernetes/manifests-monitoring/
kubectl create -f 00-monitoring-ns.yaml
kubectl apply $(ls *-prometheus-*.yaml | awk ' { print " -f " $1 } ')
kubectl apply $(ls *-grafana-*.yaml | awk ' { print " -f " $1 }'  | grep -v grafana-import) 
kubectl apply -f 23-grafana-import-dash-batch.yaml

echo "[+] Pulling Kubestriker"
docker pull cloudsecguy/kubestriker:v1.0.0

echo "-----------------------------------------------------------"
echo "[+] The following URL can be used to access your sock-shop:"
kubectl get svc -n sock-shop | grep front | awk '{ print $4 }'
echo "[+] The following URL is your URL for the Kubernetes API:"
cat ~/.kube/config | grep server | awk '{ print $2 }'
