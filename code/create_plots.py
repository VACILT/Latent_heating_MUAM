# /usr/bin/python
#####################################################################
import os

import matplotlib as mpl

import pylab as P

import numpy as N

from netCDF4 import Dataset

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

##############################################################################################

def vecmean(amp,pha):
  x=[]
  y=[]
  for i in range(0,len(amp)):
    x.append(amp[i]*N.cos(pha[i]))
    y.append(amp[i]*N.sin(pha[i]))
  xsum=sum(i for i in x)
  ysum=sum(i for i in y)
  ampsum=N.sqrt(xsum**2+ysum**2)
  phamean=N.arctan2(ysum,xsum)
  ampmean=ampsum/float(len(amp))
  return phamean

#####################################################

ny = 36
nz = 56
nt = 5
	
lat = N.arange(-90.,-90.+5.*(ny+1),5.,float)
lev = N.arange(0,162.,2.842,float)
lev_grid = N.arange(1.421,160.,2.842,float)
lat_grid = N.arange(-87.5,-87.5+5.*ny,5.,float)
######################################################################

var = ['tem','zon','mer','ver','phi']
variable = ['Temperature','Zonal Wind','Meridional Wind','Vertical Wind','Geopotential'] 
unit = ['K','\tm$\,$s$^{-1}$','\tm$\,$s$^{-1}$','\tcm$\,$s$^{-1}$','\t\tm']
unit2 = ['K','ms$^{-1}$','ms$^{-1}$','cm s$^{-1}$','m']
months=["Dec"] #"Dec", "Feb", 

for enso in ['el']: #'el','la'
		

	for iv in range(5):
		
		nc = Dataset('ensemble_tides_' + var[iv] + '_' + enso + '_Feb'+'.nc','r')
		
		dtamp = N.array(nc.variables['DT_amp'])
		dtpha = N.array(nc.variables['DT_pha'])
		
		sdtamp = N.array(nc.variables['SDT_amp'])
		sdtpha = N.array(nc.variables['SDT_pha'])
		
		tdtamp = N.array(nc.variables['TDT_amp'])
		tdtpha = N.array(nc.variables['TDT_pha'])
		
		qdtamp = N.array(nc.variables['QDT_amp'])
		qdtpha = N.array(nc.variables['QDT_pha'])
		
		nc.close()
		
		if var[iv]=='ver': #in cm/s
			dtamp=dtamp*100
			sdtamp=sdtamp*100
			tdtamp=tdtamp*100
			qdtamp=qdtamp*100		
	
		mean=N.zeros((3,nz,ny,4),float)
		stdv=N.zeros((3,nz,ny,4),float)
		phamean=N.zeros((3,nz,ny,4),float)
		mon_mean=N.zeros((nz,ny,4),float)
		
		amp=N.zeros((nt),float)
		pha=N.zeros((nt),float)
	
		#######################################################################
	
		mean[:,:,:,0] = N.mean(dtamp[:,:,:,:],axis=0)
		stdv[:,:,:,0] = N.std(dtamp[:,:,:,:],axis=0)
		
		mean[:,:,:,1] = N.mean(sdtamp[:,:,:,:],axis=0)
		stdv[:,:,:,1] = N.std(sdtamp[:,:,:,:],axis=0)
		
		mean[:,:,:,2] = N.mean(tdtamp[:,:,:,:],axis=0)
		stdv[:,:,:,2] = N.std(tdtamp[:,:,:,:],axis=0)
		
		mean[:,:,:,3] = N.mean(qdtamp[:,:,:,:],axis=0)
		stdv[:,:,:,3] = N.std(qdtamp[:,:,:,:],axis=0)
		
		################ Plots ###########
		
		# create directory
		if os.path.isdir('tides4/'+var[iv]+'/'):
			path='tides4/'+var[iv]+'/'
		else:
			os.mkdir('tides4/'+var[iv]+'/')
			path='tides4/'+var[iv]+'/'
	
		fileformat='.png'
	
		for im in range(1):
			
			month=months[im]
			print (var[iv],month)	
			
			############################# Amplitudes ############################
			
			#define height and latitude range for plot:
			z0=0; z2=55
			y0=0;  y2=35
			#print lev[z0],lev[z2+1],lat[y0],lat[y2+1]	
			
			######## DT #############
	  
			cmap=P.get_cmap('Blues') #cmap with red and blue colors
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmaplist[0]='white'
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			if var[iv]=='tem':
				dsig=0.4
				bounds = [0.0, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0] # colorbar range bounds = N.arange(0,30.1,2)
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='zon':
				dsig=0.5
				bounds = N.arange(0,36.1,3) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='mer':
				dsig=0.5
				bounds = N.arange(0,36.1,3) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='ver':
				dsig=0.2
				bounds = N.arange(0,10.1,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='phi':
				dsig=5
				bounds = N.arange(0,1001,100) # colorbar range
				lvls = N.arange(dsig,50,dsig)
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
			cmap.set_over('black') #upper end color
			
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(10)
			yminorLocator = MultipleLocator(10)
			
			fig=P.figure(figsize=(9,8))
			ax = fig.add_subplot(111)
			
			CS=ax.imshow(mean[im, z0:z2 + 1, y0:y2 + 1, 0], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True,extend='max') 
			cbar.ax.tick_params(labelsize=25)    
			cbar.ax.set_title(unit[iv],fontsize=20)
			CS2=P.contour(lat_grid, lev_grid, stdv[im, :, :, 0], levels=lvls, colors='white', linewidths=2)
			CS3=P.contour(lat_grid, lev_grid, stdv[im, :, :, 0], levels=lvls, colors='k', linewidths=1)
			
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.xaxis.set_tick_params(pad=12)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.figtext(0.18,0.18,'$\Delta\sigma$ = '+str(dsig)+unit2[iv],fontsize=25,backgroundcolor=(1,1,1,0.5))
			P.figtext(0.5, 0.18,'$\sigma_{max}$ = ' + str(round(N.amax(stdv[im, :, :, 0]), 1)) + unit2[iv], fontsize=25, backgroundcolor=(1, 1, 1, 0.5))
			P.title('DT, El Nino, ' +variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'DT_amp_' + var[iv] + '_' + month + '_' +enso +  fileformat)
			
			######## SDT #############
			
			cmap=P.get_cmap('Blues') #cmap with red and blue colors
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmaplist[0]='white'
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			if var[iv]=='tem':
				dsig=0.4
				bounds = [0., 0.5, 1., 2.5, 5., 10., 15., 20., 25., 30.] # colorbar range bounds = N.arange(0,31,2)
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='zon':
				dsig=0.5
				bounds = N.arange(0,36,3) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='mer':
				dsig=0.5
				bounds = N.arange(0,36,3) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='ver':
				dsig=0.2
				bounds = N.arange(0,11,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='phi':
				dsig=5
				bounds = N.arange(0,501,50) # colorbar range
				lvls = N.arange(dsig,50,dsig)
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
			cmap.set_over('black') #upper end color
			
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(10)
			yminorLocator = MultipleLocator(10)
			
			fig=P.figure(figsize=(9,8))
			ax = fig.add_subplot(111)
			
			CS=ax.imshow(mean[im, z0:z2 + 1, y0:y2 + 1, 1], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True,extend='max') 
			cbar.ax.tick_params(labelsize=25)    
			cbar.ax.set_title(unit[iv],fontsize=20)
			CS2=P.contour(lat_grid, lev_grid, stdv[im, :, :, 1], levels=lvls, colors='white', linewidths=2)
			CS3=P.contour(lat_grid, lev_grid, stdv[im, :, :, 1], levels=lvls, colors='k', linewidths=1)
			
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.xaxis.set_tick_params(pad=12)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.figtext(0.18,0.18,'$\Delta\sigma$ = '+str(dsig)+unit2[iv],fontsize=25,backgroundcolor=(1,1,1,0.5))
			P.figtext(0.5, 0.18,'$\sigma_{max}$ = ' + str(round(N.amax(stdv[im, :, :, 1]), 1)) + unit2[iv], fontsize=25, backgroundcolor=(1, 1, 1, 0.5))
			P.title('SDT, El Nino,  ' +variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'SDT_amp_' + var[iv] +'_' + month + '_' +enso +  fileformat)
			
			######## TDT #############
			
			cmap=P.get_cmap('Blues') #cmap with red and blue colors
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmaplist[0]='white'
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			if var[iv]=='tem':
				dsig=0.4
				bounds = [0.,0.1, 0.5, 1., 1.5, 2., 4., 6., 8., 10., ] # colorbar range bounds = N.arange(0,12.1,1) 
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='zon':
				dsig=0.5
				bounds = N.arange(0,12.1,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='mer':
				dsig=0.5
				bounds = N.arange(0,12.1,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='ver':
				dsig=0.2
				bounds = N.arange(0,11,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='phi':
				dsig=5
				bounds = N.arange(0,301,30) # colorbar range
				lvls = N.arange(dsig,50,dsig)
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
			cmap.set_over('black') #upper end color
			
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(10)
			yminorLocator = MultipleLocator(10)
			
			fig=P.figure(figsize=(9,8))
			ax = fig.add_subplot(111)
			
			CS=ax.imshow(mean[im, z0:z2 + 1, y0:y2 + 1, 2], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True,extend='max') 
			cbar.ax.tick_params(labelsize=25)    
			cbar.ax.set_title(unit[iv],fontsize=20)
			CS2=P.contour(lat_grid, lev_grid, stdv[im, :, :, 2], levels=lvls, colors='white', linewidths=2)
			CS3=P.contour(lat_grid, lev_grid, stdv[im, :, :, 2], levels=lvls, colors='k', linewidths=1)
			
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.xaxis.set_tick_params(pad=12)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.figtext(0.18,0.18,'$\Delta\sigma$ = '+str(dsig)+unit2[iv],fontsize=25,backgroundcolor=(1,1,1,0.5))
			P.figtext(0.5, 0.18,'$\sigma_{max}$ = ' + str(round(N.amax(stdv[im, :, :, 2]), 1)) + unit2[iv], fontsize=25, backgroundcolor=(1, 1, 1, 0.5))
			P.title('TDT, El Nino, ' +variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'TDT_amp_' + var[iv] + '_' + month + '_' +enso +  fileformat)
	
			################ QDT #################
			
			cmap=P.get_cmap('Blues') #cmap with red and blue colors
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmaplist[0]='white'
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			if var[iv]=='tem':
				dsig=0.4
				bounds = [0.,0.1, 0.5, 1., 1.5, 2., 4., 6., 8., 10., ] # colorbar range bounds = N.arange(0,12.1,1)
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='zon':
				dsig=0.5
				bounds = N.arange(0,12.1,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='mer':
				dsig=0.5
				bounds = N.arange(0,12.1,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='ver':
				dsig=0.2
				bounds = N.arange(0,11,1) # colorbar range
				lvls = N.arange(dsig,5,dsig)
			elif var[iv]=='phi':
				dsig=5
				bounds = N.arange(0,301,30) # colorbar range
				lvls = N.arange(dsig,50,dsig)
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
			cmap.set_over('black') #upper end color
			
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(10)
			yminorLocator = MultipleLocator(10)
			
			fig=P.figure(figsize=(9,8))
			ax = fig.add_subplot(111)
			
			CS=ax.imshow(mean[im, z0:z2 + 1, y0:y2 + 1, 3], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True,extend='max') 
			cbar.ax.tick_params(labelsize=25)    
			cbar.ax.set_title(unit[iv],fontsize=20)
			CS2=P.contour(lat_grid, lev_grid, stdv[im, :, :, 3], levels=lvls, colors='white', linewidths=2)
			CS3=P.contour(lat_grid, lev_grid, stdv[im, :, :, 3], levels=lvls, colors='k', linewidths=1)
			
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.xaxis.set_tick_params(pad=12)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.figtext(0.18,0.18,'$\Delta\sigma$ = '+str(dsig)+unit2[iv],fontsize=25,backgroundcolor=(1,1,1,0.5))
			P.figtext(0.5, 0.18,'$\sigma_{max}$ = ' + str(round(N.amax(stdv[im, :, :, 3]), 1)) + unit2[iv], fontsize=25, backgroundcolor=(1, 1, 1, 0.5))
			P.title('QDT, El Nino, ' +variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'QDT_amp_' + var[iv] +'_' + month + '_' +enso +  fileformat)
			
			################## Phases ###################################################
			
			#define height and latitude range for plot:
			z0=0; z2=55
			y0=0; y2=35
			#print lev[z0],lev[z2+1],lat[y0],lat[y2+1]
			
			#phasenmittel berechnen
			for z in range(nz):
				for y in range(ny):
					
					amp= dtamp[:, im, z, y]
					pha= dtpha[:, im, z, y]
					phamean[im, z, y, 0]=vecmean(amp, pha)
					
					amp= sdtamp[:, im, z, y]
					pha= sdtpha[:, im, z, y]
					phamean[im, z, y, 1]=vecmean(amp, pha)
					
					amp= tdtamp[:, im, z, y]
					pha= tdtpha[:, im, z, y]
					phamean[im, z, y, 2]=vecmean(amp, pha)
					
					amp= qdtamp[:, im, z, y]
					pha= qdtpha[:, im, z, y]
					phamean[im, z, y, 3]=vecmean(amp, pha)
					
			###### DT ##########		
		
			cmap=P.get_cmap('Reds') #cmap with red and blue colors		
	
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			bounds = N.arange(-N.pi,1.1*N.pi,N.pi/2.) # colorbar range
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(10)
			yminorLocator = MultipleLocator(10)		
	
			fig=P.figure(figsize=(9,8))   
			ax = fig.add_subplot(111)
			CS=ax.imshow(phamean[im, z0:z2 + 1, y0:y2 + 1, 0], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True) 
			cbar.ax.tick_params(labelsize=25)
			cbar.ax.set_title('$rad$',fontsize=20)
			cbar.ax.set_yticklabels((r'$-\pi$',r'$-\pi/2$', '0', r'$\pi/2$',r'$\pi$')) 
				
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.title('DT,'+enso+', '+variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'DT_pha_' + var[iv] +'_' + month + '_' +enso +  fileformat)
			
			###### SDT ##########		
		
			cmap=P.get_cmap('Reds') #cmap with red and blue colors		
	
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			bounds = N.arange(-N.pi,1.1*N.pi,N.pi/2.) # colorbar range
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(10)
			yminorLocator = MultipleLocator(10)		
	
			fig=P.figure(figsize=(9,8))   
			ax = fig.add_subplot(111)
			CS=ax.imshow(phamean[im, z0:z2 + 1, y0:y2 + 1, 1], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True) 
			cbar.ax.tick_params(labelsize=25)
			cbar.ax.set_title('$rad$',fontsize=20)
			cbar.ax.set_yticklabels((r'$-\pi$',r'$-\pi/2$', '0', r'$\pi/2$',r'$\pi$')) 
				
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.title('SDT, '+enso+', '+variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'SDT_pha_' + var[iv] +'_' + month + '_' +enso +  fileformat)
			
			###### TDT ##########		
		
			cmap=P.get_cmap('Reds') #cmap with red and blue colors		
	
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			bounds = N.arange(-N.pi,1.1*N.pi,N.pi/2.) # colorbar range
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(20)
			yminorLocator = MultipleLocator(10)		
	
			fig=P.figure(figsize=(9,8))   
			ax = fig.add_subplot(111)
			CS=ax.imshow(phamean[im, z0:z2 + 1, y0:y2 + 1, 2], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True) 
			cbar.ax.tick_params(labelsize=25)
			cbar.ax.set_title('$rad$',fontsize=20)
			cbar.ax.set_yticklabels((r'$-\pi$',r'$-\pi/2$', '0', r'$\pi/2$',r'$\pi$')) 
				
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.xaxis.set_tick_params(pad=12)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.title('TDT,'+enso+', '+variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'TDT_pha_' + var[iv] +'_' + month + '_' +enso +  fileformat)
			
			###### QDT ##########		
		
			cmap=P.get_cmap('Reds') #cmap with red and blue colors		
	
			#make descrete areas in colorbar
			cmaplist=[cmap(i) for i in range(cmap.N)]
			cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N) 
			bounds = N.arange(-N.pi,1.1*N.pi,N.pi/2.) # colorbar range
			norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	
			#define grid that is shown in the plot
			xmajorLocator = MultipleLocator(30)
			majorFormatter = FormatStrFormatter('%d')
			xminorLocator = MultipleLocator(10)
			ymajorLocator = MultipleLocator(10)
			yminorLocator = MultipleLocator(10)		
	
			fig=P.figure(figsize=(9,8))   
			ax = fig.add_subplot(111)
			CS=ax.imshow(phamean[im, z0:z2 + 1, y0:y2 + 1, 3], cmap, origin='lower', interpolation='none', norm=norm, extent=[lat[y0], lat[y2 + 1], lev[z0], lev[z2 + 1]], aspect='auto')
			cbar=P.colorbar(CS,use_gridspec=True) 
			cbar.ax.tick_params(labelsize=25)
			cbar.ax.set_title('$rad$',fontsize=20)
			cbar.ax.set_yticklabels((r'$-\pi$',r'$-\pi/2$', '0', r'$\pi/2$',r'$\pi$')) 
				
			ax.xaxis.set_major_locator(xmajorLocator)
			ax.xaxis.set_major_formatter(majorFormatter)
			ax.xaxis.set_minor_locator(xminorLocator)
			ax.tick_params(axis='x', direction='out',pad=12)
			P.xticks(size=25)
	
			P.ylim(lev[z0],lev[z2+1]) 
			ax.yaxis.set_major_locator(ymajorLocator)
			ax.yaxis.set_major_formatter(majorFormatter)
			ax.yaxis.set_minor_locator(yminorLocator)
			ax.tick_params(axis='y', direction='out',pad=16)
			P.yticks(size=25)
	
			P.grid(b=True, which='major', color='gray', linestyle='--')
	
			P.xlabel(r'Latitude ($^\circ$)',fontsize=25)
			P.ylabel(r'Log-Pressure Height (km)',fontsize=25)
			P.title('QDT, '+enso+', '+variable[iv]+', '+month,fontsize=25)
			P.tight_layout()
			P.savefig(path +'QDT_pha_' + var[iv] +'_' + month + '_' +enso +  fileformat)
			
			P.close("all")