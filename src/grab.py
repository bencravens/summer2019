"""script to import variables from NetCDF files on high capacity storage."""
import os
from netCDF4 import Dataset
import numpy as np
import sys

######## SPECIFIC DATA GRABBING FUNCTIONS ###############################

def ice_area_seasonal(path, modelname):
    """grabs mean total sea ice area for each month given the name of model one wants and the path to the model files"""
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    filecount = len(os.listdir('./'))

    # now we will sort the files based on month.
    # assumes same number of files for each month
    monthareas = np.ma.zeros([12, filecount/12], dtype='float64')
    monthcount = np.zeros(12)
    stdevs = np.ma.zeros(12, dtype='float64')
    means = np.ma.zeros(12, dtype='float64')
    maxes = np.ma.zeros(12, dtype='float64')
    mins = np.ma.zeros(12, dtype='float64')
    for filenum, filename in enumerate(os.listdir('./')):
        print filename
        testdata = Dataset(filename)
        # now grabbing latitude just to check if we are in the southern hemisphere (some data is full world)
        lats = np.ma.array(testdata.variables['TLAT'][:, :], dtype='float64')
        cond = lats <= 0  # if we are below the equator, grab
        if filenum == 0:
            tarea = np.ma.array(
                testdata.variables['tarea'][:, :], dtype='float64')[cond]
        # grabbing month value from filename... format does not vary
        monthstr = filename[19:21]
        monthnum = int(monthstr)-1

        print "the month we are grabbing is {}".format(monthstr)
        print "Grabbing {}, file {} of {}".format(filename, filenum, filecount)
        aice = np.ma.squeeze(np.ma.array(
            testdata.variables['aice'][:, :], dtype='float64'))[cond]
        # adding total ice area into its respective month bin
        # catching weird error as one or two files are invalid
        try:
            monthareas[monthnum, monthcount[monthnum]] = np.ma.sum(aice*tarea)
        except:
            print "Error:", sys.exc_info()[0]
        monthcount[monthnum] += 1 
        testdata.close()
        # now converting to numpy array

    # now calculating the mean for each month and returning that value, as well as the standard deviation for each month.
    # first masking the mins value correctly so that it does not count "0" entries
    [x, y] = monthareas.shape
    for i in xrange(x):
        for j in xrange(y):
            if monthareas[i, j] == 0:
                monthareas[i, j] = np.ma.masked

    for i in xrange(12):
        stdevs[i] = np.ma.std(monthareas[i, :])
        means[i] = np.ma.mean(monthareas[i, :])
        maxes[i] = np.ma.max(monthareas[i, :])
        mins[i] = np.ma.min(monthareas[i, :])

    return stdevs, means, maxes, mins

def ice_volume_seasonal(path, modelname):
    """grabs mean total sea ice volume for each month given the name of model one wants and the path to the model files"""
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    filecount = len(os.listdir('./'))

    # now we will sort the files based on month.
    # assumes same number of files for each month
    monthvolumes = np.ma.zeros([12, filecount/12], dtype='float64')
    monthcount = np.zeros(12)
    stdevs = np.ma.zeros(12, dtype='float64')
    means = np.ma.zeros(12, dtype='float64')
    maxes = np.ma.zeros(12, dtype='float64')
    mins = np.ma.zeros(12, dtype='float64')
    for filenum, filename in enumerate(os.listdir('./')):
        print filename
        testdata = Dataset(filename)
        # now grabbing latitude just to check if we are in the southern hemisphere (some data is full world)
        lats = np.ma.array(testdata.variables['TLAT'][:, :], dtype='float64')
        cond = lats <= 0  # if we are below the equator, grab
        if filenum == 0:
            tarea = np.ma.array(
                testdata.variables['tarea'][:, :], dtype='float64')[cond]
        # grabbing month value from filename... format does not vary
        monthstr = filename[19:21]
        monthnum = int(monthstr)-1

        print "the month we are grabbing is {}".format(monthstr)
        print "Grabbing {}, file {} of {}".format(filename, filenum, filecount)
        aice = np.ma.squeeze(np.ma.array(
            testdata.variables['aice'][:, :], dtype='float64'))[cond]
        sithick = np.ma.squeeze(np.ma.array(
            testdata.variables['sithick'][:,:],dtype='float64'))[cond]
        # catching weird error as one or two files are invalid
        try:
            monthvolumes[monthnum, monthcount[monthnum]] = np.ma.sum(aice*tarea*sithick)
        except:
            print "Error:", sys.exc_info()[0]
        monthcount[monthnum] += 1 
        testdata.close()
        # now converting to numpy array

    # now calculating the mean for each month and returning that value, as well as the standard deviation for each month.
    # first masking the mins value correctly so that it does not count "0" entries
    [x, y] = monthvolumes.shape
    for i in xrange(x):
        for j in xrange(y):
            if monthvolumes[i, j] == 0:
                monthvolumes[i, j] = np.ma.masked

    for i in xrange(12):
        stdevs[i] = np.ma.std(monthvolumes[i, :])
        means[i] = np.ma.mean(monthvolumes[i, :])
        maxes[i] = np.ma.max(monthvolumes[i, :])
        mins[i] = np.ma.min(monthvolumes[i, :])

    return stdevs, means, maxes, mins

def ice_area_tseries(path, modelname):
    """makes a time series plot of a certain model """
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))

    # declaring array to hold ice areas for each timestep
    ice_area = []

    # sorting the files and appending the mean of each to an array
    for i, filename in enumerate(sorted(os.listdir('./'))):
        print filename  # just making sure we are grabbing files in order...
        testdata = Dataset(filename)
        if i == 0:
            tarea = np.ma.array(
                testdata.variables['tarea'][:, :], dtype='float64')
        aice = np.ma.squeeze(np.ma.array(
            testdata.variables['aice'][:, :], dtype='float64'))
        ice_area.append(np.ma.sum(aice*tarea))
        testdata.close()

    # Now that we have all of the data we will return it
    return ice_area


def ice_area_month(path, modelname, monthnum):
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    ice_area = []
    monthcount = 0

    for filename in (sorted(os.listdir('./'))):
        # grabbing month from filename
        monthstr = filename[19:21]
        # we only want the files of a certain month given by monthnum
        if int(monthstr) == monthnum:
            testdata = Dataset(filename)
            # want to make sure we are in the southern hemisphere
            lats = np.ma.array(
                testdata.variables['TLAT'][:, :], dtype='float64')
            cond = lats <= 0  # if out latitude is below the equator...
            if monthcount == 0:
                tarea = np.ma.array(
                    testdata.variables['tarea'][:, :], dtype='float64')[cond]
            aice = np.ma.squeeze(np.ma.array(
                testdata.variables['aice'][:, :], dtype='float64'))[cond]
            print "reached fine"
            print "aice shape is {}".format(aice.shape)
            print "tarea shape is {}".format(tarea.shape)
            try:
                ice_area.append(np.ma.sum(aice*tarea))
                print "area added is {}".format(np.ma.sum(aice*tarea))
            except:
                print "Error:", sys.exc_info()[0]
            monthcount += 1  # we have added the data for one month
    return ice_area

def ice_volume_month(path, modelname, monthnum):
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    ice_volume = []
    monthcount = 0

    for filename in (sorted(os.listdir('./'))):
        # grabbing month from filename
        monthstr = filename[19:21]
        # we only want the files of a certain month given by monthnum
        if int(monthstr) == monthnum:
            testdata = Dataset(filename)
            # want to make sure we are in the southern hemisphere
            lats = np.ma.array(
                testdata.variables['TLAT'][:, :], dtype='float64')
            cond = lats <= 0  # if out latitude is below the equator...
            if monthcount == 0:
                tarea = np.ma.array(
                    testdata.variables['tarea'][:, :], dtype='float64')[cond]
            aice = np.ma.squeeze(np.ma.array(
                testdata.variables['aice'][:, :], dtype='float64'))[cond]
            sithick = np.ma.squeeze(np.ma.array(
                testdata.variables['sithick'][:,:],dtype='float64'))[cond]
            try:
                ice_volume.append(np.ma.sum(aice*tarea))
                print "volume added is {}".format(np.ma.sum(aice*tarea*sithick))
            except:
                print "Error:", sys.exc_info()[0]
            monthcount += 1  # we have added the data for one month
    return ice_volume

#
############### GENERAL FUNCTIONS FOR DATA GRABBING ##################################

def month_map_mean(path, modelname, monthnum, varname,isice):
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    monthcount = 0
    for filename in (sorted(os.listdir('./'))):
        # grabbing month from filename
        monthstr = filename[19:21]
        # we only want the files of a certain month given by monthnum
        if int(monthstr) == monthnum:
            print "grabbing {}".format(filename)
            testdata = Dataset(filename)
            if monthcount == 0:  # latitude and longitude of grid cells does not change... also dims of myvar dont change
                lats = np.ma.array(
                    testdata.variables['TLAT'][:, :], dtype='float64')
                lons = np.ma.array(
                    testdata.variables['TLON'][:, :], dtype='float64')
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))
                aice = np.ma.squeeze(np.ma.array(
                    testdata.variables['aice'][:,:], dtype='float64'))
                if isice==False:
                    #if the variable is not aice, set all sections where there is no ice to NaN as there should be no data here...
                    cond = aice == 0
                    myvar = np.ma.masked_where(cond,myvar)
                myvar_total = []  # making total myvar
                myvar_total.append(myvar)
                #we want to grab the units from the netCDF file so that we can add them to the plot...
                units = testdata.variables[varname].units 
                testdata.close()
                monthcount += 1
            else:
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))
                if isice==False:
                    #if the variable is not aice, set all sections where there is no ice to NaN as there should be no data here...
                    aice = np.ma.squeeze(np.ma.array(
                        testdata.variables['aice'][:,:], dtype='float64'))
                    cond = aice == 0
                    myvar = np.ma.masked_where(cond,myvar)
                myvar_total.append(myvar)
                # making sure we don't have too many files open at once...
                testdata.close()
                monthcount += 1  # we have added the data for one month.
    #now taking mean of all datapoints
    #first convert to np.ma array
    myvar_total = np.ma.asarray(myvar_total)
    means = myvar_total.mean(axis=0)
    return lons, lats, means, units


def month_map_anom(path, modelname, monthnum, varname,isice):
    """this function loads in the control model (u-at053), and makes map plots of average monthly difference between it and a given model for a parameter."""
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    monthcount = 0
    for filename in (sorted(os.listdir('./'))):
        # grabbing month from filename
        monthstr = filename[19:21]
        # we only want the files of a certain month given by monthnum
        if int(monthstr) == monthnum:
            print "grabbing {}".format(filename)
            testdata = Dataset(filename)
            if monthcount == 0:  # latitude and longitude of grid cells does not change... also dims of myvar dont change
                lats = np.ma.array(
                    testdata.variables['TLAT'][:, :], dtype='float64')
                cond = lats < -50.0  # we only want stuff near antarctica
                lons = np.ma.array(
                    testdata.variables['TLON'][:, :], dtype='float64')[cond]
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                aice = np.ma.squeeze(np.ma.array(
                    testdata.variables['aice'][:,:], dtype='float64'))[cond]
                if isice==False:
                    #if the variable is not aice, set all sections where there is no ice to NaN as there should be no data here...
                    icecond = aice == 0
                    print "icecond shape is {}, myvar shape is {}".format(icecond.shape,myvar.shape)
                    myvar = np.ma.masked_where(icecond,myvar)
                lats = lats[cond]
                # size should be the same for all of them...
                size = lons.shape[0]
                # now reshaping to be proper size
                lats = np.reshape(lats, [int(size/360.0), 360])
                lons = np.reshape(lons, [int(size/360.0), 360])
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                myvar_total = []
                myvar_total.append(myvar)
                units = testdata.variables[varname].units
                testdata.close()
                monthcount += 1
            else:
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                aice = np.ma.squeeze(np.ma.array(
                    testdata.variables['aice'][:,:], dtype='float64'))[cond]
                if isice==False:
                    #if the variable is not aice, set all sections where there is no ice to NaN as there should be no data here...
                    icecond = aice == 0
                    print "icecond shape is {}, myvar shape is {}".format(icecond.shape,myvar.shape)
                    myvar = np.ma.masked_where(icecond,myvar)
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                myvar_total.append(myvar)
                # making sure we don't have too many files open at once...
                testdata.close()
                monthcount += 1  # we have added the data for one month.
    myvar_total = np.ma.asarray(myvar_total)
    myvar_total_mean = myvar_total.mean(axis=0)

    # now grabbing control model total amount of variable... "gridsize * value at each grid"
    os.chdir("../../u-at053/ice/")
    monthcount = 0
    for filename in (sorted(os.listdir('./'))):
        monthstr = filename[19:21]
        # we only want the files of a certain month given by monthnum
        if int(monthstr) == monthnum:
            print "grabbing CONTROL: {}".format(filename)
            testdata = Dataset(filename)
            if monthcount == 0:  # dims of myvar dont change
                lats = np.ma.array(
                    testdata.variables['TLAT'][:, :], dtype='float64')
                cond = lats < -50.0
                tarea = np.ma.array(
                    testdata.variables['tarea'][:, :], dtype='float64')[cond]
                lons = np.ma.array(
                    testdata.variables['TLON'][:, :], dtype='float64')[cond]
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                aice = np.ma.squeeze(np.ma.array(
                    testdata.variables['aice'][:,:], dtype='float64'))[cond]
                if isice==False:
                    #if the variable is not aice, set all sections where there is no ice to NaN as there should be no data here...
                    icecond = aice == 0
                    print "icecond shape is {}, myvar shape is {}".format(icecond.shape,myvar.shape)
                    myvar = np.ma.masked_where(icecond,myvar)
                lats = lats[cond]
                # size should be the same for all of them...
                size = lons.shape[0]
                # now reshaping to be proper size
                lats = np.reshape(lats, [int(size/360.0), 360])
                lons = np.reshape(lons, [int(size/360.0), 360])
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                tarea = np.reshape(tarea, [int(size/360.0), 360])
                myvar_total_control = []  # making total myvar
                myvar_total_control.append(myvar)
                testdata.close()
                monthcount += 1
            else:
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                aice = np.ma.squeeze(np.ma.array(
                    testdata.variables['aice'][:,:], dtype='float64'))[cond]
                if isice==False:
                    #if the variable is not aice, set all sections where there is no ice to NaN as there should be no data here...
                    icecond = aice == 0
                    print "icecond shape is {}, myvar shape is {}".format(icecond.shape,myvar.shape)
                    myvar = np.ma.masked_where(icecond,myvar)
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                myvar_total_control.append(myvar)
                # making sure we don't have too many files open at once...
                testdata.close()
                monthcount += 1  # we have added the data for one month.
    myvar_total_control = np.ma.asarray(myvar_total_control)
    myvar_total_control_mean = myvar_total_control.mean(axis=0)

    # convention is model - control
    # total myvar difference by gridpoint
    myvar_diff = myvar_total_mean - myvar_total_control_mean
    # now finding the total difference in m^2
    total_diff = np.ma.sum(myvar_diff*tarea)

    # now returning the lon,lat and anomaly of myvar
    return lons, lats, myvar_diff, total_diff, units


def month_map_stddev(path, modelname, monthnum, varname):
    """given a path to a model, the name of the model and a number denoting a month, calculate the std_dev of the variable given for that month at each gridpoint"""
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    monthcount = 0
    varlist = []
    for filename in (sorted(os.listdir('./'))):
        # grabbing month from filename
        monthstr = filename[19:21]
        # we only want the files of a certain month given by monthnum
        if int(monthstr) == monthnum:
            print "grabbing {}".format(filename)
            testdata = Dataset(filename)
            if monthcount == 0:  # dims of aice dont change
                lats = np.ma.array(
                    testdata.variables['TLAT'][:, :], dtype='float64')
                cond = lats < -50.0
                # now grabbing the variable we want
                lons = np.ma.array(
                    testdata.variables['TLON'][:, :], dtype='float64')[cond]
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                lats = lats[cond]
                # size should be the same for all of them...
                size = myvar.shape[0]
                # now reshaping to be proper size
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                lats = np.reshape(lats, [int(size/360.0), 360])
                lons = np.reshape(lons, [int(size/360.0), 360])
                varlist.append(myvar)
                testdata.close()
                monthcount += 1
            else:
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                varlist.append(myvar)
                # making sure we don't have too many files open at once...
                testdata.close()
                monthcount += 1  # we have added the data for one month.

    # now we will calculate the standard deviation of the variable list and return it
    varlist = np.asarray(varlist)
    return lons, lats, np.std(varlist, axis=0)


def month_map_data(path, modelname, monthnum, varname):
    """grabs and returns a stack of arrays for the value of varname for model modelname during a given month"""
    os.chdir("../../../../")
    os.chdir("{}/{}/{}".format(path, modelname, "ice"))
    monthcount = 0
    varlist = []
    for filename in (sorted(os.listdir('./'))):
        # grabbing month from filename
        monthstr = filename[19:21]
        # we only want the files of a certain month given by monthnum
        if int(monthstr) == monthnum:
            print "grabbing {}".format(filename)
            testdata = Dataset(filename)
            if monthcount == 0:  # dims of aice dont change
                lats = np.ma.array(
                    testdata.variables['TLAT'][:, :], dtype='float64')
                cond = lats < -50.0
                # now grabbing the variable we want
                lons = np.ma.array(
                    testdata.variables['TLON'][:, :], dtype='float64')[cond]
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                lats = lats[cond]
                # size should be the same for all of them...
                size = myvar.shape[0]
                # now reshaping to be proper size
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                lats = np.reshape(lats, [int(size/360.0), 360])
                lons = np.reshape(lons, [int(size/360.0), 360])
                varlist.append(myvar)
                testdata.close()
                monthcount += 1
            else:
                myvar = np.ma.squeeze(np.ma.array(
                    testdata.variables[str(varname)][:, :], dtype='float64'))[cond]
                myvar = np.reshape(myvar, [int(size/360.0), 360])
                varlist.append(myvar)
                # making sure we don't have too many files open at once...
                testdata.close()
                monthcount += 1  # we have added the data for one month.

    varlist = np.asarray(varlist)
    return lons, lats, varlist
