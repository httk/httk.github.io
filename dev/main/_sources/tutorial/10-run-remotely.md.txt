# Send and run a batch remotely

Remote setup and transfer remain command-line operations, now under the
`httk workflow` command tree. The maintained adapters are explicit,
versioned bundles.

```console
httk workflow project init . --name tutorial --default-queue default
httk workflow remote add kappa --template ssh-slurm --non-interactive
httk workflow remote configure kappa:default \
  --set workspace=/remote/path/to/Runs
httk workflow remote install kappa:default

httk workflow workspace init local-runs --remote local --path Runs \
  --extension detached-transfer-v1
httk workflow workspace init kappa-runs --remote kappa:default \
  --path /remote/path/to/Runs --extension detached-transfer-v1
httk workflow transfer local-runs kappa-runs --job JOB_UUID
httk workflow manager run kappa-runs --workers 8
httk workflow workspace status kappa-runs
```

Both named workspaces must already exist with the `detached-transfer-v1`
extension. Transfers preserve the job UUID, seal and validate payload digests,
and retire the source only after acknowledgement.

See the project and workflow CLI guide in the versioned *httk-workflow*
documentation listed by the {doc}`module directory <../modules>`.
