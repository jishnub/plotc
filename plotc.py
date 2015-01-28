from __future__ import division
from matplotlib import ticker,cm,colors,pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

show=plt.show

def colorplot(arr,**kwargs):
	arr=np.squeeze(arr)
	ash=arr.shape
	try: assert len(ash) == 2
	except AssertionError: 
		print "Colorplot requires 2D arrays"
		print "Size of array provided is",str(ash)+", dimension is",len(ash)
		return
	
	if arr.dtype=='complex128' or arr.dtype=='complex64':
		print "Ignoring imaginary part"
		arr=np.real(arr)
	
	x=kwargs.get('x',None)
	x2=kwargs.get('x2',None)
	y=kwargs.get('y',None)
	y2=kwargs.get('y2',None)
	xr=kwargs.get('xr',None)
	yr=kwargs.get('yr',None)
	subplot_index=kwargs.get('subplot_index',111)
	if not subplot_index_is_valid(subplot_index): return
	colorbar=kwargs.get('colorbar',True)
	colorbar_scientific=kwargs.get('cbar_sci',False)
	xlabel=kwargs.get('xlabel',None)
	ylabel=kwargs.get('ylabel',None)
	title=kwargs.get('title',None)
	cmap=kwargs.get('cmap',None)
	zorder=kwargs.get('zorder',0)
	centerzero=kwargs.get('centerzero',False)	
	flipy=kwargs.get('flipy',False)
	flipx=kwargs.get('flipx',False)
	xtickpad=kwargs.get('xtickpad',6.)
	ytickpad=kwargs.get('ytickpad',6.)
	int_ticks=kwargs.get('int_ticks',True)
	int_ticks2=kwargs.get('int_ticks2',True)
	x1bins=kwargs.get('x1bins',10)
	y1bins=kwargs.get('y1bins',10)
	x2bins=kwargs.get('x2bins',5)
	y2bins=kwargs.get('y2bins',5)
	polar=kwargs.get('polar',False)
	
	amin=arr.min()
	amax=arr.max()
	
	vmin=kwargs.get('vmin',amin)
	vmax=kwargs.get('vmax',amax)
	if centerzero:	vmin,vmax=center_range_around_zero(vmin,vmax,amin,amax)
	
	
	
	if int(subplot_index) ==111: plt.clf(); 
	
	fig=plt.gcf()	
	if polar: 
		print "Note: Assuming x is theta and y is r"
		print "If plot looks correct you may safely ignore this"
		print "If plot looks weird you might want to specify x and y"

	plt.subplot(subplot_index,polar=polar)
	ax=plt.gca()

	
	#~ Set scientific notation on colorbar for small or large values
	cbar_clip=max(abs(vmax),abs(vmin))
	if cbar_clip>1e4 or cbar_clip<1e-2: colorbar_scientific=True
	
	#~ Define the coordinate grid, if unspecified
	if x is None and y is None:
		x=np.arange(ash[1])
		y=np.arange(ash[0])
	elif x is None and y is not None:
		x=np.arange(ash[1])
	elif x is not None and y is None:
		y=np.arange(ash[0])
	
	#~ Change 2D coordinate meshgrids to 1D
	if len(x.shape) == 2:	x=x[0]
	if len(y.shape) == 2:	y=y[:,0]
	
	#~ Check if sizes match
	Nx=len(x);Ny=len(y)	
	try:	assert Nx==ash[1] and Ny==ash[0]
	except AssertionError:
		if Nx==ash[0] and Ny==ash[1]: arr=arr.T
		elif Nx==ash[1] and Ny!=ash[0]: 
			print "Array sizes do not match"
			print "Size of array",ash
			print "Length of y array is "+str(Ny)+", required size is",ash[0]
			return
		elif Ny==ash[0] and Nx!=ash[1]:
			print "Array sizes do not match"
			print "Size of array",ash
			print "Length of x array is "+str(Nx)+", required size is",ash[1]
			return
		else:
			print "Array sizes do not match"
			print "Size of array",ash
			print "Length of x array is "+str(Nx)+", required size is",ash[1]
			print "Length of y array is "+str(Ny)+", required size is",ash[0]
			return
	
	#~ Shift axis grid from boundaries to centers of grid squares
	#~ dx=x[-1]-x[-2];dy=y[-1]-y[-2]
	#~ xlast=x[-1]+dx;ylast=y[-1]+dy
#~ 
	#~ Boundary trick from http://alex.seeholzer.de/2014/05/fun-with-matplotlib-pcolormesh-getting-data-to-display-in-the-right-position/
	#~ xgrid=np.insert(x,len(x),xlast)-dx/2
	#~ ygrid=np.insert(y,len(y),ylast)-dy/2
	
	xgrid,ygrid=get_centered_grid_for_pcolormesh(x,y)
	
	Xax,Yax=np.meshgrid(xgrid,ygrid)

	
	#~ Set ranges of axis ticks
	set_axis_limits(xgrid,ygrid,xr,yr)	
	
	if int_ticks: ax.get_xaxis().set_major_locator(ticker.MaxNLocator(nbins=x1bins,integer=True))
	if int_ticks: ax.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=y1bins,integer=True))
	
	
	#~ Take care of empty colorbar range
	if vmin==vmax: 		
		print "Constant colorbar range, colorbar will reflect an offset of 10^-10"
		vmax=vmin+1e-10
		colorbar_scientific=True
	
	
	#~ Actual plot
	if cmap is None: cmap=get_appropriate_colormap(vmin,vmax)
	p=plt.pcolormesh(Xax,Yax,arr,cmap=cmap,vmin=vmin,vmax=vmax,zorder=zorder)
	
	
	
	if colorbar: cb=generate_colorbar(colorbar_scientific=colorbar_scientific)	
	
	if x2 is not None: 
		ax2=plt.twiny(ax=ax)
		dx=x2[1]-x2[0]
		x2,_=get_centered_grid_for_pcolormesh(x=x2,y=None)
		
		ax2.set_xlim(x2[0],x2[-1])
		
		if int_ticks2: ax2.get_xaxis().set_major_locator(ticker.MaxNLocator(nbins=x2bins,integer=True))
		
	if y2 is not None: 
		ax2=plt.twinx(ax=ax)
		_,y2=get_centered_grid_for_pcolormesh(x=None,y=y2)
		
		ax2.set_ylim(y2[0],y2[-1])
		
		if int_ticks2: ax2.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=y2bins,integer=True))
	
	if flipx: ax.invert_xaxis()
	if flipy: ax.invert_yaxis()
	
	for tick in ax.get_xaxis().get_major_ticks():
		tick.set_pad(xtickpad)
		tick.label1 = tick._get_text1()
		
	for tick in ax.get_yaxis().get_major_ticks():
		tick.set_pad(ytickpad)
		tick.label1 = tick._get_text1()
	
	if xlabel: ax.set_xlabel(xlabel)
	if ylabel: ax.set_ylabel(ylabel)
	if title:  ax.set_title(title)
	
	
	
	
def plot1D(y,**kwargs):
	x=kwargs.get('x',None)
	xr=kwargs.get('xr',None)
	yr=kwargs.get('yr',None)
	subplot_index=kwargs.get('subplot_index',None)
	if not subplot_index_is_valid(subplot_index): return
	xlabel=kwargs.get('xlabel',None)
	ylabel=kwargs.get('ylabel',None)
	title=kwargs.get('title',None)
	zorder=kwargs.get('zorder',0)
	
	ymin=y.min()
	ymax=y.max()
	
	ax=plt.gca()
	prev_ymin,prev_ymax=ax.get_ylim()
	
	ys=y.shape
	try:
		assert ys
		assert ys[0]
	except AssertionError:
		print "Zero length sequence can't be plotted"
		return
	Ny=1
	if len(ys)==1:	Npts=ys[0]
	else: 
		Ny=ys[0]
		Npts=ys[1]
	
	if subplot_index is not None:
		plt.subplot(subplot_index)
		
	if x is None:	x=np.arange(Npts)
	
	if xr is None:			plt.xlim(x[0],x[-1])
	elif xr[0] is None:		plt.xlim(x[0],xr[1])
	elif xr[1] is None:		plt.xlim(xr[0],x[-1])
	else:					plt.xlim(xr)
	
	if yr is None:
		if ymax>prev_ymax and ymin<prev_ymin:
			plt.ylim(ymin,ymax)
		elif ymax>prev_ymax and ymin>=prev_ymin:
			plt.ylim(prev_ymin,ymax)
		elif ymax<=prev_ymax and ymin<prev_ymin:
			plt.ylim(ymin,prev_ymax)
	elif yr[0] is None:
		if ymin<prev_ymin:
			plt.ylim(ymin,yr[0])
		else:
			plt.ylim(prev_ymin,yr[0])
	elif yr[1] is None:
		if ymax>prev_ymax:
			plt.ylim(yr[0],ymax)
		else:
			plt.ylim(yr[0],prev_ymax)
	else:					plt.ylim(yr)
	
	if Ny>1:
		print "Plotting columns of y"
	
	plt.plot(x,y,zorder=zorder)
			
	if xlabel: plt.xlabel(xlabel)
	if ylabel: plt.ylabel(ylabel)
	if title:  plt.title(title)

def sphericalplot(arr,**kwargs):
		
	arr=np.squeeze(arr)
	ash=arr.shape
	try: assert len(ash) == 2
	except AssertionError: 
		print "sphericalplot requires 2D arrays"
		print "Size of array provided is",str(ash)+", dimension is",len(ash)
		return
	
	if arr.dtype=='complex128' or arr.dtype=='complex64':
		print "Ignoring imaginary part"
		arr=np.real(arr)
	
	amin=arr.min()
	amax=arr.max()
	vmin=kwargs.get('vmin',amin)
	vmax=kwargs.get('vmax',amax)
	subplot_index=kwargs.get('subplot_index',111)
	if not subplot_index_is_valid(subplot_index): return
	colorbar=kwargs.get('colorbar',True)
	colorbar_scientific=kwargs.get('cbar_sci',False)
	xlabel=kwargs.get('xlabel','x')
	ylabel=kwargs.get('ylabel','y')
	zlabel=kwargs.get('zlabel','z')
	title=kwargs.get('title',None)
	cmap=kwargs.get('cmap',None)
	rstride=kwargs.get('rstride',int(ash[0]/50))
	cstride=kwargs.get('cstride',int(ash[1]/50))
	centerzero=kwargs.get('centerzero',False)
	zorder=kwargs.get('zorder',0)
	flipx=kwargs.get('flipx',False)
	flipy=kwargs.get('flipy',False)
	flipz=kwargs.get('flipz',False)
	azim=kwargs.get('azim',None)
	elev=kwargs.get('elev',None)
	dist=kwargs.get('dist',None)
		
	if int(subplot_index)==111: plt.clf()
	
	ax=plt.subplot(subplot_index, projection='3d')
	if centerzero:	vmin,vmax=center_range_around_zero(vmin,vmax,amin,amax)

	u = kwargs.get('phi',np.linspace(0, 2 * np.pi, ash[1]))
	v = kwargs.get('theta',np.linspace(0, np.pi, ash[0]))

	lonax,latax=np.meshgrid(u,v)
	
	#~ Norm setting from http://stackoverflow.com/questions/25023075/normalizing-colormap-used-by-facecolors-in-matplotlib
	norm = colors.Normalize(vmin=vmin,vmax=vmax)

	cmap=get_appropriate_colormap(vmin,vmax)

	scm=cm.ScalarMappable(cmap=cmap)
	scm.set_array(arr)
	scm.set_clim(vmin,vmax)	

	x = np.outer(np.sin(v),np.cos(u))
	y = np.outer(np.sin(v),np.sin(u))
	z = np.outer(np.cos(v),np.ones(np.size(u)))
	
	#~ Actual plot
	ax.plot_surface(x, y, z,  rstride=rstride, cstride=cstride,
	facecolors=cmap(norm(arr)),shade=False)
	
	if azim is not None: ax.azim=azim
	else:                
		mlcol=np.argmax(abs(arr))%ash[1]
		ax.azim=360/ash[1]*mlcol
	
	if elev is not None: ax.elev=elev
	else:                ax.elev=10
	
	if dist is not None: ax.dist=dist
	else:                ax.dist=10
	
	#~ Set scientific notation on colorbar for small or large values
	cbar_clip=max(abs(vmax),abs(vmin))
	if cbar_clip>1e4 or cbar_clip<1e-2: colorbar_scientific=True
	
	if colorbar: cb=generate_colorbar(mappable=scm,colorbar_scientific=colorbar_scientific)

	if flipx: ax.invert_xaxis()
	if flipy: ax.invert_yaxis()
	if flipz: ax.invert_zaxis()
	
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_zlabel(zlabel)
	if title:  plt.title(title)

def drawline(**kwargs):
	
	
	ls=kwargs.get('ls','--')
	col=kwargs.get('col','k')
	
	ax=plt.gca()
	xl=ax.get_xlim()
	yl=ax.get_ylim()
	
	x=kwargs.get('x',xl)
	y=kwargs.get('y',yl)
	
	try: 
		if len(y)==1: y=y[0]
	except: pass
	try: 
		if len(x)==1: x=x[0]
	except: pass
	if (not isinstance(x,list) and not isinstance(x,tuple)
		and not isinstance(y,list) and not isinstance(y,tuple)):
		print "Either x or y needs to be a range"
		return
	
	try: 
		int(y)
		y=[y,y]
	except TypeError: pass
	try: 
		int(x)
		x=[x,x]
	except TypeError: pass
		
	plt.plot(x,y,ls=ls,color=col)

def gridlist(nrows,ncols):
	return iter([str(nrows)+str(ncols)+str(i) for i in xrange(1,nrows*ncols+1)])

#~ Shifted colormap from http://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower ofset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to 
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highets point in the colormap's range.
          Defaults to 1.0 (no upper ofset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False), 
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap

def get_appropriate_colormap(vmin,vmax):
	
	positive_negative_cmap=cm.coolwarm
	all_positive_cmap=cm.OrRd
	all_negative_cmap=cm.Blues_r
	
	if vmax>0 and (vmin*vmax>=0 or -vmin/vmax<2e-2): 
		return all_positive_cmap
	elif vmin<0 and (vmin*vmax>=0 or -vmax/vmin<2e-2): 
		return all_negative_cmap
	elif vmin*vmax<0:
		midpoint = 1 - vmax/(vmax + abs(vmin))
		orig_cmap=positive_negative_cmap
		return shiftedColorMap(orig_cmap, midpoint=midpoint, name='shifted')
	else: 
		return positive_negative_cmap

def get_centered_grid_for_pcolormesh(x=None,y=None):
	#~ Shift axis grid from boundaries to centers of grid squares
	#~ Boundary trick from http://alex.seeholzer.de/2014/05/fun-with-matplotlib-pcolormesh-getting-data-to-display-in-the-right-position/
	
	if x is not None:
		dx=x[-1]-x[-2];
		xlast=x[-1]+dx;
		xgrid=np.insert(x,len(x),xlast)-dx/2
	else: xgrid=None
	
	if y is not None:
		dy=y[-1]-y[-2]
		ylast=y[-1]+dy
		ygrid=np.insert(y,len(y),ylast)-dy/2
	else: ygrid=None
		

	return xgrid,ygrid


def center_range_around_zero(vmin,vmax,amin,amax):
	if vmax*vmin<0:
		if vmin == amin and vmax != amax:
				vmin=-vmax
		elif vmin != amin and vmax == amax:
			vmax=-vmin
		elif vmin != amin and vmax != amax:
			if -vmin>vmax: 
				vmax=-vmin
			else: 
				vmin=-vmax
		else:
			vmax=max(amax,-amin)
			vmin=-vmax
	elif vmax*vmin==0:
		print "Zero lies on colormap border, can't center around zero"
	else:
		print "Zero lies outside colorbar range, can't center around zero"
	return vmin,vmax

def set_axis_limits(xgrid,ygrid,xr,yr):
	if xr is None:			plt.xlim(xgrid[0],xgrid[-1])
	elif xr[0] is None:		plt.xlim(xgrid[0],xr[1])
	elif xr[1] is None:		plt.xlim(xr[0],xgrid[-1])
	else:					plt.xlim(xr)
		
	if yr is None:			plt.ylim(ygrid[0],ygrid[-1])
	elif yr[0] is None:		plt.ylim(ygrid[0],yr[0])
	elif yr[1] is None:		plt.ylim(yr[0],ygrid[-1])
	else:					plt.ylim(yr)

def generate_colorbar(mappable=None,colorbar_scientific=False):
	
	if mappable is not None:
		if colorbar_scientific:
			cb=plt.colorbar(mappable=mappable,format="%1.0e")
		else:
			cb=plt.colorbar(mappable=mappable)
	else:
		if colorbar_scientific:
			cb=plt.colorbar(format="%1.0e")
		else:
			cb=plt.colorbar()
	tick_locator = ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()
	
	return cb
	
def subplot_index_is_valid(subplot_index):
		
	try:
		assert int(subplot_index)>=111 and int(subplot_index)<=999
	except AssertionError:
		print "Subplot index should lie between 111 and 999"
		return False
	except ValueError:
		print "Subplot index should be a number"
		return False
		
	
	nrows=int(int(subplot_index)//100)
	ncols=int((int(subplot_index)%100)//10)
	rowno=int((int(subplot_index)%10-1)//ncols)
	colno=int((int(subplot_index)%10-1)%ncols)
	

	try:
		assert rowno<nrows and colno<ncols
	except AssertionError:
		print "Invalid subplot index."
		if nrows>1 and ncols>1:
			print "Subplot has "+str(nrows)+" rows and "+str(ncols)+" columns"
		elif nrows==1 and ncols>1:
			print "Subplot has "+str(nrows)+" row and "+str(ncols)+" columns"
		elif nrows>1 and ncols==1:
			print "Subplot has "+str(nrows)+" rows and "+str(ncols)+" column"
		else:
			print "Subplot has 1 row and 1 column"
		if nrows==1 and ncols==1:
			print "Index should be 111"
		else:
			print ("Index should lie in the range "+str(nrows)+str(ncols)+ 
				"1 to "+str(nrows)+str(ncols)+str(nrows*ncols))
		return False
	
	return True
	



