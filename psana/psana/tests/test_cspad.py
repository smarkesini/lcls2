#------------------------------
# nosetests -sv psana/psana/tests
#
#------------------------------

doPlot = 0

#------------------------------

import psana
if doPlot: import matplotlib.pyplot as plt

ds = psana.DataSource('/reg/common/package/temp/crystal_xray_evts.xtc')
det = ds.Detector("DsdCsPad")
for i, evt in enumerate(ds.events()):
    raw = det.raw(evt)
    photonEnergy = det.photonEnergy(evt)
    timestamp = det.timestamp(evt)
    print(i, raw.shape)
    print(photonEnergy)
    print(timestamp)

if doPlot:
    for i in range(raw.shape[0]):
        plt.imshow(raw[i])
        plt.title(i)
        plt.colorbar()
        plt.show()
