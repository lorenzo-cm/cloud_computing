argocd app create guestbook \
      --repo https://github.com/lorenzo-cm/cloud_computing.git \
      --path . \
      --project $USER-project \
      --dest-namespace $USER \
      --dest-server https://kubernetes.default.svc \
      --sync-policy auto