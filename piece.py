import math

import numpy as np
import matplotlib.pyplot as plt
from skimage import feature
from skimage import filters
from skimage import io
from skimage import measure
from skimage import morphology


# Load the image.
source = 'a.jpg'
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


'''
coords = feature.corner_peaks(feature.corner_fast(canny_edges, n=15),
                              min_distance=dist)
'''

'''
foerstner_sigma = 1
w, q = feature.corner_foerstner(canny_edges, sigma=foerstner_sigma)
accuracy_thresh = 0.5
roundness_thresh = 0.5
foerstner = (q > roundness_thresh) * (w > accuracy_thresh) * w
coords = feature.corner_peaks(foerstner, min_distance=dist)
'''

'''
coords = feature.corner_peaks(feature.corner_kitchen_rosenfeld(canny_edges),
                              min_distance=dist)
'''

'''
coords = feature.corner_peaks(feature.corner_shi_tomasi(canny_edges, sigma=3))
'''

'''
coords_subpix = feature.corner_subpix(canny_edges, coords, window_size=window)
'''



# Display results.
fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(20, 8))

ax1.imshow(piece, cmap=plt.cm.gray)
ax1.axis('off')

ax2.imshow(canny_edges, cmap=plt.cm.gray)
ax2.axis('off')
ax2.set_title('Canny filter, $\sigma=%s$' % sigma, fontsize=20)

ax3.imshow(canny_edges, cmap=plt.cm.gray)
ax3.plot(coords[:, 1], coords[:, 0], '+r', markersize=12)
#ax3.plot(coords_subpix[:, 1], coords_subpix[:, 0], '.b', markersize=5)
ax3.axis('off')
ax3.set_title('Harris corners', fontsize=20)

fig.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9,
                    bottom=0.02, left=0.02, right=0.98)
plt.show()
fig.savefig('out.png')
