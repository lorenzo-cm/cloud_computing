zip function.zip main.py helper.py

kubectl create configmap userfunc-zip \
  --from-file=function.zip=./function.zip \
  --dry-run=client \
  --output yaml > userfunc-zip.yaml

kubectl apply -f userfunc-zip.yaml
