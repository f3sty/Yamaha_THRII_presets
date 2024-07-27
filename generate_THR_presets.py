#!/usr/local/bin/python3
import json
import csv
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--presets", help="csv to read presets from. Defaults to 'presets.csv'")
parser.add_argument("--out", help="Directory to write preset file to. Defaults to 'presets'")

args = parser.parse_args()


if args.presets:
    presets_file = args.presets
else:
    presets_file = os.path.join('data','presets.csv')

if args.out:
    presets_dir = args.out
else:
    presets_dir = 'presets'    


# use a template so if the format changes one day,
# its easier to update
with open(os.path.join('data','template.thrl6p')) as json_file:
    d = json.load(json_file)


# load the amp type/mode lookup
with open(os.path.join('data', 'amps.json')) as amps_json:
    amps = json.load(amps_json)

# load in the cab types
cabtype = {}
with open(os.path.join('data','cabs.csv'), newline='') as cabs_csv:
    cabs = csv.DictReader(cabs_csv)
    for row in cabs:
      cabname = row['cab']
      cab_id  = row['cab_id']
      cabtype[cabname] = cab_id


def fn(num):
  if num.isdigit():
    return int(num) / 100
  else:
    return 0


# Load and process the presets csv
with open(presets_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        grpamp = amps[row['Amp']]
        ga = grpamp[row['Mode']]
        cabinet = int(cabtype[row['Cabinet']])

        # Preset name
        d['data']['meta']['name'] = row['Preset']

        # Amp 
        d['data']['tone']['THRGroupAmp']['@asset'] = ga
        d['data']['tone']['THRGroupAmp']['Bass'] = fn(row['Bass'])
        d['data']['tone']['THRGroupAmp']['Mid'] = fn(row['Mid'])
        d['data']['tone']['THRGroupAmp']['Treble'] = fn(row['Treble'])
        d['data']['tone']['THRGroupAmp']['Drive'] = fn(row['Gain'])
        d['data']['tone']['THRGroupAmp']['Master'] = fn(row['Master'])

        # Cab type
        d['data']['tone']['THRGroupCab']['SpkSimType'] = cabinet



        # compressor 
        d['data']['tone']['THRGroupFX1Compressor']['Sustain'] = fn(row['Sustain'])
        d['data']['tone']['THRGroupFX1Compressor']['Level'] = fn(row['Level'])
        if fn(row['Level']) == 0:
          d['data']['tone']['THRGroupFX1Compressor']['@enabled'] = False
        else:
          d['data']['tone']['THRGroupFX1Compressor']['@enabled'] = True

        # Effects
        etype = row['Type']
        if etype != 'NA' and etype != "":
          # Presets spreadsheet has Chorus/Phaser/Flanger/Tremelo, translate to their proper names
          if "Chorus" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "StereoSquareChorus"
          elif "Phaser" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "Phaser"
          elif "Flanger" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "L6Flanger"
          elif "Tremelo" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "BiasTrremelo"

        d['data']['tone']['THRGroupFX2Effect']['Depth'] = fn(row['Depth'])
        d['data']['tone']['THRGroupFX2Effect']['Feedback'] = fn(row['Feedback'])
        d['data']['tone']['THRGroupFX2Effect']['@wetDry'] = fn(row['Mix'])
        d['data']['tone']['THRGroupFX2Effect']['Freq'] = fn(row['Speed'])
        d['data']['tone']['THRGroupFX2Effect']['Pre'] = fn(row['Pre'])

        # Assume the effects are disabled is mix is zero
        if fn(row['Mix']) == 0:
          d['data']['tone']['THRGroupFX2Effect']['@enabled'] = False
        else:
          d['data']['tone']['THRGroupFX2Effect']['@enabled'] = True

        # Echo
        if row['E_Type'] != 'NA':
          if "Delay" in row['E_Type']:
            d['data']['tone']['THRGroupFX3EffectEcho']['@asset'] = "L6DigitalDelay"
          elif "Tape" in row['E_Type']:
            d['data']['tone']['THRGroupFX3EffectEcho']['@asset'] = "TapeEcho"

        d['data']['tone']['THRGroupFX3EffectEcho']['@wetDry'] = fn(row['E_Mix'])
        d['data']['tone']['THRGroupFX3EffectEcho']['Bass'] = fn(row['E_Bass'])
        d['data']['tone']['THRGroupFX3EffectEcho']['Treble'] = fn(row['E_Treble'])
        d['data']['tone']['THRGroupFX3EffectEcho']['Time'] = fn(row['E_Time'])
        d['data']['tone']['THRGroupFX3EffectEcho']['Feedback'] = fn(row['E_Feedback'])
        if fn(row['E_Mix']) == 0:
          d['data']['tone']['THRGroupFX3EffectEcho']['@enabled'] = False
        else:
          d['data']['tone']['THRGroupFX3EffectEcho']['@enabled'] = True

        # Reverb
        rtype = row['R_Type']
        if rtype != 'NA' and rtype != '':
            if "Spring" in rtype:
                d['data']['tone']['THRGroupFX4EffectReverb']['@asset'] = "StandardSpring"
            elif "Room" in rtype:
                d['data']['tone']['THRGroupFX4EffectReverb']['@asset'] = "SmallRoom1"
            elif "Plate" in rtype:
                d['data']['tone']['THRGroupFX4EffectReverb']['@asset'] = "LargePlate1"
            elif "Hall" in rtype:
                d['data']['tone']['THRGroupFX4EffectReverb']['@asset'] = "ReallyLargeHall"

        d['data']['tone']['THRGroupFX4EffectReverb']['@wetDry'] = fn(row['R_Mix'])
        d['data']['tone']['THRGroupFX4EffectReverb']['Time'] = fn(row['R_Decay'])
        d['data']['tone']['THRGroupFX4EffectReverb']['Tone'] = fn(row['R_Tone'])
        if fn(row['R_Mix']) == 0:
          d['data']['tone']['THRGroupFX4EffectReverb']['@enabled'] = False
        else:
          d['data']['tone']['THRGroupFX4EffectReverb']['@enabled'] = True

        # noise gate
        d['data']['tone']['THRGroupGate']['Thresh'] = (fn(row['Threshold'])* 100) - 100
        d['data']['tone']['THRGroupGate']['Decay'] = fn(row['Decay'])
        if fn(row['Threshold']) == 0:
            d['data']['tone']['THRGroupGate']['@enabled'] = False
        else:
            d['data']['tone']['THRGroupGate']['@enabled'] = True

        # write the preset out to a file  
        if not os.path.exists(presets_dir):
          os.makedirs(presets_dir)
        fname = row['Preset'] + ".thrl6p"
        # watch out for slashes in the preset filenames
        x = fname.replace("/","_")
        fname = os.path.join(presets_dir, x)
        print(fname)
        with open(fname, 'w') as preset_file:
            json.dump(d, preset_file, indent=2)



          









