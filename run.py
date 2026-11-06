import argparse
import re
import subprocess
import sys
from pathlib import Path
import mlflow

parser = argparse.ArgumentParser()
parser.add_argument("--run-name", default="baseline")
parser.add_argument("--experiment", default="convmixer-cifar10")
args, extra = parser.parse_known_args()

defaults = [
    "--lr-max=0.05", "--ra-n=2", "--ra-m=12",
    "--wd=0.005", "--scale=1.0", "--jitter=0",
    "--reprob=0"
]
cmd = [sys.executable, "-u", "train.py", *defaults, *extra]

params = {}
for arg in defaults + extra:
    if arg.startswith("--"):
        key, _, value = arg[2:].partition("=")
        params[key] = value or True

Path("logs").mkdir(exist_ok=True)
mlflow.set_tracking_uri(f"sqlite:///{Path('mlflow.db').resolve()}")
mlflow.set_experiment(args.experiment)

pattern = re.compile(
    r"Epoch: (\d+) \| Train Acc: ([\d.]+), "
    r"Test Acc: ([\d.]+), Time: ([\d.]+), lr: ([\d.]+)"
)

with mlflow.start_run(run_name=args.run_name) as run:
    mlflow.log_params(params)
    mlflow.set_tag("command", " ".join(cmd))

    log_path = Path("logs") / f"{args.run_name}_{run.info.run_id[:8]}.txt"

    with log_path.open("w") as log:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True
        )

        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()

            match = pattern.search(line)
            if match:
                epoch, train, test, sec, lr = match.groups()
                mlflow.log_metrics({
                    "train_acc": float(train),
                    "test_acc": float(test),
                    "epoch_time": float(sec),
                    "lr": float(lr)
                }, step=int(epoch))

        status = process.wait()

    mlflow.log_artifact(str(log_path))

    if status:
        raise RuntimeError(f"Training failed with exit code {status}")

print(f"Run ID: {run.info.run_id}")
print(f"Log: {log_path}")