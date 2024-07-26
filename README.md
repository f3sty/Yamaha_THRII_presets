(If you just want to download the presets, get the zip file here https://raw.githubusercontent.com/f3sty/Yamaha_THRII_presets/main/presets/0_presets.zip)


## Yamaha THRII Presets file generator ##

Grab the latest presets spreadsheet from https://docs.google.com/spreadsheets/d/10lyVgoF1gH7fTSWiEYdZt8hImeB0m6s7LzRIS4W9ENo and download as CSV

Replace the top 3 header rows with the header from data/presets.header

e.g.  

     $ cat data/presets.header > my_presets.csv; tail -n +2 downloaded_presets.csv >> my_presets.csv

Run  
     
      ./generate_THR_presets.py --presets my_presets.csv --out my_presets  
      

Optionally add --master nn to set the master volume of all the presets to nn (1-100)



