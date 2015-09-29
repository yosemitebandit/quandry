"""Puzzle piece image processing."""

import matplotlib.pyplot as plt
import numpy as np
from skimage import feature
from skimage import filters
from skimage import io


# Load the image.
source = 'b.jpg'
piece = io.imread(source, as_grey=True)

# Find edges with the Canny filter.
low = 0.0
otsu = filters.threshold_otsu(piece, nbins=256)
sigma = 3
canny_edges = feature.canny(piece, sigma=sigma, low_threshold=low,
                            high_threshold=otsu)
canny_edges = np.logical_not(canny_edges)

# Get corners.
dist = 20
sensitivity = 0.05
window = 13
harris = feature.corner_harris(canny_edges, k=sensitivity)
coords = feature.corner_peaks(harris, min_distance=dist)

# Find approximate center.
center = [sum(coords[:, 0]) / len(coords[:, 0]),
          sum(coords[:, 1]) / len(coords[:, 1])]

# Display results.
fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(20, 8))

ax1.imshow(piece, cmap=plt.cm.gray)
ax1.axis('off')

ax2.imshow(canny_edges, cmap=plt.cm.gray)
ax2.axis('off')
ax2.set_title('Canny filter, $\sigma=%s$' % sigma, fontsize=20)

ax3.imshow(canny_edges, cmap=plt.cm.gray)
ax3.plot(coords[:, 1], coords[:, 0], '+r', markersize=12)
ax3.plot(center[1], center[0], '*b', markersize=8)
ax3.axis('off')
ax3.set_title('Harris corners', fontsize=20)

fig.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9,
                    bottom=0.02, left=0.02, right=0.98)
plt.show()
fig.savefig('out.png')
