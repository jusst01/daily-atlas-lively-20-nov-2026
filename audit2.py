import numpy as np
from PIL import Image
a = np.asarray(Image.open("/tmp/arttest/entry.png").convert("RGB")).astype(int)
PAPER = np.array((243, 245, 247))
# truly empty gutters
for label, sl in [("gutter above stat strip", (slice(146, 150), slice(24, 1000))),
                  ("gap between grid and band", (slice(676, 684), slice(24, 1000))),
                  ("right margin strip", (slice(100, 900), slice(1004, 1020)))]:
    reg = a[sl]
    u = np.unique(reg.reshape(-1, 3), axis=0)
    print(label, "unique colours:", len(u), "maxdev:",
          np.abs(reg - PAPER).max())
