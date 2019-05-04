# Blender Curve to SVG

> A simple Blender add-on for exporting 2D curves to SVG files

Who doesn’t like to edit curves in Blender? :stuck_out_tongue:

I mean,
precise transform operators
that allow to input values or expressions,
dynamic workflow with combination of hot-keys,
a global pivot to do complex transformations,
and you can even set the handle coordinates!

If that fancy curve could be exported…
Blender can import vectors, why not export?


## Install

- Go to `Add-ons` tab in the `User Preferences`
- Click `Install Add-on from File...`
- Find and select `curve_to_svg.py`
- Enable the add-on by clicking on its checkbox


## Usage

Select one or more 2D Curves,
go to `Properties > Data > Export SVG`
and export your curves to a SVG file.

You can adjust the scale factor
(how many pixels one blender unit represents)
and the floating point precision.
There is also the option to minify the SVG file to one line.


## How it works

Once you click `export`,
all selected 2D curves will be processed
to convert its splines to `path` elements:
each point is mapped to path commands
in the `d` attribute.
All original points coordinates are preserved,
and `transform` attributes adjust the elements.

When there are more than one spline,
they are grouped by their assigned material.
So a `g` element contains one `path` for each material index.

If you check the `U` option
in the _Active Spline_ panel,
the spline becomes cyclic
and Blender shows a closed shape.
Even if you don't mark this option,
currently all curves are exported as solid shapes.
But if you want the closing connection,
it is important to select that option
for each spline.

At the same time,
some calculations are performed
to fit all selected curves
in the `viewBox`.
