#!/bin/bash

# build new image
bash build.sh

# create namespace
kubectl get namespace monitor
RES=$?
if [ "$RES" == "1" ]; then
  kubectl create ns monitor
fi

# create config
kubectl -n monitor get secret monitor-config
RES=$?
if [ "$RES" == "1" ]; then
  cp config.yaml /tmp/
  vi /tmp/config.yaml
  kubectl create secret generic monitor-config --from-file=config.yaml=/tmp/config.yaml -n monitor
fi

# create cronjob
cat <<EOF | kubectl -n monitor apply -f -
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: monitor
spec:
  schedule: "* * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: monitor
            imagePullPolicy: Always
            image: sybex/monitor-client
            command: ['sh', '-c', 'ln -s /app/config/config.yaml /app/config.yaml; python3 /app/client.py']
            volumeMounts:
            - name: config
              mountPath: "/app/config"
              readOnly: true
          volumes:
          - name: config
            secret:
              secretName: monitor-config
          restartPolicy: OnFailure
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-view
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitor-view
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: view
subjects:
- kind: ServiceAccount
  name: default
  namespace: monitor
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitor-node
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: node-view
subjects:
- kind: ServiceAccount
  name: default
  namespace: monitor
EOF
