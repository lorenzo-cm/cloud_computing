kubectl create configmap pyfile \
  --from-file pyfile=main.py \
  --dry-run=client \
  --output yaml > pyfile-configmap.yaml

kubectl apply -f pyfile-configmap.yaml
