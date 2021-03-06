from __future__ import division as _division
from matplotlib import ticker as _ticker,cm as _cm,colors as _colors,pyplot as plt
import numpy as _np

class PlotCollection():
    def __init__(self,axis,colorbar,plot):
        self.axis = axis
        self.colorbar = colorbar
        self.mappable = plot

def _center_range_around_zero(vmin,vmax,amin,amax,subplot_index=111):
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
        print "Zero lies on colormap border in subplot "+str(subplot_index)+", can't center around zero"
    else:
        print "Zero lies outside colorbar range, can't center around zero"
    return vmin,vmax

def colorplot(arr,**kwargs):
    ''' Creates a 2D density plot of the array using matplotlib's
    pcolormesh.
    Usage:
    colorplot(arr[,x=[1D array],y=[1D array],colorbar=True,
                xlim=[xlow,xhigh],ylim=[ylow,yhigh],ax=gca(),
                vmin=arr.min(),vmax=arr.max(),centerzero=True,
                rasterized=True,usetex=False,
                axes_properties=dict(xlabel="",...),
                colorbar_properties=dict(...),
                subplot_properties=dict(polar=False,...),
                locator_properties_xy=dict(...),
                title_properties=dict(...),**kwargs]
            )
    Chooses a suitable colormap based on your data, unless specified otherwise.
    It places tick labels at tick centers, instead of cell edges,
    which is pcolormesh default behaviour. Whenever applicable,
    pass the axis as ax=axis to avoid unwanted shifts arising due to default
    behaviour of pyplot's gca().
    '''

    arr=_np.squeeze(arr)
    ash=arr.shape
    try: assert len(ash) == 2
    except AssertionError:
        print "Colorplot requires 2D arrays"
        print "Size of array provided is",str(ash)+", dimension is",len(ash)
        return

    if arr.dtype=='complex128' or arr.dtype=='complex64':
        print "Ignoring imaginary part"
        arr=_np.real(arr)

    x=_np.array(kwargs.pop('x',_np.arange(ash[1])))

    x2=kwargs.pop('x2',None)
    if x2 is not None: x2=_np.array(x2)
    y=_np.array(kwargs.pop('y',_np.arange(ash[0])))
    y2=kwargs.pop('y2',None)
    if y2 is not None: y2=_np.array(y2)
    xr=kwargs.pop('xlim',kwargs.pop('xr',None))
    yr=kwargs.pop('ylim',kwargs.pop('yr',None))

    subplot_index=kwargs.pop('subplot_index',kwargs.pop('subplot',kwargs.pop('sp',111)))
    subplot_properties=kwargs.pop('subplot_properties',{})
    if not _subplot_index_is_valid(subplot_index): return

    colorbar=kwargs.pop('colorbar',True)
    colorbar_properties=kwargs.pop('colorbar_properties',{})
    centerzero=kwargs.pop('centerzero',False)

    cmap=kwargs.pop('cmap',None)

    kwargs['rasterized']=kwargs.get('rasterized',True)

    axes_properties=kwargs.pop('axes_properties',{})

    xrpad=axes_properties.get('xrpad',False)
    yrpad=axes_properties.get('yrpad',False)
    xtickpad=axes_properties.get('xtickpad',6.)
    ytickpad=axes_properties.get('ytickpad',6.)

    x_sci=axes_properties.get('x_sci',True)
    y_sci=axes_properties.get('y_sci',True)
    xy_sci=axes_properties.get('xy_sci',False)
    xscilimits=axes_properties.get('xscilimits',(-3,3))
    yscilimits=axes_properties.get('yscilimits',(-3,3))
    if xy_sci:	x_sci=y_sci=True

    # hide_xticks=axes_properties.get('hide_xticks',False)
    # hide_xticklabels=axes_properties.get('hide_xticklabels',False)
    # hide_yticks=axes_properties.get('hide_yticks',False)
    # hide_yticklabels=axes_properties.get('hide_yticklabels',False)
    # hide_x2ticks=axes_properties.get('hide_x2ticks',False)
    # hide_x2ticklabels=axes_properties.get('hide_x2ticklabels',False)
    # hide_y2ticks=axes_properties.get('hide_y2ticks',False)
    # hide_y2ticklabels=axes_properties.get('hide_y2ticklabels',False)

    usetex=kwargs.pop('usetex',False)

    amin=arr.min()
    amax=arr.max()

    vmin=kwargs.pop('vmin',amin)
    vmax=kwargs.pop('vmax',amax)

    if centerzero: 	vmin,vmax=_center_range_around_zero(vmin,vmax,amin,amax,subplot_index)
    #~ Take care of empty colorbar range
    if vmin==vmax:
        print "Constant colorbar range in subplot "+str(subplot_index)+","
        " colorbar will reflect an offset of 10^-10"
        vmax=vmin+1e-10
        colorbar_scientific=True

    # Colorbar extended ends
    if vmin<=amin and vmax>=amax:
        colorbar_properties["extend"]="neither"
    elif vmin>amin and vmax>=amax:
        colorbar_properties["extend"]="min"
    elif vmin<=amin and vmax<amax:
        colorbar_properties["extend"]="max"
    else:
        colorbar_properties["extend"]="both"

    ax=kwargs.pop('ax',None)
    if ax is None:
        if int(subplot_index) ==111:
			plt.clf()
        ax=plt.subplot(subplot_index,**subplot_properties)

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

    xgrid,ygrid=_get_centered_grid_for_pcolormesh(x,y)

    #~ Actual plot
    if cmap is None: cmap=_get_appropriate_colormap(vmin,vmax)

    mesh=ax.pcolormesh(xgrid,ygrid,arr,cmap=cmap,vmin=vmin,vmax=vmax,**kwargs)

    _set_axis_limits(xgrid,ygrid,xr,yr,xrpad=xrpad,yrpad=yrpad,ax=ax)

    #~ Set scientific notation on colorbar for small or large values
    cbar_clip=max(abs(vmax),abs(vmin))
    if cbar_clip>1e4 or cbar_clip<1e-2: colorbar_properties['scientific']=True

    colorbar_properties['ax']=ax
    colorbar_properties['mappable']=mesh

    if colorbar: cb=_generate_colorbar(**colorbar_properties)
    else: cb=None

    if usetex:
        ax.draw=_texfonts(ax.draw)
        if cb is not None:
            cb.ax.draw=_texfonts(cb.ax.draw)


    return PlotCollection(ax,cb,mesh)

#~ Custom div cmap from http://pyhogs.github.io/colormap-examples.html
def custom_div_cmap(numcolors=11, name='custom_div_cmap',
                    mincol=(0.019607843831181526, 0.18823529779911041, 0.3803921639919281, 1.0),
                    midcol='white', maxcol='darkred'):
    """ Create a custom diverging colormap with three colors

    Default is blue to white to red with 11 colors.  Colors can be specified
    in any way understandable by matplotlib.colors.ColorConverter.to_rgb()
    """

    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list(name=name,
                                             colors =[mincol, midcol, maxcol],
                                             N=numcolors)
    return cmap


def fitsplot(fitsfile,**kwargs):
    '''Loads a 2D fits file and plots it. Squeezes the array if necessary.
    It uses colorplot() to create the image, so it accepts the usual pcolormesh
    arguments. It requires pyfits to be installed.
    '''

    try:
        import pyfits
    except ImportError:
        print "No pyfits found"
        print "Install it using 'pip install pyfits'"
        quit()

    arr=_np.squeeze(pyfits.getdata(fitsfile))

    colorplot(arr,**kwargs)

def _generate_colorbar(**colorbar_properties):

    colorbar_scientific=colorbar_properties.pop('scientific',False)

    ticklabels=colorbar_properties.pop('ticklabels',None)
    ticks=colorbar_properties.pop('ticks',None)

    cbar_title=colorbar_properties.pop('title',None)
    title_properties=colorbar_properties.pop('title_properties',{})

    title_properties['horizontalalignment']=title_properties.get('horizontalalignment','center')
    title_properties['verticalalignment']=title_properties.get('verticalalignment','center')

    orientation=colorbar_properties.get('orientation','vertical')

    title_xcoord=title_properties.pop('x',1 if orientation=='vertical' else 0.5)
    title_ycoord=title_properties.pop('y',1.08 if orientation=='vertical' else -2.0)

    visible=colorbar_properties.pop('visible',True)

    textformat = colorbar_properties.pop('format',colorbar_properties.pop('fmt',"%1.0e"))
    cb=plt.colorbar(format=textformat if colorbar_scientific else None,**colorbar_properties)

    if ticks is None:
        cb.locator = _ticker.MaxNLocator(nbins=5)
        cb.update_ticks()
    else:
        cb.locator = _ticker.FixedLocator(ticks)
        cb.update_ticks()

    if ticklabels is not None:
        cb.set_ticklabels(ticklabels)

    if cbar_title is not None:
        cb.ax.text(title_xcoord,title_ycoord,cbar_title,**title_properties)

    cb.ax.set_visible(visible)
    return cb

def _getlocator(tick_locator):
    if tick_locator=='linear': return _ticker.LinearLocator
    elif tick_locator=='fixed': return _ticker.FixedLocator
    elif tick_locator=='log': return _ticker.LogLocator
    elif tick_locator=='null': return _ticker.NullLocator
    elif tick_locator=='multiple': return _ticker.MultipleLocator
    else: return _ticker.MaxNLocator

def _get_appropriate_colormap(vmin,vmax):

    all_positive_cmap=_cm.OrRd
    positive_negative_cmap=_cm.RdBu_r
    all_negative_cmap=_cm.Blues_r

    if vmax>0 and (vmin*vmax>=0 or -vmin/vmax<2e-2):
        return all_positive_cmap
    elif vmin<0 and (vmin*vmax>=0 or -vmax/vmin<2e-2):
        return all_negative_cmap
    elif vmin*vmax<0:
        midpoint = 1 - vmax/(vmax + abs(vmin))
        orig_cmap=positive_negative_cmap
        return _shiftedColorMap(orig_cmap, midpoint=midpoint, name='shifted')
    else:
        return positive_negative_cmap

def _get_centered_grid_for_pcolormesh(x=None,y=None):
    #~ Shift axis grid from boundaries to centers of grid squares
    #~ Boundary trick from http://alex.seeholzer.de/2014/05/fun-with-matplotlib-pcolormesh-getting-data-to-display-in-the-right-position/

    if x is not None:
        dx=x[-1]-x[-2];
        xlast=x[-1]+dx;
        xgrid=_np.insert(x,len(x),xlast)-dx/2
    else: xgrid=None

    if y is not None:
        dy=y[-1]-y[-2]
        ylast=y[-1]+dy
        ygrid=_np.insert(y,len(y),ylast)-dy/2
    else: ygrid=None


    return xgrid,ygrid

def gridlist(nrows,ncols):
    return iter([str(nrows)+str(ncols)+str(i) for i in xrange(1,nrows*ncols+1)])

def _is_natural_ordered(arr):
    assert len(arr.shape)==1,"Axis has to be 1D"

    tolerance=1e-10
    c=_np.diff(_np.fft.fftshift(arr))
    if (abs(c-c[0])<tolerance).all(): return True
    else: return False

def quiver2D(U,V,**kwargs):
    '''Creates a 2D vector plot using the specified x and y components U and V, sampling
    the data as specified in every. Uses's pyplot's quiver() and accepts standard keywords.
    Usage:
    quiver2D(U,V[,x=1D array,y=1D array,every=[1,1],
                ax=gca(),xlim=ax.get_xlim(),ylim=ax.get_ylim(),
                show_key=False,usetex=False,
                axes_properties=dict(xlabel=ax.get_xlabel(),...),
                key_properties=dict(scale=...,...),
                subplot_properties=dict(...),
                locator_properties_xy=dict(...),
                title_properties=dict(...),**kwargs]
            )
    It defaults to show_key=False, change this to true to generate a suitable key based on your data. You
    can specify the key length as scale=... in key_properties. Whenever possible, specify the current axis
    as ax=axis to avoid unwanted behavious arising due to pyplot's gca().
    '''

    gridshape =U.shape
    try: assert len(gridshape) == 2
    except AssertionError:
        print "quiver2D requires the two components U and V to be 2D fields."
        print "Size of array provided is",str(gridshape)+", dimension is",len(gridshape)
        return

    x =_np.squeeze(kwargs.pop('x',_np.linspace(0,10,gridshape[1])))
    x2=kwargs.pop('x2',None)
    if x2 is not None: x2=_np.squeeze(x2)
    y =_np.squeeze(kwargs.pop('y',_np.linspace(0,10,gridshape[0])))
    y2=kwargs.pop('y2',None)
    if y2 is not None: y2=_np.squeeze(y2)

    every=kwargs.pop('every',[1,1])

    xr=kwargs.pop('xlim',kwargs.pop('xr',None))
    yr=kwargs.pop('ylim',kwargs.pop('yr',None))

    subplot_index=kwargs.pop('subplot_index',kwargs.pop('subplot',kwargs.pop('sp',111)))
    subplot_properties=kwargs.pop('subplot_properties',{})
    if not _subplot_index_is_valid(subplot_index): return

    axes_properties =kwargs.pop('axes_properties',{})


    xrpad=axes_properties.get('xrpad',False)
    yrpad=axes_properties.get('yrpad',False)
    xtickpad=axes_properties.get('xtickpad',6.)
    ytickpad=axes_properties.get('ytickpad',6.)

    xtick_locator=axes_properties.get('xtick_locator','max')
    x2tick_locator=axes_properties.get('x2tick_locator',axes_properties.get('xtick_locator','max'))
    ytick_locator=axes_properties.get('ytick_locator','max')
    y2tick_locator=axes_properties.get('y2tick_locator',axes_properties.get('ytick_locator','max'))
    xytick_locator=axes_properties.get('xytick_locator',None)
    x2y2tick_locator=axes_properties.get('xytick_locator',axes_properties.get('xytick_locator',None))

    if xytick_locator is not None: xtick_locator=ytick_locator=xytick_locator
    if x2y2tick_locator is not None: x2tick_locator=y2tick_locator=x2y2tick_locator

    locator_properties_x=axes_properties.get('locator_properties_x',{})
    locator_properties_x2=axes_properties.get('locator_properties_x2',axes_properties.get('locator_properties_x',{}))
    locator_properties_y=axes_properties.get('locator_properties_y',{})
    locator_properties_y2=axes_properties.get('locator_properties_y2',axes_properties.get('locator_properties_y',{}))
    locator_properties_xy=axes_properties.get('locator_properties_xy',{})
    locator_properties_x2y2=axes_properties.get('locator_properties_x2y2',axes_properties.get('locator_properties_xy',{}))

    if xtick_locator=='max':
        if not ('nbins' in locator_properties_x): locator_properties_x['nbins']=5
    if ytick_locator=='max':
        if not ('nbins' in locator_properties_y): locator_properties_y['nbins']=5

    locator_properties_x.update(locator_properties_xy)
    locator_properties_y.update(locator_properties_xy)
    locator_properties_x2.update(locator_properties_x)
    locator_properties_y2.update(locator_properties_y)
    locator_properties_x2.update(locator_properties_x2y2)
    locator_properties_y2.update(locator_properties_x2y2)

    x_sci=axes_properties.get('x_sci',True)
    y_sci=axes_properties.get('y_sci',True)
    xy_sci=axes_properties.get('xy_sci',False)
    xscilimits=axes_properties.get('xscilimits',(-3,3))
    yscilimits=axes_properties.get('yscilimits',(-3,3))
    if xy_sci:				x_sci=y_sci=True

    hide_xticks =axes_properties.get('hide_xticks',False)
    hide_xticklabels=axes_properties.get('hide_xticklabels',False)
    hide_yticks =axes_properties.get('hide_yticks',False)
    hide_yticklabels=axes_properties.get('hide_yticklabels',False)
    hide_x2ticks=axes_properties.get('hide_x2ticks',False)
    hide_x2ticklabels =axes_properties.get('hide_x2ticklabels',False)
    hide_y2ticks=axes_properties.get('hide_y2ticks',False)
    hide_y2ticklabel=axes_properties.get('hide_y2ticklabels',False)

    usetex  =kwargs.pop('usetex',False)
    key =kwargs.pop('key',False)
    key_properties  =kwargs.pop('key_properties',{})
    keyscale=key_properties.get('scale',None)
    keyprefix =key_properties.get('prefix',"")
    keysuffix =key_properties.get('suffix',"")

    kwargs['rasterized']=kwargs.get('rasterized',True)

    ax=kwargs.pop('ax',None)
    if ax is None:
        if int(subplot_index) ==111: plt.clf();
        ax=plt.subplot(subplot_index,**subplot_properties)

    title=kwargs.pop('title',ax.get_title())
    title =axes_properties.get('title',title)
    title_properties=kwargs.pop('title_properties',{})

    xlabel=kwargs.pop('xl',kwargs.pop('xlabel',ax.get_xlabel()))
    ylabel=kwargs.pop('yl',kwargs.pop('ylabel',ax.get_ylabel()))
    xlabelproperties=kwargs.pop('xlabelproperties',{})
    ylabelproperties=kwargs.pop('ylabelproperties',{})
    xylabelproperties=kwargs.pop('xylabelproperties',{})

    xlabel =axes_properties.get('xlabel',axes_properties.get('xl',xlabel))
    ylabel =axes_properties.get('ylabel',axes_properties.get('xl',ylabel))

    xlabelproperties.update(xylabelproperties)
    ylabelproperties.update(xylabelproperties)


    #~ Actual plot
    every_x,every_y=every
    Q=plt.quiver(x[::every_x],y[::every_y],U[::every_y,::every_x],V[::every_y,::every_x],**kwargs)

    if key:
        if keyscale is None:
            mod=_np.sqrt(U**2+V**2)
            keyscale=mod.max()*0.66

        sci=key_properties.get('sci',True)
        fmt=key_properties.get('fmt',None)
        if (fmt is None) and sci:
            keytext="{:.1e}".format(keyscale)
        elif (fmt is None) and (not sci):
            keytext="{:2.1f}".format(keyscale)
        elif fmt is not None:
            keytext=fmt.format(keyscale)
        keytext=keyprefix+str(keytext)+keysuffix
        plt.quiverkey(Q,0.8,1.02,keyscale,keytext,labelpos='N',
        fontproperties={'size':key_properties.get('fontsize',14)})

    #~ Axis limits
    _set_axis_limits(x,y,xr,yr,xrpad=xrpad,yrpad=yrpad,ax=ax)

    #~ Axis ticks
    if hide_xticks: ax.set_xticks([])
    else:
		ax.get_xaxis().set_major_locator(_getlocator(xtick_locator)(**locator_properties_x))
		if x_sci:    ax.ticklabel_format(axis='x', style='sci', scilimits=xscilimits)
		for tick in ax.get_xaxis().get_major_ticks():
			tick.set_pad(xtickpad)
			tick.label1 = tick._get_text1()

    if hide_yticks: ax.set_yticks([])
    else:
		ax.get_yaxis().set_major_locator(_getlocator(ytick_locator)(**locator_properties_y))
		if y_sci:    ax.ticklabel_format(axis='y', style='sci', scilimits=yscilimits)
		for tick in ax.get_yaxis().get_major_ticks():
			tick.set_pad(ytickpad)
			tick.label1 = tick._get_text1()

    #~ Axis tick labels
    if hide_xticklabels: ax.set_xticklabels([])
    if hide_yticklabels: ax.set_yticklabels([])

    #~ Axis labels
    ax.set_xlabel(xlabel,**xlabelproperties)
    ax.set_ylabel(ylabel,**ylabelproperties)

    ax.set_title(title,**title_properties)

    if usetex: ax.draw=_texfonts(ax.draw)

    return PlotCollection(ax,None,Q)

def _set_axis_limits(xgrid,ygrid,xr,yr,xrpad=False,yrpad=False,dim=2,**kwargs):

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

#~ Shifted colormap from http://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
def _shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
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

    # regular index to compute the _colors
    reg_index = _np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = _np.hstack([
        _np.linspace(0.0, midpoint, 128, endpoint=False),
        _np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = _colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap

def spectrumplot(arr,**kwargs):

    arr=_np.squeeze(arr)
    ash=arr.shape

    x=kwargs.pop('x',None)
    y=kwargs.pop('y',None)

    if x is not None: x=_np.array(x)
    else: x=_np.fft.fftfreq(ash[1])*ash[1]

    if y is not None: y=_np.array(y)
    else: y=_np.fft.fftfreq(ash[0])*ash[0]

    if _is_natural_ordered(x) and _is_natural_ordered(y):
        return colorplot(_np.fft.fftshift(arr),x=_np.fft.fftshift(x),y=_np.fft.fftshift(y),**kwargs)
    elif _is_natural_ordered(x) and (not _is_natural_ordered(y)):
        return colorplot(_np.fft.fftshift(arr,axes=0),x=_np.fft.fftshift(x),y=y,**kwargs)
    elif (not _is_natural_ordered(x)) and _is_natural_ordered(y):
        return colorplot(_np.fft.fftshift(arr,axes=1),x=x,y=_np.fft.fftshift(y),**kwargs)
    else:
        return colorplot(arr,x=x,y=y,**kwargs)

def sphericalplot(arr,**kwargs):

    '''Plots the array arr[theta,phi] on a sphere, where theta represents
    the colatitude and phi represents the longitude.
    Usage:
    sphericalplot(arr[,theta=1D array,phi=1D array,
                    vmin=arr.min(),vmax=arr.max(),centerzero=False,
                    ax=gca(),colorbar=True,
                    axes_properties=dict(xlabel="",...),
                    colorbar_properties=dict(...),
                    subplot_properties=dict(polar=False,...),
                    locator_properties_xyz=dict(...),
                    title_properties=dict(...),**kwargs]
                )
    Chooses a suitable colormap based on your data, unless specified otherwise.
    Whenever possible, pass the axis as ax=axis to avoid unwanted shifts
    arising due to the default behaviour of pyplot's gca().
    '''

    from mpl_toolkits.mplot3d import Axes3D as _Axes3D

    arr=_np.squeeze(arr)
    ash=arr.shape
    try: assert len(ash) == 2
    except AssertionError:
        print "sphericalplot requires 2D arrays"
        print "Size of array provided is",str(ash)+", dimension is",len(ash)
        return

    warning=kwargs.pop('warn',True)

    if warning:
        print "Assuming latitude along axis 0 and longitude along axis 1."
        print "If the plot looks all right you can safely ignore this warning."
        print "Otherwise you might want to transpose your array."

    if arr.dtype=='complex128' or arr.dtype=='complex64':
        print "Ignoring imaginary part"
        arr=_np.real(arr)

    amin  =arr.min()
    amax  =arr.max()
    vmin  =kwargs.pop('vmin',amin)
    vmax  =kwargs.pop('vmax',amax)
    subplot_index =kwargs.pop('subplot_index',kwargs.pop('subplot',kwargs.pop('sp',111)))
    if not _subplot_index_is_valid(subplot_index): return

    colorbar=kwargs.pop('colorbar',True)
    colorbar_properties=kwargs.pop('colorbar_properties',{})
    centerzero=kwargs.pop('centerzero',False)

    kwargs['rstride'] =kwargs.get('rstride',int(ash[0]/50))
    kwargs['cstride'] =kwargs.get('cstride',int(ash[1]/50))
    kwargs['shade'] =kwargs.get('shade',False)

    cmap  =kwargs.pop('cmap',None)

    axes_properties =kwargs.pop('axes_properties',{})

    flipx =axes_properties.get('flipx',False)
    flipy =axes_properties.get('flipy',False)
    flipz =axes_properties.get('flipz',False)

    sphere=kwargs.pop('sphere_properties',{})

    azim  =sphere.get('azim',360/ash[1]*_np.argmax(abs(arr))%ash[1])
    elev  =sphere.get('elev',10)
    dist  =sphere.get('dist',10)

    ax=kwargs.get('ax',None)
    if ax is None:
        if int(subplot_index) ==111: plt.clf();
        ax=plt.subplot(subplot_index, projection='3d')

    xlabel=kwargs.pop('xl',kwargs.pop('xlabel',None))
    ylabel=kwargs.pop('yl',kwargs.pop('ylabel',None))
    zlabel=kwargs.pop('zl',kwargs.pop('zlabel',None))
    xlabel=axes_properties.get('xl',axes_properties.get('xlabel',xlabel))
    ylabel=axes_properties.get('yl',axes_properties.get('ylabel',ylabel))
    zlabel=axes_properties.get('zl',axes_properties.get('zlabel',zlabel))
    xlabelproperties=kwargs.pop('xlabelproperties',{})
    ylabelproperties=kwargs.pop('ylabelproperties',{})
    zlabelproperties=kwargs.pop('zlabelproperties',{})
    xyzlabelproperties=kwargs.pop('xyzlabelproperties',{})

    xlabelproperties.update(xyzlabelproperties)
    ylabelproperties.update(xyzlabelproperties)
    zlabelproperties.update(xyzlabelproperties)

    title =kwargs.pop('title',None)
    title_properties=kwargs.pop('title_properties',{})

    usetex=kwargs.pop('usetex',False)

    if centerzero:        vmin,vmax=_center_range_around_zero(vmin,vmax,amin,amax,subplot_index)

    phi=kwargs.get('phi',_np.linspace(0, 2 * _np.pi, ash[1]))
    theta =kwargs.get('theta',_np.linspace(0, _np.pi, ash[0]))

    lonax,latax=_np.meshgrid(phi,theta)

    #~ Norm setting from http://stackoverflow.com/questions/25023075/normalizing-colormap-used-by-facecolors-in-matplotlib
    norm = _colors.Normalize(vmin=vmin,vmax=vmax)

    cmap=_get_appropriate_colormap(vmin,vmax)

    scm=_cm.ScalarMappable(cmap=cmap)
    scm.set_array(arr)
    scm.set_clim(vmin,vmax)

    x = _np.outer(_np.sin(theta),_np.cos(phi))
    y = _np.outer(_np.sin(theta),_np.sin(phi))
    z = _np.outer(_np.cos(theta),_np.ones(_np.size(phi)))

    #~ Actual plot
    ax.plot_surface(x, y, z, facecolors=cmap(norm(arr)),**kwargs)

    ax.azim=azim
    ax.elev=elev
    ax.dist=dist

    #~ Set scientific notation on colorbar for small or large values
    cbar_clip=max(abs(vmax),abs(vmin))
    if cbar_clip>1e4 or cbar_clip<1e-2: colorbar_properties['scientific']=True

    colorbar_properties['mappable']=scm
    if colorbar: cb=_generate_colorbar(**colorbar_properties)
    else: cb=None

    if flipx: ax.invert_xaxis()
    if flipy: ax.invert_yaxis()
    if flipz: ax.invert_zaxis()

    if xlabel: ax.set_xlabel(xlabel,**xlabelproperties)
    if ylabel: ax.set_ylabel(ylabel,**ylabelproperties)
    if zlabel: ax.set_zlabel(zlabel,**zlabelproperties)

    if title: ax.set_title(title,**title_properties)

    if usetex:
        ax.draw=_texfonts(ax.draw)
        if cb is not None:
            cb.ax.draw=_texfonts(cb.ax.draw)

    return ax,cb

def _subplot_index_is_valid(subplot_index):

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

def _texfonts(f):
    params={
    'font.family':'serif',
    'font.serif':'Helvetica',
    'text.usetex':True
    }
    # wrap_rcparams from http://stackoverflow.com/questions/22569071/matplotlib-change-math-font-size-and-then-go-back-to-default
    def _wrap_rcparams(f, params):
        def _f(*args, **kw):
            backup = {key:plt.rcParams[key] for key in params}
            plt.rcParams.update(params)
            f(*args, **kw)
            plt.rcParams.update(backup)
        return _f
    return _wrap_rcparams(f,params)

def layout_subplots(numplots):
    '''Returns nrows,ncols'''
    if numplots<=3: nrows=1;ncols=numplots
    elif numplots==4: nrows=2;ncols=2
    elif numplots<=6: nrows=2;ncols=3
    elif numplots<=9: nrows=3;ncols=3
    else: nrows= int(numplots//4);ncols=4

    return nrows,ncols,gridlist(nrows,ncols)
