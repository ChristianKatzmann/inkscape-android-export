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

def check(value):
  return value.capitalize() == 'True'

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

def export(svg, options, qualifier, dpi):
  dir = "%s/drawable-%s" % (options.resdir, qualifier)

  if not os.path.exists(dir):
    os.makedirs(dir)

  for id in options.id:
    png = "%s/%s.png" % (dir, id)

    subprocess.check_output([
                              "inkscape",
                              "--without-gui",
                              "--export-id=%s" % id,
                              "--export-dpi=%s" % dpi,
                              "--export-png=%s" % png,
                              svg
                            ], stderr=subprocess.STDOUT)

    if check(options.reduce):
      subprocess.check_output([
                                "convert", "-antialias", "-strip", png, png
                              ], stderr=subprocess.STDOUT)
      subprocess.check_output([
                                "optipng", "-quiet", "-o7", png
                              ], stderr=subprocess.STDOUT)

parser = optparse.OptionParser(usage="usage: %prog [options] SVGfile")
parser.add_option("--id",     action="append", help="ID attribute of objects to export")
parser.add_option("--resdir", action="store",  help="Resources directory")
parser.add_option("--ldpi",   action="store",  help="Export LDPI variants")
parser.add_option("--mdpi",   action="store",  help="Export MDPI variants")
parser.add_option("--hdpi",   action="store",  help="Export HDPI variants")
parser.add_option("--xhdpi",  action="store",  help="Export XHDPI variants")
parser.add_option("--xxhdpi", action="store",  help="Export XXHDPI variants")
parser.add_option("--reduce", action="store",  help="Use ImageMagick and OptiPNG to reduce the image size")

svg = sys.argv[-1]
(options, args) = parser.parse_args()

if options.resdir is None:
  error("No Android Resource directory specified")
elif not os.path.isdir(options.resdir):
  error("Wrong Android Resource directory specified:\n'%s' is no dir" % options.resdir)
elif not os.access(options.resdir, os.W_OK):
  error("Wrong Android Resource directory specified:\nCould not write to '%s'" % options.resdir)
elif options.id is None:
  error("Select at least one item to export")
elif not check(options.ldpi) and not check(options.mdpi) and not check(options.hdpi) and not check(options.xhdpi) and not check(options.xxhdpi):
  error("Select at least one DPI variant to export")
elif not checkForPath("inkscape"):
  error("Make sure you have 'inkscape' on your PATH")
elif check(options.reduce) and not checkForPath("convert"):
  error("Make sure you have 'convert' on your PATH if you want to reduce the image size")
elif check(options.reduce) and not checkForPath("optipng"):
  error("Make sure you have 'optipng' on your PATH if you want to reduce the image size")
else:
  if check(options.ldpi):
    export(svg, options, "ldpi", 67.5)
  if check(options.mdpi):
    export(svg, options, "mdpi", 90)
  if check(options.hdpi):
    export(svg, options, "hdpi", 135)
  if check(options.xhdpi):
    export(svg, options, "xhdpi", 180)
  if check(options.xxhdpi):
    export(svg, options, "xxhdpi", 270)
