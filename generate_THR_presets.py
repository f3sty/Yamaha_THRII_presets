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


# csv fieldnames
fieldnames = ["Preset","Source","Amp","Mode","Gain","Master","Bass","Mid","Treble","Cabinet","Guitar","Audio","Sustain","Level","Threshold","Decay","Type","Speed","Depth","Pre","Feedback","Mix","E_Type","E_Time","E_Feedback","E_Bass","E_Treble","E_Mix","R_Type","Reverb","R_Decay","R_Pre","R_Tone","R_Mix","notes"]

def fn(num):
  if num.isdigit():
    return int(num) / 100
  else:
    return 0.5  # for disabled settings, set to 50%

def isEnabled(num):
  if num.isdigit():
    return True
  else:
    return False

# Load and process the presets csv
with open(presets_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=fieldnames)
    for row in reader:
        if row['Preset'] == "Preset" or row['Preset'] == "Yamaha THRii Presets" or row['Preset'] == "":
            continue

        grpamp = amps[row['Amp']]
        ga = grpamp[row['Mode']]
        # one typo in the spreadsheet, 'Amercan 4x12'
        cabinet = int(cabtype[row['Cabinet'].replace("Amercan","American")])

        # Preset name
        d['data']['meta']['name'] = row['Preset']
        d['data']['meta']['source'] = row['Source']

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
        d['data']['tone']['THRGroupFX1Compressor']['@enabled'] = isEnabled(row['Level'])

        # Effects
        etype = row['Type']
        if etype != 'NA' and etype != "":
          # Presets spreadsheet has Chorus/Phaser/Flanger/Tremolo, translate to their proper names
          if "Chorus" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "StereoSquareChorus"
          elif "Phaser" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "Phaser"
          elif "Flanger" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "L6Flanger"
          elif "Tremolo" in etype:
            d['data']['tone']['THRGroupFX2Effect']['@asset'] = "BiasTremolo"

        d['data']['tone']['THRGroupFX2Effect']['Depth'] = fn(row['Depth'])
        d['data']['tone']['THRGroupFX2Effect']['Feedback'] = fn(row['Feedback'])
        d['data']['tone']['THRGroupFX2Effect']['@wetDry'] = fn(row['Mix'])
        d['data']['tone']['THRGroupFX2Effect']['Freq'] = fn(row['Speed'])
        d['data']['tone']['THRGroupFX2Effect']['Speed'] = fn(row['Speed'])
        d['data']['tone']['THRGroupFX2Effect']['Pre'] = fn(row['Pre'])

        # Assume the effects are disabled is mix is zero
        d['data']['tone']['THRGroupFX2Effect']['@enabled'] = isEnabled(row['Mix'])

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
        d['data']['tone']['THRGroupFX3EffectEcho']['@enabled'] = isEnabled(row['E_Mix'])

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
        d['data']['tone']['THRGroupFX4EffectReverb']['PreDelay'] = fn(row['R_Pre'])
        d['data']['tone']['THRGroupFX4EffectReverb']['Decay'] = fn(row['R_Decay'])
        d['data']['tone']['THRGroupFX4EffectReverb']['@enabled'] = isEnabled(row['R_Mix'])

        # noise gate
        d['data']['tone']['THRGroupGate']['Decay'] = fn(row['Decay'])
        if isEnabled(row['Threshold']):
            d['data']['tone']['THRGroupGate']['@enabled'] = True
            d['data']['tone']['THRGroupGate']['Thresh'] = (fn(row['Threshold'])* 100) - 100

        else:
            d['data']['tone']['THRGroupGate']['@enabled'] = False
            d['data']['tone']['THRGroupGate']['Thresh'] = -50.0

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



          









