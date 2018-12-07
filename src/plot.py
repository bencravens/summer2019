"""script file containing tools for plotting data grabbed from NETCDF4 files"""

#IMPORT LIBRARIES
import grab
import grabtest
import mystats
from netCDF4 import *
import os
import numpy as np
import matplotlib.pyplot as plt
import time
import statistics as stats
from mpl_toolkits.basemap import Basemap
import cmocean.cm as cmo
import scipy
from scipy import stats

######## ICE AREA SPECIFIC DATA GRABBING FUNCTIONS ###############################

def ice_area_seasonal_main():
	"""grabbing dataset for all models, calculating seasonal ice area, plotting."""
	#vectorizing plotting routine
	models = ["at053", "au866", "av231", "au872", "au874"]
	models2 = ["au866","au874","av231","at053","au872"]
	testmodels = ["au874"]
	for i, model in enumerate(models):
		tempstd,tempmean,tempmax,tempmin = grab.ice_area_seasonal("/media/windowsshare", "u-{}".format(model))
		print "the minimum areas are {}".format(tempmin)
		plot(range(1,13),tempmean,'Months of the year','Sea ice area (m^2)', '{} - Seasonal'.format(model),[3,2,i+1],tempstd,tempmax,tempmin)
	elapsed = time.time() - t
	print "Elapsed time is {}".format(elapsed)
	plt.show()

def ice_area_tseries_main():
	"""makes a nice time series plot for ice area of a given model..."""
	ice_area = grab.ice_area_tseries("/media/windowsshare","u-at053")
	plt.plot(ice_area)
	plt.title("Sea ice area from 1990-2009 for control model")
	plt.xlabel("Time (months)")
	plt.ylabel("Total antarctic sea ice area (m^2)")
	plt.show()

def ice_area_month_main():
	"""makes a time series plot of ice area for a given month"""
	ice_area = grab.ice_area_month("/media/windowsshare","u-at053",2) #grabbing data for feb, (i.e) month=2	
	plt.plot(ice_area)
	plt.title("Sea ice area from 1990-2009 for the month of February")
	plt.xlabel("Years since 1990")
	plt.ylabel("Total antarctic sea ice area (m^2)")
	std_dev = stats.stdev(ice_area)*np.ones(len(ice_area))
	xvals = np.linspace(0,19,20,dtype='int')
	plt.fill_between(xvals,ice_area+std_dev,ice_area-std_dev,facecolor='green',alpha=0.2,linestyle="--")
	plt.show()

############### GENERAL FUNCTIONS FOR MAP PLOTTING ##################################

def month_map_mean_main(modelname,monthnum,varname):
	"""function called when map plots of mean of variable varname are wanted..."""
	lons,lats,myvar = grab.month_map_mean("/media/windowsshare",modelname,monthnum,varname) #grabbing data
	fig,ax=plt.subplots(figsize=(8,8))
	m = Basemap(resolution='h',projection='spstere',lat_0=-90,lon_0=-180,boundinglat=-55)
	m.drawcoastlines(linewidth=1)
	m.fillcontinents(color='grey')
	m.drawmapboundary(linewidth=1)
	cm = m.pcolormesh(lons,lats,myvar,latlon=True)
	monthdict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}	
	plt.title("map plot for {} mean {} in the month of {}".format(modelname,varname,monthdict[monthnum])) 
	cbar = m.colorbar(cm,location='bottom',pad="5%")
	cbar.set_label('{} in grid cell'.format(varname))
	fig.savefig('/home/ben/Desktop/mapplots/{}-{}-{}'.format(modelname,varname,monthnum))	

def month_map_anom_main(modelname,monthnum,varname):
	"""function called when anomaly map plots of variable varname are wanted..."""
	lons,lats,myvar,total_diff = grab.month_map_anom("/media/windowsshare",modelname,monthnum,varname) #grabbing data
	fig,ax=plt.subplots(figsize=(8,8))
	m = Basemap(resolution='h',projection='spstere',lat_0=-90,lon_0=-180,boundinglat=-55)
	m.drawcoastlines(linewidth=1)
	m.fillcontinents(color='grey')
	m.drawmapboundary(linewidth=1)
	cm = m.pcolormesh(lons,lats,myvar,latlon=True,cmap='seismic')
	monthdict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}	
	plt.title("Control - {} in the month of {} \n variable plotted is {} \n total difference is {}".format(modelname, monthdict[monthnum],varname,total_diff)) 
	cbar = m.colorbar(cm,location='bottom',pad="5%")
	cbar.set_label('change in variable {}'.format(varname))
	plt.clim(-1.0,1.0) #one may have to adjust clim depending on variable...
	fig.savefig('/home/ben/Desktop/anomplots/{}-{}-{}'.format(modelname,varname,monthnum))	

def month_map_variance_main(modelname,monthnum,varname):
	"""plots the variance of a seasonal variable myvar for a given model and month"""
	lons, lats, myvar = grab.month_map_stddev("/media/windowsshare",modelname,monthnum,varname)
	fig,ax=plt.subplots(figsize=(8,8))
	m = Basemap(resolution='h',projection='spstere',lat_0=-90,lon_0=-180,boundinglat=-55)
	m.drawcoastlines(linewidth=1)
	m.fillcontinents(color='grey')
	m.drawmapboundary(linewidth=1)
	cm = m.pcolormesh(lons,lats,np.multiply(myvar,myvar),latlon=True,cmap='Blues') #doing np.multiply to get the variance, which is the square of the std-dev
	monthdict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}	
	plt.title("variance of {} for model {} in the month of {}".format(varname, modelname,monthdict[monthnum])) 
	cbar = m.colorbar(cm,location='bottom',pad="5%")
	cbar.set_label('variance in variable {}'.format(varname))
	fig.savefig('/home/ben/Desktop/varplots/{}-{}-{}'.format(modelname,varname,monthnum))	

def t_test_main(modelname,monthnum,varname,pval_filter,t_or_p):
	"""performs the student's t-test on each gridpoint. if t_or_p is true, plots the t-statistic scalar field, else plots the p value."""
	lons,lats,myvar = grab.month_map_data("/media/windowsshare",modelname,monthnum,varname)
	lons,lats,controlvar = grab.month_map_data("/media/windowsshare","u-at053",monthnum,varname)

	#now performing the t-test
	#myvar and controlvar should be the same shape
	assert controlvar.shape == myvar.shape
	[z,x,y] = myvar.shape
	
	#now making an empty array to chuck results into
	tstats = np.ma.zeros([x,y])
	pvals = np.ma.zeros([x,y])
	for i in xrange(x):
		for j in xrange(y):
			tstats[i,j], pvals[i,j] = scipy.stats.mstats.ttest_ind(controlvar[:,i,j],myvar[:,i,j])
	
	tstats = np.ma.masked_where(pvals>pval_filter,tstats)
	fig,ax=plt.subplots(figsize=(8,8))
	m = Basemap(resolution='h',projection='spstere',lat_0=-90,lon_0=-180,boundinglat=-55)
	m.drawcoastlines(linewidth=1)
	#m.fillcontinents(color='grey')
	m.drawlsmask(land_color='grey',ocean_color='aqua',lakes=True)
	m.drawmapboundary(linewidth=1)
	if t_or_p:
		cm = m.pcolormesh(lons,lats,tstats,latlon=True,cmap='seismic')
		monthdict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}			
		plt.title("tstatistic of {} for model {} in the month of {}\n plotted where pval <{}".format(varname, modelname,monthdict[monthnum],pval_filter)) 
		cbar = m.colorbar(cm,location='bottom',pad="5%")
		cbar.set_label('tstatistic of {}'.format(varname))
		fig.savefig('/home/ben/Desktop/tstatplots/{}-{}-{}_tstat'.format(modelname,varname,monthnum))	
	else:
		cm = m.pcolormesh(lons,lats,pvals,latlon=True,cmap='seismic')
		monthdict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}	
		plt.title("pvalues of {} for model {} in the month of {}".format(varname, modelname,monthdict[monthnum])) 
		cbar = m.colorbar(cm,location='bottom',pad="5%")
		cbar.set_label('pvalues of {}'.format(varname))
		fig.savefig('/home/ben/Desktop/tstatplots/{}-{}-{}_pval'.format(modelname,varname,monthnum))	
	
def plot(input_x,input_y,xlab,ylab,title,plotarr,std_devs,maxes,mins):
	"""plots a given dataset given inputs, titles and graph labels etc"""
	plt.subplot(plotarr[0],plotarr[1], plotarr[2])
	plt.plot(input_x,input_y)
	plt.plot(input_x,maxes,color='r',linestyle=":")
	plt.plot(input_x,mins,color='r',linestyle=":")
	plt.ylabel(ylab)
	plt.xlabel(xlab)
	plt.title(title)
	xmin = min(input_x)
	xmax = max(input_x)
	ymin = min(input_y)
	ymax = max(input_y)
	plt.xlim([xmin,xmax])
	plt.ylim([ymin*0.9,ymax*1.1])
	#now plotting the fill between the mean value +- the standard deviation
	plt.fill_between(input_x,input_y-std_devs,input_y+std_devs,facecolor='green',alpha=0.2,linestyle="--")
	plt.tight_layout() #making sure the plots do not overlap...


if __name__=='__main__':
	models = ["u-au866","u-av231","u-au872","u-au874","u-at053"]
	months = [2,9]
	for model in models:
		for month in months:
			t_test_main(model,month,"aice",1.0,False)
			t_test_main(model,month,"aice",0.05,True)	
