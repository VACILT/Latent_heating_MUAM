#!/usr/bin/env python
# coding: utf-8

# In[33]:


import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from pathlib import Path
import numpy as np


# In[2]:


def process(ds):
    ds['lat'] = lat_grid
    ds['lat'].attrs['long_name'] = 'latitude'
    ds['lat'].attrs['units'] = 'deg'
    ds['lev'] = lev_grid
    ds['lev'].attrs['long_name'] = 'height'
    ds['lev'].attrs['units'] = 'km'
    return ds.mean('yr', keep_attrs = True), ds.std('yr', keep_attrs = True)


# In[3]:


root_path = '/home/gemeinsam_tmp/VACILT/'

ny = 36
nz = 56
nt = 5
lev_grid = np.arange(1.421,160.,2.842,float)
lat_grid = np.arange(-87.5,-87.5+5.*ny,5.,float)


# In[4]:


sel_var = 'tem'
sel_month = 'Jan'
sel_phase = 'la'


# In[5]:


infile = f'ensemble_tides_{sel_var}_{sel_phase}_{sel_month}.nc'
ds_wo_lh = xr.open_dataset(f'{root_path}muam_mstober/{infile}')
mean_wo_lh, std_wo_lh = process(ds_wo_lh)

ds_w_lh = xr.open_dataset(f'{root_path}latent_heat_output/{infile}')
mean_w_lh, std_w_lh = process(ds_w_lh)

diff = mean_w_lh-mean_wo_lh


# In[6]:


sel_tide = 'SDT_amp'


# In[38]:


cmap=plt.get_cmap('Blues') #cmap with blue colors
#make descrete areas in colorbar
cmaplist=[cmap(i) for i in range(cmap.N)]
cmaplist[0]='white'
cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
if sel_var=='tem':
    dsig=0.4
    bounds = [0.0, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0] # colorbar range bounds = N.arange(0,30.1,2)
    lvls = np.arange(dsig,5,dsig)
    diff_clabel = 'diff [K]'
    clabel = 'temperature [K]'
elif sel_var=='zon':
    dsig=0.5
    bounds = np.arange(0,36.1,3) # colorbar range
    lvls = np.arange(dsig,5,dsig)
    diff_clabel = 'diff [m/s]'
    clabel = 'zonal wind [K]'
elif sel_var=='mer':
    dsig=0.5
    bounds = np.arange(0,36.1,3) # colorbar range
    lvls = np.arange(dsig,5,dsig)
    diff_clabel = 'diff [m/s]'
    clabel = 'meridional wind [m/s]'
elif sel_var=='ver':
    dsig=0.2
    bounds = np.arange(0,10.1,1) # colorbar range
    lvls = np.arange(dsig,5,dsig)
    diff_clabel = 'diff [m/s]'
    clabel = 'vertical wind [m/s]'
elif selvar=='phi':
    dsig=5
    bounds = np.arange(0,1001,100) # colorbar range
    lvls = np.arange(dsig,50,dsig)
    diff_clabel = 'diff [m]'
    clabel = 'geopotential height [m]'
cmap.set_over('black') 

c_pad = 0.2
c_shrink = 0.99
c_aspect = 20

ymajorLocator = MultipleLocator(20)
xmajorLocator = MultipleLocator(30)


# In[42]:


plt.rcParams.update({'font.size': 20})
fig, axes = plt.subplots(ncols = 3, figsize = (16,6), sharey = True, sharex = True)

ax = axes[0]
p = mean_w_lh[sel_tide].plot(cmap = cmap, ax = ax, 
                             add_colorbar = False, levels = bounds)
std_w_lh[sel_tide].squeeze().plot.contour(levels = lvls, colors='g', ax = ax)
ax.set_title('With LH')
ax.text(0.6,0.1,'$\sigma_{max}$'+f'= {std_w_lh[sel_tide].max().values:2.3f}', 
        fontsize=13, backgroundcolor=(1, 1, 1, 0.5), transform=ax.transAxes)
ax.xaxis.set_major_locator(xmajorLocator)
ax.yaxis.set_major_locator(ymajorLocator)
ax.grid(b=True, which='major', color='gray', linestyle='--')

ax = axes[1]
cbar = fig.colorbar(p, ax=axes[:2],  location='bottom',                     extend = 'both', pad = c_pad,                     shrink=c_shrink, aspect = c_aspect)
cbar.set_label(clabel)

mean_wo_lh[sel_tide].plot(cmap = cmap, ax = ax,
                          add_colorbar = False, levels = bounds)
std_wo_lh[sel_tide].squeeze().plot.contour(levels = lvls, colors='g', ax = ax)

ax.text(0.6,0.1,'$\sigma_{max}$'+f'= {std_wo_lh[sel_tide].max().values:2.3f}', 
        fontsize=13, backgroundcolor=(1, 1, 1, 0.5), transform=ax.transAxes)
ax.set_ylabel('')
ax.set_title('Without LH')
ax.grid(b=True, which='major', color='gray', linestyle='--')

ax = axes[2]
diff[sel_tide].plot(ax = ax, robust = True, 
                    cbar_kwargs={'orientation': 'horizontal', 'pad': c_pad, \
                                 'aspect': c_aspect/2., "shrink": c_shrink, 
                                 'extend': 'both', 'label': diff_clabel})
ax.text(0.6,0.1,'$\Delta_{max}$'+f'= {diff[sel_tide].max().values:2.3f}', 
        fontsize=13, backgroundcolor=(1, 1, 1, 0.5), transform=ax.transAxes)
ax.set_ylabel('')
ax.set_title('Difference')
ax.grid(b=True, which='major', color='gray', linestyle='--')

plt.suptitle(f'{sel_tide} comparison for {sel_month}', y=1.02)
fig.savefig(f'{sel_tide}_comparison_{sel_var}_{sel_phase}_{sel_month}.pdf', bbox_inches='tight')

