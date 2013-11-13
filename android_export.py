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
import sys
import os
import subprocess
from copy import copy

def checkForPath(command):
  try:
    subprocess.check_output([
                              command, "--version"
                            ], stderr=subprocess.STDOUT)
    return True
  except:
    return False

def error(msg):
  sys.stderr.write((unicode(msg) + "\n").encode("UTF-8"))
  sys.exit(1)

def export(svg, options, qualifier, dpi):
  dir = "%s/drawable-%s" % (options.resdir, qualifier)

  if not os.path.exists(dir):
    os.makedirs(dir)

  def export_resource(param, name):
    png = "%s/%s.png" % (dir, name)

    subprocess.check_output([
                              "inkscape",
                              "--without-gui",
                              param,
                              "--export-dpi=%s" % dpi,
                              "--export-png=%s" % png,
                              svg
                            ], stderr=subprocess.STDOUT)

    if options.reduce:
      subprocess.check_output([
                                "convert", "-antialias", "-strip", png, png
                              ], stderr=subprocess.STDOUT)
      subprocess.check_output([
                                "optipng", "-quiet", "-o7", png
                              ], stderr=subprocess.STDOUT)

  if options.source == '"selected_ids"':
    for id in options.id:
      export_resource("--export-id=%s" % id, id)
  else:
    export_resource("--export-area-page", options.resname)

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

parser = optparse.OptionParser(usage="usage: %prog [options] SVGfile", option_class=Option)
parser.add_option("--source",  action="store",  help="Source of the drawable. Either 'selected_ids' (specified via --id) or 'page'.")
parser.add_option("--id",      action="append", help="ID attribute of objects to export")
parser.add_option("--resdir",  action="store",  help="Resources directory")
parser.add_option("--resname", action="store",  help="Resource name (when --source=page).")
parser.add_option("--ldpi",    action="store",  type="boolstr", help="Export LDPI variants")
parser.add_option("--mdpi",    action="store",  type="boolstr", help="Export MDPI variants")
parser.add_option("--hdpi",    action="store",  type="boolstr", help="Export HDPI variants")
parser.add_option("--xhdpi",   action="store",  type="boolstr", help="Export XHDPI variants")
parser.add_option("--xxhdpi",  action="store",  type="boolstr", help="Export XXHDPI variants")
parser.add_option("--xxxhdpi", action="store",  type="boolstr", help="Export XXXHDPI variants")
parser.add_option("--reduce",  action="store",  type="boolstr", help="Use ImageMagick and OptiPNG to reduce the image size")

svg = sys.argv[-1]
(options, args) = parser.parse_args()

if options.resdir is None:
  error("No Android Resource directory specified")
if not os.path.isdir(options.resdir):
  error("Wrong Android Resource directory specified:\n'%s' is no dir" % options.resdir)
if not os.access(options.resdir, os.W_OK):
  error("Wrong Android Resource directory specified:\nCould not write to '%s'" % options.resdir)
if options.source not in ('"selected_ids"', '"page"'):
  error("Select what to export (selected items or whole page)")
if options.source == '"selected_ids"' and options.id is None:
  error("Select at least one item to export")
if options.source == '"page"' and not options.resname:
  error("Please enter a resource name")
if not options.ldpi and not options.mdpi and not options.hdpi and not options.xhdpi and not options.xxhdpi and not options.xxxhdpi:
  error("Select at least one DPI variant to export")
if not checkForPath("inkscape"):
  error("Make sure you have 'inkscape' on your PATH")
if options.reduce:
  if not checkForPath("convert"):
    error("Make sure you have 'convert' on your PATH if you want to reduce the image size")
  if not checkForPath("optipng"):
    error("Make sure you have 'optipng' on your PATH if you want to reduce the image size")

if options.ldpi:
  export(svg, options, "ldpi", 67.5)
if options.mdpi:
  export(svg, options, "mdpi", 90)
if options.hdpi:
  export(svg, options, "hdpi", 135)
if options.xhdpi:
  export(svg, options, "xhdpi", 180)
if options.xxhdpi:
  export(svg, options, "xxhdpi", 270)
if options.xxxhdpi:
  export(svg, options, "xxxhdpi", 360)
