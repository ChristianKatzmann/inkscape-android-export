#!/usr/bin/env python

# ***** BEGIN APACHE LICENSE BLOCK *****
#
# Copyright 2013 Christian Becker <christian.becker.1987@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ***** END APACHE LICENCE BLOCK *****

import optparse
import os
import subprocess
import sys
from copy import copy

try:
  from subprocess import DEVNULL
except ImportError:
  DEVNULL = open(os.devnull, 'w')

def checkForPath(command):
  try:
    return 0 == subprocess.call([
                                  command, "--version"
                                ], stdout=DEVNULL, stderr=subprocess.STDOUT)
  except:
    return False

def error(msg):
  sys.stderr.write((unicode(msg) + "\n").encode("UTF-8"))
  sys.exit(1)

def export(svg, options):
  for qualifier, dpi in options.densities:
    export_density(svg, options, qualifier, dpi)

def export_density(svg, options, qualifier, dpi):
  dir_type = "drawable"
  if options.launcher_icon:
    dir_type = "mipmap"

  dir = "%s/%s-%s" % (options.resdir, dir_type, qualifier)

  if not os.path.exists(dir):
    os.makedirs(dir)

  def export_resource(params, name):
    png = "%s/%s.png" % (dir, name)

    call_params = ["inkscape",
                   "--without-gui",
                   "--export-dpi=%s" % dpi,
                   "--export-png=%s" % png]

    if isinstance(params, list):
        call_params.extend(params)
    else:
        call_params.append(params)

    call_params.append(svg)

    subprocess.check_call(call_params, stdout=DEVNULL, stderr=subprocess.STDOUT)

    if options.strip:
      subprocess.check_call([
                              "convert", "-antialias", "-strip", png, png
                            ], stdout=DEVNULL, stderr=subprocess.STDOUT)
    if options.optimize:
      subprocess.check_call([
                              "optipng", "-quiet", "-o7", png
                            ], stdout=DEVNULL, stderr=subprocess.STDOUT)

  if options.source == '"selected_ids"':
    if options.scale and (options.scale > 0):
      dpi *= options.scale

    params = create_selection_params(options)

    for id in options.ids:
      current_params = ["--export-id=%s" % id]
      current_params.extend(params)

      filename = get_selection_filename(id, options)

      export_resource(current_params, filename)

  else:
    export_resource("--export-area-page", options.resname)


def create_selection_params(options):
    params = []
    if options.only_selected:
        params.append("--export-id-only")
    if options.transparent_background:
        params.append("-y 0")
    return params


def get_selection_filename(id, options):
    if len(options.ids) == 1 and options.resname:
        return options.resname

    return id


def check_boolstr(option, opt, value):
  value = value.capitalize()
  if value == "True":
    return True
  if value == "False":
    return False
  raise optparse.OptionValueError("option %s: invalid boolean value: %s" % (opt, value))

class Option(optparse.Option):
  TYPES = optparse.Option.TYPES + ("boolstr",)
  TYPE_CHECKER = copy(optparse.Option.TYPE_CHECKER)
  TYPE_CHECKER["boolstr"] = check_boolstr

def append_density(option, opt_str, value, parser, *density):
  if not value:
    return
  if getattr(parser.values, option.dest) is None:
    setattr(parser.values, option.dest, [])
  getattr(parser.values, option.dest).append(density)

class DensityGroup(optparse.OptionGroup):
  def add_density_option(self, name, dpi):
    self.add_option("--%s" % name, action="callback", type="boolstr", dest="densities", metavar="BOOL",
      callback=append_density, callback_args=(name, dpi), help="Export %s variants" % name.upper())

parser = optparse.OptionParser(usage="usage: %prog [options] SVGfile", option_class=Option)
parser.add_option("--source",  action="store", type="choice", choices=('"selected_ids"', '"page"'),  help="Source of the drawable")
parser.add_option("--id",      action="append", dest="ids", metavar="ID", help="ID attribute of objects to export, can be specified multiple times")
parser.add_option("--resdir",  action="store",  help="Resources directory")
parser.add_option("--resname", action="store",  help="Resource name (when --source=page)")
parser.add_option("--launcher-icon", action="store", type="boolstr", help="Whether the icon is a launcher icon")
parser.add_option("--only-selected", action="store", type="boolstr", help="Export only selected (without any background or other elements)")
parser.add_option("--scale", action="store", type="float", help="Output image scale")
parser.add_option("--transparent-background", action="store", type="boolstr", help="Transparent background")

group = DensityGroup(parser, "Select which densities to export")
# dpi obtained from http://developer.android.com/guide/practices/screens_support.html
# 3:4:6:8 ratio see Table 1. Configuration qualifiers that allow you to provide special resources for different screen configurations.
# and 1:1.5:2:3:4 ratios from developer.android.com/design/style/iconography.html
group.add_density_option("ldpi", 120)
group.add_density_option("mdpi", 160)
group.add_density_option("hdpi", 240)
group.add_density_option("xhdpi", 320)
group.add_density_option("xxhdpi", 480)
group.add_density_option("xxxhdpi", 640)
parser.add_option_group(group)

parser.add_option("--strip",  action="store",  type="boolstr", help="Use ImageMagick to reduce the image size")
parser.add_option("--optimize",  action="store",  type="boolstr", help="Use OptiPNG to reduce the image size")

(options, args) = parser.parse_args()
if len(args) != 1:
  parser.error("Expected exactly one argument, got %d" % len(args))
svg = args[0]

if options.resdir is None:
  error("No Android Resource directory specified")
if not os.path.isdir(options.resdir):
  error("Wrong Android Resource directory specified:\n'%s' is no dir" % options.resdir)
if not os.access(options.resdir, os.W_OK):
  error("Wrong Android Resource directory specified:\nCould not write to '%s'" % options.resdir)
if options.source not in ('"selected_ids"', '"page"'):
  error("Select what to export (selected items or whole page)")
if options.source == '"selected_ids"' and options.ids is None:
  error("Select at least one item to export")
if options.source == '"page"' and not options.resname:
  error("Please enter a resource name")
if not options.densities:
  error("Select at least one DPI variant to export")
if not checkForPath("inkscape"):
  error("Make sure you have 'inkscape' on your PATH")
if options.strip and not checkForPath("convert"):
  error("Make sure you have 'convert' on your PATH if you want to reduce the image size using ImageMagick")
if options.optimize and not checkForPath("optipng"):
  error("Make sure you have 'optipng' on your PATH if you want to reduce the image size using OptiPNG")

export(svg, options)
