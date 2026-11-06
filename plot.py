import re
from pathlib import Path
import matplotlib.pyplot as plt

log = Path("logs/r0-baseline.txt").read_text()

pattern = (
    r"Epoch: (\d+) \| Train Acc: ([\d.]+), "
    r"Test Acc: ([\d.]+), Time: ([\d.]+), lr: ([\d.]+)"
)

rows = [list(map(float, x)) for x in re.findall(pattern, log)]
if not rows:
    raise ValueError("No epoch metrics found in log")

epochs, train, test, times, lr = zip(*rows)
epochs = [int(x) + 1 for x in epochs]

Path("results").mkdir(exist_ok=True)

plt.plot(epochs, train, label="Train")
plt.plot(epochs, test, label="Test")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.title("ConvMixer-256/8 on CIFAR-10")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("results/accuracy.png", dpi=150, bbox_inches="tight")
plt.close()

plt.plot(epochs, lr)
plt.xlabel("Epoch")
plt.ylabel("Learning rate")
plt.title("Learning Rate Schedule")
plt.grid(alpha=0.3)
plt.savefig("results/learning_rate.png", dpi=150, bbox_inches="tight")
plt.close()

print("Plots saved to results/")