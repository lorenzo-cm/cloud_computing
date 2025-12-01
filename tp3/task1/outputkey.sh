kubectl create configmap outputkey \
  --from-literal REDIS_OUTPUT_KEY=f6939046d4b2aa170232bf5ef9631f01-ifs4-proj3-output \
  --dry-run=client \
  --output yaml > outputkey-configmap.yaml

kubectl apply -f outputkey-configmap.yaml
