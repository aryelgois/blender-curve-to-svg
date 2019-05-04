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
