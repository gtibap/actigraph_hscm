import numpy as np
import matplotlib.pyplot as plt


a=np.array([[np.nan,0,1],[2,5,0],[4,np.nan,0]])
b=np.array([])
stat_all=np.array([],dtype=float).reshape(0,3)
print(a, np.nanmean(a))
print(b)
print(stat_all, stat_all.shape)

# a=np.array([0,0,1,2,3,0,4,0,0,2,3,0,0,0,0,4,6])
# ab= a>2
# c = ab[:-1] != ab[1:]
# idx = np.flatnonzero(c)
# intervals = idx[1:]-idx[:-1]
# print(intervals)
# duration_inactive = intervals[0::2]
# duration_active =   intervals[1::2]

# print('duration_active: ', duration_active)
# print('duration_inactive: ', duration_inactive)

# ra = ones()
# print(ra)


# def f(t):
#     return np.exp(-t) * np.cos(2*np.pi*t)


# t1 = np.arange(0.0, 3.0, 0.01)

# ax1 = plt.subplot(212)
# ax1.margins(0.05)           # Default margin is 0.05, value 0 means fit
# ax1.plot(t1, f(t1))

# ax2 = plt.subplot(221)
# ax2.margins(2, 2)           # Values >0.0 zoom out
# ax2.plot(t1, f(t1))
# ax2.set_title('Zoomed out')

# ax3 = plt.subplot(222)
# ax3.margins(x=0, y=-0.25)   # Values in (-0.5, 0.0) zooms in to center
# ax3.plot(t1, f(t1))
# ax3.set_title('Zoomed in')

# plt.show()