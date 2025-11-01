argocd app create lorenzomagalhaes-app \
      --repo https://github.com/lorenzo-cm/cloud_computing.git \
      --path kubernetes \
      --project $USER-project \
      --dest-namespace $USER \
      --dest-server https://kubernetes.default.svc \
      --sync-policy auto \
      