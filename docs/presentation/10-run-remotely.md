# Send and run a batch remotely

Computer setup and transfer remain command-line operations, now under the
`httk workflow` command tree. The maintained adapters are explicit,
versioned bundles.

```console
httk workflow project init . --name presentation --default-queue default
httk workflow computer add kappa --template ssh-slurm --non-interactive
httk workflow computer configure kappa:default \
  --set workspace=/remote/path/to/Runs
httk workflow computer install kappa:default

httk workflow tasks send kappa:default JOB_UUID --workspace Runs
httk workflow tasks start-manager kappa:default --workers 8
httk workflow tasks status kappa:default
```

The destination workspace must already exist with the
`detached-transfer-v1` extension. Transfers preserve the job UUID, seal and
validate payload digests, and retire the source only after acknowledgement.

See the [project and workflow CLI
guide](https://docs.httk.org/httk-workflow/workflow_cli.html).
