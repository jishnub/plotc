from __future__ import division
from matplotlib import ticker,cm,colors,pyplot as plt,rcParams
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

plot=plt.plot
gcf,gca=plt.gcf,plt.gca
show=plt.show
figure=plt.figure
savefig=plt.savefig
clf,cla=plt.clf,plt.cla
tight_layout=plt.tight_layout
subplots_adjust=plt.subplots_adjust
subplot,subplots=plt.subplot,plt.subplots

def colorplot(arr,**kwargs):
    arr                    	=np.squeeze(arr)
    ash                    	=arr.shape
    try: assert len(ash) == 2
    except AssertionError: 
        print "Colorplot requires 2D arrays"
        print "Size of array provided is",str(ash)+", dimension is",len(ash)
        return
    
    if arr.dtype=='complex128' or arr.dtype=='complex64':
        print "Ignoring imaginary part"
        arr=np.real(arr)
    
    x						=kwargs.get('x',None)
    x2						=kwargs.get('x2',None)
    y						=kwargs.get('y',None)
    y2						=kwargs.get('y2',None)
    xr						=kwargs.get('xlim',kwargs.get('xr',None))
    yr						=kwargs.get('ylim',kwargs.get('yr',None))
    
    subplot_index			=kwargs.get('subplot_index',kwargs.get('subplot',kwargs.get('sp',111)))
    subplot_properties		=kwargs.get('subplot_properties',{})
    if not subplot_index_is_valid(subplot_index): return
    
    colorbar           	 	=kwargs.get('colorbar',True)
    colorbar_properties		=kwargs.get('colorbar_properties',{})
    centerzero				=kwargs.get('centerzero',False) 
    
    xlabel					=kwargs.get('xl',kwargs.get('xlabel',""))
    ylabel					=kwargs.get('yl',kwargs.get('ylabel',""))
    xlabelproperties		=kwargs.get('xlabelproperties',{})
    ylabelproperties		=kwargs.get('ylabelproperties',{})
    xylabelproperties		=kwargs.get('xylabelproperties',{})
    
    xlabelproperties.update(xylabelproperties)
    ylabelproperties.update(xylabelproperties)
    
    
    title=kwargs.get('title',"")
    title_properties=kwargs.get('title_properties',{})
    
    cmap					=kwargs.get('cmap',None)
    
    pcolormesh_properties	=kwargs.get('pcolormesh_properties',{})
    pcolormesh_properties['rasterized']=pcolormesh_properties.get('rasterized',True)
    
    axes_properties			=kwargs.get('axes_properties',{})
    
    flipy					=axes_properties.get('flipy',False)
    flipx					=axes_properties.get('flipx',False)
    xrpad					=axes_properties.get('xrpad',False)
    yrpad					=axes_properties.get('yrpad',False)
    xtickpad				=axes_properties.get('xtickpad',6.)
    ytickpad				=axes_properties.get('ytickpad',6.)
    
    x_sci					=axes_properties.get('x_sci',True)
    y_sci					=axes_properties.get('y_sci',True)
    xy_sci					=axes_properties.get('xy_sci',False)
    xscilimits				=axes_properties.get('xscilimits',(-3,3))
    yscilimits				=axes_properties.get('yscilimits',(-3,3))
    if xy_sci:				x_sci=y_sci=True
    
    hide_xticks				=axes_properties.get('hide_xticks',False)
    hide_xticklabels   		=axes_properties.get('hide_xticklabels',False)
    hide_yticks				=axes_properties.get('hide_yticks',False)
    hide_yticklabels		=axes_properties.get('hide_yticklabels',False)
    hide_x2ticks			=axes_properties.get('hide_x2ticks',False)
    hide_x2ticklabels		=axes_properties.get('hide_x2ticklabels',False)
    hide_y2ticks			=axes_properties.get('hide_y2ticks',False)
    hide_y2ticklabels		=axes_properties.get('hide_y2ticklabels',False)
    
    xtick_locator			=axes_properties.get('xtick_locator','max')
    ytick_locator			=axes_properties.get('ytick_locator','max')
    locator_properties_x	=kwargs.get('locator_properties_x',{})
    locator_properties_x2	=kwargs.get('locator_properties_x2',{})
    locator_properties_y	=kwargs.get('locator_properties_y',{})
    locator_properties_y2	=kwargs.get('locator_properties_y2',{})
    locator_properties_xy	=kwargs.get('locator_properties_xy',{})
    locator_properties_x2y2	=kwargs.get('locator_properties_x2y2',{})
    
    locator_properties_x.update(locator_properties_xy)
    locator_properties_y.update(locator_properties_xy)
    locator_properties_x2.update(locator_properties_x2y2)
    locator_properties_y2.update(locator_properties_x2y2)
    
    
    def getlocator(tick_locator):
			if tick_locator=='linear': return ticker.LinearLocator
			elif tick_locator=='fixed': return ticker.LinearLocator
			else: return ticker.MaxNLocator
    
    polar					=subplot_properties.get('polar',False)
    if polar: 
        print "Note: Assuming x is theta and y is r"
        print "If plot looks correct you may safely ignore this"
        print "If plot looks weird you might want to specify x and y"
    
    usetex					=kwargs.get('usetex',False)
    if usetex:				texfonts()
    
    amin=arr.min()
    amax=arr.max()
    
    vmin					=kwargs.get('vmin',amin)
    vmax					=kwargs.get('vmax',amax)
    
    if centerzero:        	vmin,vmax=center_range_around_zero(vmin,vmax,amin,amax)

    ax						=kwargs.get('ax',None)
    if ax is None:
        if int(subplot_index) ==111: 
			plt.clf()
        ax=plt.subplot(subplot_index,**subplot_properties)
    

    
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
    if len(x.shape) == 2:    x=x[0]
    if len(y.shape) == 2:    y=y[:,0]
    
    #~ Check if sizes match
    Nx=len(x);Ny=len(y)    
    try:    assert Nx==ash[1] and Ny==ash[0]
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
        
    xgrid,ygrid=get_centered_grid_for_pcolormesh(x,y)

    #~ Take care of empty colorbar range
    if vmin==vmax:         
        print "Constant colorbar range, colorbar will reflect an offset of 10^-10"
        vmax=vmin+1e-10
        colorbar_scientific=True
    
    #~ Actual plot
    if cmap is None: cmap=get_appropriate_colormap(vmin,vmax)

    mesh=ax.pcolormesh(xgrid,ygrid,arr,cmap=cmap,vmin=vmin,vmax=vmax,**pcolormesh_properties)
    
    
    set_axis_limits(xgrid,ygrid,xr,yr,xrpad=xrpad,yrpad=yrpad,ax=ax)
    
    #~ Set scientific notation on colorbar for small or large values
    cbar_clip=max(abs(vmax),abs(vmin))
    if cbar_clip>1e4 or cbar_clip<1e-2: colorbar_properties['scientific']=True
    
    colorbar_properties['ax']=ax
    colorbar_properties['mappable']=mesh
    
    if colorbar: cbax=generate_colorbar(**colorbar_properties)  
    else: cbax=None  
    
    if x2 is not None: 
        ax2=plt.twiny(ax=ax)
        dx=x2[1]-x2[0]
        x2,_=get_centered_grid_for_pcolormesh(x=x2,y=None)
        
        ax2.set_xlim(x2[0],x2[-1])
        
        ax2.get_xaxis().set_major_locator(ticker.MaxNLocator(nbins=x2bins,integer=True if int_ticks_x2 else False))
        if hide_x2ticks: ax2.set_xticks([])
        if hide_x2ticklabels: ax2.set_xticklabels([])
        
    if y2 is not None: 
        ax2=plt.twinx(ax=ax)
        _,y2=get_centered_grid_for_pcolormesh(x=None,y=y2)
        
        ax2.set_ylim(y2[0],y2[-1])
        
        if int_ticks_y2: ax2.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=y2bins,integer=True))
        if hide_y2ticks: ax2.set_yticks([])
        if hide_y2ticklabels: ax2.set_yticklabels([])
    
    if flipx: ax.invert_xaxis()
    if flipy: ax.invert_yaxis()

    
    if hide_xticks: ax.set_xticks([])
    else: 
		ax.get_xaxis().set_major_locator(getlocator(xtick_locator)(**locator_properties_x))
		if x_sci:    ax.ticklabel_format(axis='x', style='sci', scilimits=xscilimits)
		for tick in ax.get_xaxis().get_major_ticks():
			tick.set_pad(xtickpad)
			tick.label1 = tick._get_text1()

    if hide_yticks: ax.set_yticks([])
    else: 
		ax.get_yaxis().set_major_locator(getlocator(ytick_locator)(**locator_properties_y))
		if y_sci:    ax.ticklabel_format(axis='y', style='sci', scilimits=yscilimits)
		for tick in ax.get_yaxis().get_major_ticks():
			tick.set_pad(ytickpad)
			tick.label1 = tick._get_text1()
    
    if hide_xticklabels: ax.set_xticklabels([])
    if hide_yticklabels: ax.set_yticklabels([])
    
    ax.set_xlabel(xlabel,**xlabelproperties)
    ax.set_ylabel(ylabel,**ylabelproperties)
    ax.set_title(title,**title_properties)
    
    return ax,cbax
    
def quiver2D(U,V,**kwargs):
    gridshape            =U.shape
    x                    =kwargs.get('x',np.linspace(0,10,gridshape[1]))
    x2                    =kwargs.get('x2',None)    
    y                    =kwargs.get('y',np.linspace(0,10,gridshape[0]))
    y2                    =kwargs.get('y2',None)
    
    quiver_properties    =kwargs.get('quiver_properties',{})
    
    every                =kwargs.get('every',[1,1])
    
    xr                    =kwargs.get('xlim',kwargs.get('xr',None))
    yr                    =kwargs.get('ylim',kwargs.get('yr',None))
    
    subplot_index        =kwargs.get('subplot_index',kwargs.get('subplot',kwargs.get('sp',111)))
    subplot_properties    =kwargs.get('subplot_properties',{})
    if not subplot_index_is_valid(subplot_index): return

    xlabel                =kwargs.get('xl',kwargs.get('xlabel',""))
    ylabel                =kwargs.get('yl',kwargs.get('ylabel',""))
    xlabelproperties    =kwargs.get('xlabelproperties',{})
    ylabelproperties    =kwargs.get('ylabelproperties',{})
    xylabelproperties        =kwargs.get('xylabelproperties',{})
    
    xlabelproperties.update(xylabelproperties)
    ylabelproperties.update(xylabelproperties)
    
    title                =kwargs.get('title',"")
    title_properties    =kwargs.get('title_properties',{})
    
    axes_properties        =kwargs.get('axes_properties',{})
    
    xrpad                =axes_properties.get('xrpad',False)
    yrpad                =axes_properties.get('yrpad',False)
    xtickpad            =axes_properties.get('xtickpad',6.)
    ytickpad            =axes_properties.get('ytickpad',6.)    
    int_ticks_x            =axes_properties.get('int_ticks_x',False)
    int_ticks_y            =axes_properties.get('int_ticks_y',False)
    int_ticks            =axes_properties.get('int_ticks',False)
    int_ticks_x2        =axes_properties.get('int_ticks_x2',True)
    int_ticks_y2        =axes_properties.get('int_ticks_y2',True)
    int_ticks2            =kwargs.get('int_ticks2',True)
    if int_ticks2:         int_ticks_x2=int_ticks_y2=True
    if int_ticks:         int_ticks_x=int_ticks_y=True
    
    x1bins                =axes_properties.get('xbins',10)
    y1bins                =axes_properties.get('ybins',10)
    x2bins                =axes_properties.get('x2bins',5)
    y2bins                =axes_properties.get('y2bins',5)
    
    x_sci                =axes_properties.get('x_sci',True)
    y_sci                =axes_properties.get('y_sci',True)
    xy_sci                =axes_properties.get('xy_sci',False)
    if xy_sci:             x_sci=y_sci=True
    
    hide_xticks            =axes_properties.get('hide_xticks',False)
    hide_xticklabels    =axes_properties.get('hide_xticklabels',False)
    hide_yticks            =axes_properties.get('hide_yticks',False)
    hide_yticklabels    =axes_properties.get('hide_yticklabels',False)
    hide_x2ticks        =axes_properties.get('hide_x2ticks',False)
    hide_x2ticklabels    =axes_properties.get('hide_x2ticklabels',False)
    hide_y2ticks        =axes_properties.get('hide_y2ticks',False)
    hide_y2ticklabel    =axes_properties.get('hide_y2ticklabels',False)
    
    usetex                =kwargs.get('usetex',False)
    key                    =kwargs.get('show_key',False)
    key_properties        =kwargs.get('key_properties',{})
    keyscale            =key_properties.get('keyscale',None)
    keyprefix            =key_properties.get('keyprefix',"")
    keysuffix            =key_properties.get('keysuffix',"")
    
    if usetex: texfonts()
    
    ax=kwargs.get('ax',None)
    if ax is None:
        if int(subplot_index) ==111: plt.clf(); 
        ax=plt.subplot(subplot_index,**subplot_properties)
    
    #~ Actual plot
    every_x,every_y=every
    Q=plt.quiver(x[::every_x],y[::every_y],U[::every_y,::every_x],V[::every_y,::every_x],**quiver_properties)
    
    if key:
        if keyscale is None:
            mod=np.sqrt(U**2+V**2)
            keyscale=mod.max()*0.66    
            keyscale=int(np.floor(keyscale/100)*100)
        plt.quiverkey(Q,0.8,1.02,keyscale,keyprefix+str(keyscale)+keysuffix,labelpos='N',
        fontproperties={'size':14})
    
    set_axis_limits(x,y,xr,yr,xrpad=xrpad,yrpad=yrpad,ax=ax)
    
    ax.get_xaxis().set_major_locator(ticker.MaxNLocator(nbins=x1bins,integer=True if int_ticks_x else False))
    ax.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=y1bins,integer=True if int_ticks_y else False))

    if x_sci:
        ax.ticklabel_format(axis='x', style='sci', scilimits=(-3,3))
    if y_sci:
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-3,3))
    
    if hide_xticklabels: ax.set_xticklabels([])
    if hide_yticklabels: ax.set_yticklabels([])
    
    ax.set_xlabel(xlabel,**xlabelproperties)
    ax.set_ylabel(ylabel,**ylabelproperties)
    ax.set_title(title,**title_properties)
    
    return ax
    
quiver2d=quiver2D
        
def plot1D(arr,**kwargs):
    
    try: arr=np.array(arr)
    except:
        print "Require array like object to plot"
        return
    
    plot_properties=kwargs.get('plot_properties',{})
    
    x=kwargs.get('x',None)
    xr=kwargs.get('xlim',kwargs.get('xr',None))
    yr=kwargs.get('ylim',kwargs.get('yr',None))

    subplot_index			=kwargs.get('subplot_index',kwargs.get('subplot',kwargs.get('sp',None)))
    subplot_properties		=kwargs.get('subplot_properties',{})
    
    xlabel					=kwargs.get('xl',kwargs.get('xlabel',""))
    ylabel                  =kwargs.get('yl',kwargs.get('ylabel',""))
    xlabelproperties        =kwargs.get('xlabelproperties',{})
    ylabelproperties        =kwargs.get('ylabelproperties',{})
    xylabelproperties       =kwargs.get('xylabelproperties',{})
    
    xlabelproperties.update(xylabelproperties)
    ylabelproperties.update(xylabelproperties)
    
    title					=kwargs.get('title',"")
    title_properties		=kwargs.get('title_properties',{})
    
    usetex					=kwargs.get('usetex',False)
    if usetex:				texfonts()
    
    ax						=kwargs.get('ax',None)
    axes_properties			=kwargs.get('axes_properties',{})
    
    xlabel 					=axes_properties.get('xlabel',axes_properties.get('xl',xlabel))
    ylabel 					=axes_properties.get('ylabel',axes_properties.get('xl',ylabel))
    
    x_sci					=axes_properties.get('x_sci',True)
    y_sci					=axes_properties.get('y_sci',True)
    xy_sci					=axes_properties.get('xy_sci',False)
    xscilimits				=axes_properties.get('xscilimits',(-3,3))
    yscilimits				=axes_properties.get('yscilimits',(-3,3))
    if xy_sci:				x_sci=y_sci=True
    
    hide_xticks				=axes_properties.get('hide_xticks',False)
    hide_xticklabels    	=axes_properties.get('hide_xticklabels',False)
    hide_yticks				=axes_properties.get('hide_yticks',False)
    hide_yticklabels		=axes_properties.get('hide_yticklabels',False)
    hide_x2ticks			=axes_properties.get('hide_x2ticks',False)
    hide_x2ticklabels		=axes_properties.get('hide_x2ticklabels',False)
    hide_y2ticks			=axes_properties.get('hide_y2ticks',False)
    hide_y2ticklabels		=axes_properties.get('hide_y2ticklabels',False)
    
    exponent_xy				=axes_properties.get('exponent_xy',None)
    
    xtick_locator			=axes_properties.get('xtick_locator','max')
    ytick_locator			=axes_properties.get('ytick_locator','max')
    locator_properties_x	=kwargs.get('locator_properties_x',{})
    locator_properties_x2	=kwargs.get('locator_properties_x2',{})
    locator_properties_y	=kwargs.get('locator_properties_y',{})
    locator_properties_y2	=kwargs.get('locator_properties_y2',{})
    locator_properties_xy	=kwargs.get('locator_properties_xy',{})
    locator_properties_x2y2	=kwargs.get('locator_properties_x2y2',{})
    
    locator_properties_x.update(locator_properties_xy)
    locator_properties_y.update(locator_properties_xy)
    locator_properties_x2.update(locator_properties_x2y2)
    locator_properties_y2.update(locator_properties_x2y2)
    
    def getlocator(tick_locator):
			if tick_locator=='linear': return ticker.LinearLocator
			elif tick_locator=='fixed': return ticker.LinearLocator
			else: return ticker.MaxNLocator
    
    int_ticks_x				=locator_properties_x.get('int_ticks_x',False)
    int_ticks_y				=locator_properties_y.get('int_ticks_y',False)
    int_ticks				=locator_properties_xy.get('int_ticks',False)
    int_ticks_x2			=locator_properties_x2.get('int_ticks_x2',True)
    int_ticks_y2			=locator_properties_y2.get('int_ticks_y2',True)
    int_ticks2				=locator_properties_x2y2.get('int_ticks2',True)
    
    if int_ticks:			int_ticks_x=int_ticks_y=True
    if int_ticks2:			int_ticks_x2=int_ticks_y2=True
    
    x1bins					=locator_properties_x.get('xbins',10)
    y1bins					=locator_properties_y.get('ybins',10)
    x2bins					=locator_properties_x2.get('x2bins',5)
    y2bins					=locator_properties_x2y2.get('y2bins',5)
    
    ash=arr.shape
    try:
        assert ash
        assert ash[0]
    except AssertionError:
        print "Zero length sequence can't be plotted"
        return
    Ny=1
    if len(ash)==1:    Npts=ash[0]
    else: 
        Ny=ash[0]
        Npts=ash[1]
    
    ylim_original=None
    xlim_original=None
    if ax is None and subplot_index is None:
    	ax=plt.gca()
    elif ax is None and subplot_index is not None:
        if not subplot_index_is_valid(subplot_index): return
        ax=plt.subplot(subplot_index,**subplot_properties)        
    if ax.has_data():		
        ylim_original=ax.get_ylim()
        xlim_original=ax.get_xlim()
		
        
    if x is None:    x=np.arange(Npts)    
    
    if Ny>1: print "Plotting columns of y"
    
    p=ax.plot(x,arr,**plot_properties)
    
    if ylim_original==None:	ylim_original=ax.get_ylim()
    if xlim_original==None:	xlim_original=ax.get_xlim()
    
    if hide_xticks: ax.set_xticks([])
    else: 
		ax.get_xaxis().set_major_locator(getlocator(xtick_locator)(**locator_properties_x))
		if x_sci:    ax.ticklabel_format(axis='x', style='sci', scilimits=xscilimits)

    if hide_yticks: ax.set_yticks([])
    else: 
		ax.get_yaxis().set_major_locator(getlocator(ytick_locator)(**locator_properties_y))
		if y_sci:    ax.ticklabel_format(axis='y', style='sci', scilimits=yscilimits)
		
    set_axis_limits(x,arr,xr,yr,dim=1,ax=ax,xlim_original=xlim_original,ylim_original=ylim_original)
		
    if hide_xticklabels: ax.set_xticklabels([])
    if hide_yticklabels: ax.set_yticklabels([])
            
    ax.set_xlabel(xlabel,**xlabelproperties)
    ax.set_ylabel(ylabel,**ylabelproperties)
    ax.set_title(title,**title_properties)
    
    return ax

def sphericalplot(arr,**kwargs):
        
    arr=np.squeeze(arr)
    ash=arr.shape
    try: assert len(ash) == 2
    except AssertionError: 
        print "sphericalplot requires 2D arrays"
        print "Size of array provided is",str(ash)+", dimension is",len(ash)
        return
    
    print "Assuming latitude along axis 0 and longitude along axis 1."
    print "If the plot looks all right you can safely ignore this warning."
    print "Otherwise you might want to transpose your array."
    
    if arr.dtype=='complex128' or arr.dtype=='complex64':
        print "Ignoring imaginary part"
        arr=np.real(arr)
    
    amin                =arr.min()
    amax                =arr.max()
    vmin                =kwargs.get('vmin',amin)
    vmax                =kwargs.get('vmax',amax)
    subplot_index        =kwargs.get('subplot_index',kwargs.get('subplot',kwargs.get('sp',111)))
    if not subplot_index_is_valid(subplot_index): return
    
    colorbar            =kwargs.get('colorbar',True)
    colorbar_properties    =kwargs.get('colorbar_properties',{})
    centerzero            =colorbar_properties.pop('centerzero',False)
    
    xlabel                =kwargs.get('xl',kwargs.get('xlabel',""))
    ylabel                =kwargs.get('yl',kwargs.get('ylabel',""))
    zlabel                =kwargs.get('zlabel',kwargs.get('zlabel',""))
    xlabelproperties    =kwargs.get('xlabelproperties',{})
    ylabelproperties    =kwargs.get('ylabelproperties',{})
    zlabelproperties    =kwargs.get('zlabelproperties',{})
    xylabelproperties        =kwargs.get('xylabelproperties',{})
    
    title                =kwargs.get('title',None)
    title_properties    =kwargs.get('title_properties',{})
    
    cmap                =kwargs.get('cmap',None)
    
    axes_properties        =kwargs.get('axes_properties',{})
    
    flipx                =axes_properties.get('flipx',False)
    flipy                =axes_properties.get('flipy',False)
    flipz                =axes_properties.get('flipz',False)
    
    sphere                =kwargs.get('sphere_properties',{})
    
    sphere['rstride']    =sphere.get('rstride',int(ash[0]/50))
    sphere['cstride']    =sphere.get('cstride',int(ash[1]/50))
    sphere['shade']        =sphere.get('shade',False)
    azim                =sphere.get('azim',360/ash[1]*np.argmax(abs(arr))%ash[1])
    elev                =sphere.get('elev',10)
    dist                =sphere.get('dist',10)
        
    ax=kwargs.get('ax',None)
    if ax is None:
        if int(subplot_index) ==111: plt.clf(); 
        ax=plt.subplot(subplot_index, projection='3d')
    
    
    if centerzero:    vmin,vmax=center_range_around_zero(vmin,vmax,amin,amax)

    phi                    =kwargs.get('phi',np.linspace(0, 2 * np.pi, ash[1]))
    theta                =kwargs.get('theta',np.linspace(0, np.pi, ash[0]))

    lonax,latax=np.meshgrid(phi,theta)
    
    #~ Norm setting from http://stackoverflow.com/questions/25023075/normalizing-colormap-used-by-facecolors-in-matplotlib
    norm = colors.Normalize(vmin=vmin,vmax=vmax)

    cmap=get_appropriate_colormap(vmin,vmax)

    scm=cm.ScalarMappable(cmap=cmap)
    scm.set_array(arr)
    scm.set_clim(vmin,vmax)    

    x = np.outer(np.sin(theta),np.cos(phi))
    y = np.outer(np.sin(theta),np.sin(phi))
    z = np.outer(np.cos(theta),np.ones(np.size(phi)))
    
    #~ Actual plot
    ax.plot_surface(x, y, z, facecolors=cmap(norm(arr)),**sphere)
    
    ax.azim=azim
    ax.elev=elev
    ax.dist=dist
    
    #~ Set scientific notation on colorbar for small or large values
    cbar_clip=max(abs(vmax),abs(vmin))
    if cbar_clip>1e4 or cbar_clip<1e-2: colorbar_properties['scientific']=True
    colorbar_properties['mappable']=scm    
    if colorbar: cbax=generate_colorbar(**colorbar_properties)
    else: cbax=None

    if flipx: ax.invert_xaxis()
    if flipy: ax.invert_yaxis()
    if flipz: ax.invert_zaxis()
    
    ax.set_xlabel(xlabel,**dict(chain.from_iterable([xlabelproperties,xylabelproperties])))
    ax.set_ylabel(ylabel,**dict(chain.from_iterable([ylabelproperties,xylabelproperties])))
    ax.set_zlabel(zlabel,**dict(chain.from_iterable([zlabelproperties,xylabelproperties])))
    ax.set_title(title,**title_properties)
    
    return ax,cbax

def drawvlines(x,**kwargs):
    
    ax=kwargs.pop('ax',plt.gca())
    yl=ax.get_ylim()
    
    ymin=kwargs.pop('ymin',yl[0])
    ymax=kwargs.pop('ymax',yl[1])
    
    kwargs['linestyles']=kwargs.get('linestyles',kwargs.pop('ls','solid'))
    kwargs['colors']=kwargs.get('colors',kwargs.pop('col','k'))
    restore_ylim=kwargs.pop('restore_ylim',False)
    
    lines=ax.vlines(x,ymin,ymax,**kwargs)
    
    if restore_ylim: ax.set_ylim(yl)
    
    return ax,lines
    
def drawhlines(y,**kwargs):
    
    ax=kwargs.pop('ax',plt.gca())
    xl=ax.get_xlim()
    
    xmin=kwargs.pop('xmin',xl[0])
    xmax=kwargs.pop('xmax',xl[1])
    
    kwargs['linestyles']=kwargs.get('linestyles',kwargs.pop('ls','solid'))
    kwargs['colors']=kwargs.get('colors',kwargs.pop('col','k'))
    
    return ax,ax.hlines(y,xmin,xmax,**kwargs)

def drawline(**kwargs):
    
    ax=kwargs.pop('ax',plt.gca())
    xl=ax.get_xlim()
    yl=ax.get_ylim()
    
    x=kwargs.pop('x',xl)
    y=kwargs.pop('y',yl)
    
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
        
    return plt.plot(x,y,**kwargs)

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
    
    all_positive_cmap=cm.OrRd    
    positive_negative_cmap=cm.RdBu_r    
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

def set_axis_limits(xgrid,ygrid,xr,yr,xrpad=False,yrpad=False,dim=2,**kwargs):
    
    dx=xgrid[1]-xgrid[0]
    dy=ygrid[1]-ygrid[0]
    
    ax=kwargs.get('ax')
    xlim_original=kwargs.get('xlim_original',ax.get_xlim())
    ylim_original=kwargs.get('ylim_original',ax.get_ylim())
    
   
    if dim==2:
        if xr is None:    xlim=ax.set_xlim(xgrid[0],xgrid[-1])
        elif xr[0] is None:        
            if xrpad:    xlim=ax.set_xlim(xgrid[0],xr[1]+dx/2)
            else:        xlim=ax.set_xlim(xgrid[0],xr[1])
        elif xr[1] is None:        
		    if xrpad:    xlim=ax.set_xlim(xr[0]-dx/2,xgrid[-1])
		    else:        xlim=ax.set_xlim(xr[0],xgrid[-1])
        else:
            if xrpad:    xlim=ax.set_xlim(xr[0]-dx/2,xr[1]+dx/2)
            else:       xlim=ax.set_xlim(xr[0],xr[1])
    
        if yr is None:            
            ylim=ax.set_ylim(ygrid[0],ygrid[-1])
        elif yr[0] is None:        
            if yrpad:     ylim=ax.set_ylim(ygrid[0],yr[1]+dy/2)
            else:        ylim=ax.set_ylim(ygrid[0],yr[1])
        elif yr[1] is None:        
            if yrpad:     ylim=ax.set_ylim(yr[0]-dy/2,ygrid[-1])
            else:        ylim=ax.set_ylim(yr[0],ygrid[-1])
        else:            
            if yrpad:    ylim=ax.set_ylim(yr[0]-dy/2,yr[1]+dy/2)
            else:        ylim=ax.set_ylim(yr[0],yr[1])
    elif dim==1:
        
        if xr is None:    
            xleft=min(xgrid.min(),min(xlim_original))
            xright=max(xgrid.max(),max(xlim_original))
            xlim=ax.set_xlim(xleft,xright)
        elif xr[0] is None:
            xleft=min(xgrid.min(),min(xlim_original))
            xright=xr[1]
            xlim=ax.set_xlim(xleft,xright)
        elif xr[1] is None:
            xleft=xr[0]
            xright=max(xgrid.max(),max(xlim_original))        
            xlim=ax.set_xlim(xleft,xright)
        else:
            xleft,xright=xr
            xlim=ax.set_xlim(xleft,xright)
        
        
        ylim=None
        
    return xlim,ylim

def generate_colorbar(**colorbar_properties):
    
    colorbar_scientific=colorbar_properties.pop('scientific',False)
    cbar_title=colorbar_properties.pop('title',None)
    ticklabels=colorbar_properties.pop('ticklabels',None)
    
    cb=plt.colorbar(format="%1.0e" if colorbar_scientific else None,**colorbar_properties)
    orientation=cb.orientation
    
    if ticklabels is not None: 
        cb.set_ticklabels(ticklabels)
    
    if not 'ticks' in colorbar_properties:
        cb.locator = ticker.MaxNLocator(nbins=5)
        cb.update_ticks()
    
    if cbar_title is not None:
        cax=cb.ax
        cax.text(-0.5,1.02,cbar_title,rotation=0,fontsize=15)
    
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

def texfonts():
    rcParams['font.family'] = 'serif'
    rcParams['font.serif'] = ['Helvetica']
    rcParams['text.usetex'] = True

def figuresize(width=6.5,height=5):
    plt.gcf().set_size_inches(width,height)
    
figsize=figuresize
