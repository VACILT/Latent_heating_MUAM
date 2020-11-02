# /usr/bin/python

#####################################################################
import os.path

import numpy as N

from netCDF4 import Dataset

from scipy import optimize

from pathlib import Path

##############################################################################################

nx = 64
ny = 36
nz = 56
nv = 3
nh = 24
nd = 30
nt = nh * nd
nw = nd

lon = N.arange(0., 5.625 * nx, 5.625, float)
lat = N.arange(-87.5, -87.5 + 5. * ny, 5., float)
lev = N.arange(1.421, 160., 2.842, float)
day = N.arange(0., float(nw * 24.), 24. / nh, float)

######################################################################
var = ['tem', 'zon', 'mer', 'ver', 'phi']
#define ENSO months
months=[ "Feb"] #"Dec", "Jan",
# define ENSO years
el_year_ls = [1983, 1992, 1998, 2003, 2010]
la_year_ls = [1989, 1999, 2000, 2008, 2011]

for enso in ['el','la']:

    if enso == "el":
        enso_years = el_year_ls
    if enso == "la":
        enso_years = la_year_ls

    k1w = N.zeros((len(var), len(enso_years), len(months), nz, ny, 4, 2), float)  # var,year,month,levs,lats,kwave,amp/pha

    for iv in range(len(var)):

        for iy in range(len(enso_years)):

            # # Get list of input files
            root_path = Path('/projekt5/hochatm/muam_mstober/')
            in_folders = [f for f in root_path.iterdir() if f.is_dir()]  # get all folder in root_path

            # get ENSO directories
            enso_in_folders = sorted(list(filter(lambda x: str(x)[-8:] in [f'{enso_years[iy]}_{mon}' for mon in months], in_folders)))

            print(enso_in_folders)

            for im in range(len(months)):

                # and particular input files
                add_nc_suffix = lambda x: x / 'nc' / str('muam_' + months[im] + '360.nc')
                enso_in_files = Path.joinpath(enso_in_folders[im],'nc/muam_' + months[im] + '360.nc')

                print(enso_years[iy], months[im], var[iv], enso_in_files)

                nc_enso = Dataset(enso_in_files, 'r')

                data = N.array(nc_enso.variables[var[iv]])

                nc_enso.close()

                #####################################################################

                fitfunc = lambda p, s, c: p[0] + \
                                          p[1] * s[:, 0, 0] + p[2] * c[:, 0, 0] + p[3] * s[:, 0, 1] + p[4] * c[:, 0, 1] + \
                                          p[5] * s[:, 1, 0] + p[6] * c[:, 1, 0] + p[7] * s[:, 1, 1] + p[8] * c[:, 1, 1]

                x = lon * N.pi / 180.
                t = day * 2. * N.pi / float(nw * 24.)

                nx = len(x)
                nt = len(t)

                for kwave in range(4):  # kwave=0,1,2,3 (harmonics) for dt,sdt,tdt,qdt

                    s = N.zeros((nt * nx, 2, 2), float)
                    c = N.zeros((nt * nx, 2, 2), float)

                    k = -1

                    kx = kwave + 1  # kx=1,2,3 zonal wavenumber
                    px = kx * nw

                    print('k=', kx)

                    for i in range(nt):
                        for j in range(nx):
                            k = k + 1

                            s[k, 0, 0] = N.sin(kx * x[j] + px * t[i])
                            c[k, 0, 0] = N.cos(kx * x[j] + px * t[i])
                            s[k, 0, 1] = N.sin(kx * x[j] - px * t[i])
                            c[k, 0, 1] = N.cos(kx * x[j] - px * t[i])

                            s[k, 1, 0] = N.sin(kx * x[j] + 0. * t[i])
                            c[k, 1, 0] = N.cos(kx * x[j] + 0. * t[i])
                            s[k, 1, 1] = 0.  # N.sin(1.*x[j]-0.*t[i])
                            c[k, 1, 1] = 0.  # *N.cos(1.*x[j]-0.*t[i])

                    p0 = [1., 1., 1., 1., 1., 1., 1., 1., 1.]  # Initial guess for the parameters

                    for z in range(nz):

                        for k in range(ny):
                            y = N.ravel(data[:, z, k, :])

                            errfunc = lambda p, s, c, y: fitfunc(p, s, c) - y  # Distance to the target function

                            p1, success = optimize.leastsq(errfunc, p0[:], args=(s, c, y))

                            # amplitude
                            k1w[iv, iy, im, z, k, kwave, 0] = N.sqrt(p1[1] * p1[1] + p1[2] * p1[2])

                            # phase
                            k1w[iv, iy, im, z, k, kwave, 1] = N.arctan2(p1[1], p1[2])  # zwischen -pi bis pi

        out = Dataset('ensemble_tides_' + var[iv] + '_' + enso + '_Feb' + '.nc', 'w')
        out.createDimension('lat', len(lat))
        out.createDimension('lev', len(lev))
        out.createDimension('yr', len(enso_years))
        out.createDimension('mon', len(months))

        if var[iv] == 'tem':
            unit = 'K'
        elif var[iv] == 'phi':
            unit = 'm'
        else:
            unit = 'm/s'

        v = out.createVariable('DT_amp', 'f', ('yr', 'mon', 'lev', 'lat'))
        v[:, :, :, :] = k1w[iv, :, :, :, :, 0, 0]
        v.units = unit

        v = out.createVariable('DT_pha','f',('yr','mon','lev','lat'))
        v[:,:,:,:] = k1w[iv,:,:,:,:,0,1]
        v.units = 'rad'

        v = out.createVariable('SDT_amp','f',('yr','mon','lev','lat'))
        v[:,:,:,:] = k1w[iv,:,:,:,:,1,0]
        v.units = unit

        v = out.createVariable('SDT_pha','f',('yr','mon','lev','lat'))
        v[:,:,:,:] = k1w[iv,:,:,:,:,1,1]
        v.units = 'rad'

        v = out.createVariable('TDT_amp','f',('yr','mon','lev','lat'))
        v[:,:,:,:] = k1w[iv,:,:,:,:,2,0]
        v.units = unit

        v = out.createVariable('TDT_pha','f',('yr','mon','lev','lat'))
        v[:,:,:,:] = k1w[iv,:,:,:,:,2,1]
        v.units = 'rad'

        v = out.createVariable('QDT_amp','f',('yr','mon','lev','lat'))
        v[:,:,:,:] = k1w[iv,:,:,:,:,3,0]
        v.units = unit

        v = out.createVariable('QDT_pha','f',('yr','mon','lev','lat'))
        v[:,:,:,:] = k1w[iv,:,:,:,:,3,1]
        v.units = 'rad'

        out.close()
