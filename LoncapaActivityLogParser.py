#!/usr/bin/env python
# coding: utf-8

# # Loncapa to Excel
# 
# 
# First pubished version Dec 22, 2019.  
# This is version 0.0002 (revision March 23, 2020)
# 
# Licensed under the NCSA Open source license
# Copyright (c) 2019,2020 Lawrence Angrave
# All rights reserved.
# 
# Developed by: Lawrence Angrave
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal with the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
#    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimers.
#    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimers in the documentation and/or other materials provided with the distribution.
#    Neither the names of Lawrence Angrave, University of Illinois nor the names of its contributors may be used to endorse or promote products derived from this Software without specific prior written permission. 
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE. 
# 
# # Citations and acknowledgements welcomed!
# 
# In a presentation, report or paper please recognise and acknowledge the the use of this software.
# Please contact angrave@illinois.edu for a Bibliography citation. For presentations, the following is sufficient
# 
# Loncapa-to-excelL (https://github.com/angrave/Loncapa-to-excel) by Lawrence Angrave.
# Loncapa-to-excel is an iLearn project, supported by an Institute of Education Sciences Award R305A180211

cat LoncapaActivityLogParser.py 
import hashlib
import urllib
import re
from collections import OrderedDict
import argparse
import os
import pandas as pd
import numpy as np
from datetime import datetime
import traceback

remove_keys = set( ['rndseed','host', 'ip','version'])

assert 1 / 2 > 0, 'This script requires Python 3'

anonmap = OrderedDict()
anonmap[''] = ''
anonmap_modified = False

def drop_lon_capa_event( params ):
   return params['url'] =='_discussion'

def create_argparser():
   argparser = argparse.ArgumentParser( description='Parses LON-CAPA activity logs.')
   argparser.add_argument('--anonmapfile', type=str,
                       help='Filename to load (and, if salt is defined, save) userid to anonid mapping. Expected File Format: userid \\t guid')
   argparser.add_argument('--salt', type=str,
                       help='25 ASCII character salt ending with with a -. New anonids will only be generated if salt is non-empty')
   argparser.add_argument('--saltfile', type=str,
                       help='File containing the salt to prepend to new non-empty userids to generate missing anonid entries. New anonids will only be generated if salt is non-empty')
   argparser.add_argument('input_filename', type=str,
                       help='Filename of a LON-CAPA activity log.')
   argparser.add_argument('output_filename', type=str,
                       help='Output will be written in CSV format to this file. The file will be '
                       'overwritten if it already exists.')
   args = argparser.parse_args()
   if args.salt:
       verify_salt(args.salt)
   return args

# Caller should have lower'd and strip'd the userid already
def userid_to_guid_calc(userid,salt):
    if userid is None or  len(userid) == 0:
       return ''
    if salt is None or len(salt) ==0:
        return 'anonymized'
    return  'p' + hashlib.sha1((salt + userid).encode('utf-8')).hexdigest()[0:12]


def to_guid(userid, anonmap, salt):
    if userid is None:
        return ''
    key = userid.strip().lower()
    if key in anonmap:
        return anonmap[key]
    elif salt:
        anonid = userid_to_guid_calc(key,salt)
        anonmap[key] = anonid  
    else:
        anonid = ''
    return anonid

def verify_salt(salt):
    if len(salt) <15 or salt[-1] != '-' or any((ord(char) >126 or ord(char)<33) for char in salt):
        raise f"'{salt}' is invalid. Expected at least 15 ASCII printable non-space characters ending with a '-'"

def load_salt(saltfile):
    if saltfile is None:
       return None
    with open(saltfile) as f:
       salt = f.read().rstrip("\n")
    verify_salt(salt)
    return salt

def load_anonmap(anonmapfile,salt):
    anonmap = OrderedDict()
    anonmap['']=''
 
    if anonmapfile is None or not( os.path.exists(anonmapfile)):
       return anonmap

    with open(anonmapfile,'r') as f:
        lines=f.read().splitlines() # Eats mixed line endings
    assert( lines[0].strip() == 'userid\tguid')

    print( f"{len(lines)} lines read from {anonmapfile}" )
    count_saltynomatch = 0
    anonmap = OrderedDict()
    for line in lines[1:]:
        k,v = line.split('\t')
        k,v = k.strip(), v.strip()
        if len(k)==0:
           assert len(v) ==0
        else:
           anonmap[k]=v
        if salt:
           vcalc = userid_to_guid_calc(k, salt)
           if v != vcalc:
              count_saltynomatch +=1
    print( f"{count_saltynomatch} entries out of {len(lines) -1} created with different salt")
    return anonmap

def save_anonmap(anonmapfile, anonmap):
      print( f'Updating {anonmapfile} to {len(anonmap)} entries')
      with open(anonmapfile,'w') as fh:
        print( 'userid\tguid', file=fh)
        for k,v in anonmap.items():
            print( f"{k}\t{v}", file=fh)

def split_fields(details,row_i):
   keyvalues = []
   # Watch out for A&B&C&D i.e. va;od entries must have an equal in
   for kv in details.split('&'):
       if kv.find('=') > 1:
          keyvalues.append(kv)
       else:
          keyvalues[-1] += kv
   result = OrderedDict()
   subids = list()  # Use a list so we can preserve the sequence order
   qids = set()

   for kv in keyvalues:
      k,v = kv.split('=',1)
      if k.startswith('resource.'):
          subkeys=k.split('.')
          if len(subkeys) == 4:
             subid = (subkeys[2]) # not all subparts are integers e.. '4fd'
             if subid not in subids:
                 subids.append(subid)
          if len(subkeys) in [3,4]:
             qids.add(subkeys[1])
             k = subkeys[-1]
      if k not in remove_keys:
          result[k] = v
   assert( len(qids)  < 2 )
   if len(qids) == 1:
       result['qid' ] = str(list(qids)[0])
   if len(subids) > 0:
       result['qsubparts' ] = str(subids)

   return result

# 3 rows had a timestamp with a % prefix
def to_float_or_none(value):
    try:
       return float(value)
    except Exception as e:
       return None


def decode_unixtimestamp_to_UTC(seconds):
    if(pd.isnull(seconds) or pd.isna(seconds) or seconds == ''):
        return ''
    try:
        return datetime.utcfromtimestamp(float(seconds)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        traceback.print_exc()
        print("Bad unix timestamp?", seconds , e)
        return ''


def process_cstore(components, params, row_i):
   assert (len(components)) == 6
   assert components[4] == "CSTORE"
   details = urllib.parse.unquote( components[5] )
   fields= split_fields(details,row_i)
   for k in sorted(fields.keys()):
      params['lc_' + k.lower()] = fields[k]

# Read in data and split into columns.

def load_data(input_filename):
   print(f'Loading data {input_filename}')
   return  pd.read_csv(input_filename,
                   header=None,
                   names=['server_timestamp', 'server', 'extra'],
                   sep=':')

def process_data(data, anonmap,salt):
    print('Processing...')
# Try to decode the last column.
    data.extra = data.extra.astype(str).apply(urllib.parse.unquote)
    parsed = []
    forum_events = 0

    for row_i, row in data.iterrows():
    # The client seems to submit several actions at once, so we need to split them into new rows.
    # Split based on 10-digit numbers (i.e. Unix timestamps), keeping the timestamps.
       actions= re.sub('&([0-9]{10})', '%%%%%%%%\\1', row.extra).split('%%%%%%%%')
       for i, sub_row in enumerate(actions):
          components = sub_row.split(':')
          if len(components) < 2:
            raise ValueError('Unexpected sub-row format on line ' + (row_i + 1))
          # Build new rowm starting with server name and time
          params = OrderedDict(row)
          del params['extra']
          params['loncapa-linenumber'] = row_i + 1
          params['client_timestamp'] = components[0]
          params['url'] = urllib.parse.unquote(components[1])
          params['guid'] = to_guid(components[2], anonmap, salt)
          if '/aboutme/' in params['url'] or '/portfolio/' in params['url']:
            params['url'] = 'removed aboutme URL for anonymization'

          # This "extra" stuff is still not well defined and needs context-sensitive parsing.
          eventtype = components[4] if len(components) > 4 else '' 
          params['loncapa-eventtype'] = eventtype
          #params['extra'] = ':'.join(components[3:])
          #params['decoded_extra'] = urllib.parse.unquote(params['extra'])
          #is_forum_post =  'sendername' in sub_row 
          is_cstore = eventtype == 'CSTORE'
          #is_post = eventtype == 'POST'

          if is_cstore:
             process_cstore(components, params, row_i)
             if not drop_lon_capa_event(params): 
                parsed.append(params)

       if (row_i+1) % 1000 == 0:
          print(f'Parsed {1 + row_i} lines. {len(parsed)} events.')

    df = pd.DataFrame.from_records(parsed)

    for col in df.columns & ['client_timestamp','server_timestamp','lc_duedate']:
        c = str(col)
        print( 'Processing column ' + c)
        df[c] = df[c].map( to_float_or_none)
        df[ c + '_utc'] = df[c].map(decode_unixtimestamp_to_UTC)
        df[c] = df[c].map( lambda x: str(int(1000*x)) if x is not None and not  np.isnan(x) else None)

    return df

def save_data(output_filename, events):
    print(f'Saving anonymized {len(events)} events to {output_filename}.')
    events.to_csv(output_filename, index=False)


def main():
    print("Started")
    args = create_argparser()
    salt = args.salt if args.salt else load_salt(args.saltfile) 
    anonmap = load_anonmap(args.anonmapfile,salt)
    anonmap_original = dict(anonmap)
    raw_data = load_data(args.input_filename)
    events = process_data(raw_data, anonmap,salt)
    save_data(args.output_filename, events)
    
    if anonmap != anonmap_original:
       print(f'{len(anonmap) - len(anonmap_original)} entries added to the anonmap')
       if args.anonmapfile and salt:
          save_anonmap(args.anonmapfile, anonmap)
    print("Finished")

if __name__== "__main__": main()
(base) angrave@la-stat01:/data/p
# 
