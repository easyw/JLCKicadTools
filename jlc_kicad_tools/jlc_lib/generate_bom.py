# Copyright (C) 2019 Matthew Lai
# Copyright (C) 1992-2019 Kicad Developers Team
#
# This file is part of JLC Kicad Tools.
#
# JLC Kicad Tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# JLC Kicad Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JLC Kicad Tools.  If not, see <https://www.gnu.org/licenses/>.

from jlc_kicad_tools.jlc_lib import kicad_netlist_reader
import csv
import re
import logging
import os

VERSION = "1.1.0 March 2021"

LCSC_PART_NUMBER_MATCHER=re.compile('^C[0-9]+$')

def GenerateBOM(input_filename, output_filename, opts):
  net = kicad_netlist_reader.netlist(input_filename)

  try:
    f = open(output_filename, mode='w', encoding='utf-8')
    #print(output_filename)
    #fp_output_filename = output_filename.rstrip("_bom_jlc.csv")+"_fp_jlc.txt"
    fp_output_filename = output_filename[:-12]+"_fp_jlc.txt"
    print(fp_output_filename)
    #pcb_input_filename = output_filename[:-12]+".kicad_pcb"
    #print(pcb_input_filename)
    #pcb_output_filename = output_filename[:-12]+"-no-paste.txt"
    #print(pcb_output_filename)
    #fpcb_in = open(pcb_input_filename, mode='r', encoding='utf-8')
    #fpcb_out = open(pcb_output_filename, mode='w', encoding='utf-8')
    
    ffp = open(fp_output_filename, mode='w', encoding='utf-8')
    
  except IOError:
    logging.error("Failed to open file for writing: {}".format(output_filename))
    return False

  out = csv.writer(f, lineterminator='\n', delimiter=',', quotechar='\"',
                   quoting=csv.QUOTE_ALL)
  fp_out = csv.writer(ffp, lineterminator='\n', delimiter=',', quotechar='\"',
                   quoting=csv.QUOTE_ALL)
  
  out.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])

  grouped = net.groupComponents()

  num_groups_found = 0
  DNP_footprints = []
  for group in grouped:
    refs = []
    lcsc_part_numbers = set()
    lcsc_part_numbers_none_found = False
    footprints = set()
    #DNP_footprints = []

    for component in group:
      refs.append(component.getRef())
      c = component
      lcsc_part_number = None

      # Get the field name for the LCSC part number.
      for field_name in c.getFieldNames():
        field_value = c.getField(field_name).strip()

        if LCSC_PART_NUMBER_MATCHER.match(field_value):
          lcsc_part_number = field_value

      if lcsc_part_number:
        lcsc_part_numbers.add(lcsc_part_number)
      else:
        if c.getFootprint() != '':
            #print(c.getFootprint(),c.getRef())
            #print(c.getFootprint() not in str(DNP_footprints))
            if c.getFootprint() not in str(DNP_footprints):
                DNP_footprints.append(c.getFootprint())
                #print(DNP_footprints)
                fp_out.writerow([c.getRef(),c.getFootprint()])
                # fp_out.writerow([c.getFootprint()])
                #ffp.write(str([c.getFootprint()]))
        lcsc_part_numbers_none_found = True

      if c.getFootprint() != '':
        footprints.add(c.getFootprint())

    # Check part numbers for uniqueness
    if len(lcsc_part_numbers) == 0:
      if opts.warn_no_partnumber:
        logging.warning("No LCSC part number found for components {}".format(",".join(refs)))
      continue
    elif len(lcsc_part_numbers) != 1:
      logging.error("Components {components} from same group have different LCSC part numbers: {partnumbers}".format(
          components = ", ".join(refs),
          partnumbers = ", ".join(lcsc_part_numbers)))
      return False
    lcsc_part_number = list(lcsc_part_numbers)[0]

    if (not opts.assume_same_lcsc_partnumber) and (lcsc_part_numbers_none_found):
      logging.error("Components {components} from same group do not all have LCSC part number {partnumber} set. Use --assume-same-lcsc-partnumber to ignore.".format(
          components = ", ".join(refs),
          partnumber = lcsc_part_number))
      return False

    # Check footprints for uniqueness
    if (len(footprints) == 0):
      logging.error("No footprint found for components {}".format(",".join(refs)))
      return False
    if len(footprints) != 1:
      logging.error("Components {components} from same group have different foot prints: {footprints}".format(
          components = ", ".join(refs),
          footprints = ", ".join(footprints)))
      return False
    footprint = list(footprints)[0]
    #print(DNP_footprints, len(DNP_footprints))
    #DNP_footprint = list(DNP_footprints)[0]
    #print(list(DNP_footprints))
    
    # They don't seem to like ':' in footprint names.
    footprint = footprint[(footprint.find(':') + 1):]

    # Fill in the component groups common data
    out.writerow([c.getValue(), ",".join(refs), footprint, lcsc_part_number])
    num_groups_found += 1

  logging.info("{} component groups found from BOM file.".format(num_groups_found))

  return True

  
def removePaste(input_filename):
  try:
    #print(output_filename)
    #fp_output_filename = output_filename.rstrip("_bom_jlc.csv")+"_fp_jlc.txt"
    #print(input_filename)
    fp_input_filename = input_filename[:-4]+"_fp_jlc.txt"
    #print(input_filename)
    #print(fp_input_filename)
    pcb_input_filename = input_filename[:-4]+".kicad_pcb"
    #print(input_filename)
    #print(pcb_input_filename)
    pcb_output_filename = input_filename[:-4]+"-jlc-no-paste.kicad_pcb"
    #print(input_filename)
    #print(pcb_output_filename)
    fp_in = open(fp_input_filename, mode='r', encoding='utf-8')
    fpcb_in = open(pcb_input_filename, mode='r', encoding='utf-8')
    fpcb_out = open(pcb_output_filename, mode='w', encoding='utf-8')
    #ffp = open(fp_output_filename, mode='w', encoding='utf-8')
    
  except IOError:
    logging.error("Failed to open file for writing: {}".format(pcb_output_filename))
    return False
  
  footprints=[] #""
  references=[]
  for j, fp in enumerate(fp_in):
  #  print(j, fp.replace("\"",""))
    #footprints+=fp.replace("\"","")+';'
    temp_ref_fp=fp.split("\",\"")
    # print(temp_ref_fp)
    # print(temp_ref_fp[0].replace("\"",""))
    # print(temp_ref_fp[1].replace("\"","")[:-1])
    references.append(temp_ref_fp[0].replace("\"",""))
    footprints.append(temp_ref_fp[1].replace("\"","")[:-1])
    #footprints.append(fp.replace("\"","")[:-1])
  #print(footprints)
  fp_found=False
  rf_found=False
  fp_SMD=False
  #for fp in footprints:
  pcb_lines=[]
  for i, line in enumerate(fpcb_in):
    pcb_lines.append(line)
  
  #for i, line in enumerate(fpcb_in):
  i = 0
  no_paste_fps=0
  while i < len(pcb_lines)-1:
    line = pcb_lines[i]
    j=i
    #for fp in footprints:
    if line.startswith("    (fp_text reference"): #("  (module "):
        #if "a_SMD_DIODE-TR:SOT-23-5" in line:
        # print (line)
        for rf in references:
            #print (rf, line)
            if (" "+rf+" ") in line: #found reference
                # print("ref found", rf, line)
                rf_found=True
                fp_SMD=False
            if (" \""+rf+"\" ") in line: #found "reference"
                # print("ref found", rf, line)
                rf_found=True
                fp_SMD=False
            rf_search = rf
            if rf_found==True:
                pcb_out = fpcb_out.write(line)
                end_reached = False
                # print('checking for '+rf)
                while (end_reached == False) and (i < len(pcb_lines)):
                    i+=1
                    line = pcb_lines[i]
                    # if line.startswith("    (attr smd)") and rf_found==True:
                    #     fp_SMD=True
                    #     no_paste_fps+=1
                    #if line.startswith("    (pad") and fp_SMD==True and rf_found==True:
                    if line.startswith("    (pad") and rf_found==True:
                        if " F.Paste" in line:
                            fp_SMD=True
                            line = line.replace(" F.Paste","")
                            if rf == rf_search:
                                no_paste_fps+=1
                                rf_search = "already counted"
                                print('removing F.Paste on '+rf)
                    if line.startswith("  )"): # and fp_SMD==True:
                        rf_found=False
                        fp_SMD=False
                        end_reached = True
                    pcb_out = fpcb_out.write(line)
        ## for fp in footprints:
        ##     if fp in line:
        ##         #print("fp found", fp, line)
        ##         fp_found=True
        ##         fp_SMD=False
        ##     if fp_found==True:
        ##         pcb_out = fpcb_out.write(line)
        ##         end_reached = False
        ##         while (end_reached == False) and (i < len(pcb_lines)):
        ##             i+=1
        ##             line = pcb_lines[i]
        ##             if line.startswith("    (attr smd)") and fp_found==True:
        ##                 fp_SMD=True
        ##                 no_paste_fps+=1
        ##             if line.startswith("    (pad") and fp_SMD==True and fp_found==True:
        ##                 line = line.replace(" F.Paste","")
        ##             if line.startswith("  )"): # and fp_SMD==True:
        ##                 fp_found=False
        ##                 fp_SMD=False
        ##                 end_reached = True
        ##             pcb_out = fpcb_out.write(line)
    if j==i:
        pcb_out = fpcb_out.write(line)
    i+=1
    #print (i,line)
  pcb_out = fpcb_out.write('  (gr_text "JLC NO PASTE PCB FILE!!!" (at 186.583 300.962) (layer Cmts.User)'+os.linesep)
  pcb_out = fpcb_out.write('    (effects (font (size 15 15) (thickness 1.0)))'+os.linesep)
  pcb_out = fpcb_out.write('  )'+os.linesep)
  pcb_out = fpcb_out.write(')'+os.linesep)
  print(pcb_output_filename,'written')
  print("removed Paste on ",no_paste_fps,"footprints")
    
  return True
