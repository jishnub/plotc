# plotc

A bunch of convenience functions to plot 2D and 3D figures correctly. List of features:

1. Treat axis grid as cell center rather than boundary (common pcolormesh issue)
2. Choose colormap according to data range
3. Set scientific notation according to data range
4. Center colormap around zero for asymmetric data, if necessary
5. Plot 3D functions on spheres (such as spherical harmonics) with auto colorbar
