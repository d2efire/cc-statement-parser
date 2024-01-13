# cc-statement-parser

This repository contains instructions for parsing the credit card statements of Singapore banks, and obtaining comma-separated outputs. Currently this has only been tested for the following banks: Citibank, DBS, OCBC, and UOB.

You should be comfortable with:
- cloning this repository
- installing dependencies via your operating system's package manager, and from `pypi`
- setting up python virtual environments via `poetry`
- debugging setup and execution failures of open-source projects
- data manipulation using Excel (or other spreadsheet software).

We will be using the awesome [marker](https://github.com/VikParuchuri/marker) project, with all credits to [Vik Paruchuri](https://github.com/VikParuchuri). Specifically, we will use `marker` to convert the PDF file to markdown, and then extract table rows which seem like it could contain transaction data.

The below steps were successfully tested on macOS Sonoma running on an Intel iMac, for credit card statements generated in year 2023.

## Setup

Follow the `marker` setup instructions at https://github.com/VikParuchuri/marker/blob/master/README.md:
```
git clone https://github.com/VikParuchuri/marker.git
cd marker
git checkout f877c02f48d20fa738521b232295124484423438
cat scripts/install/brew-requirements.txt
brew install ocrmypdf libmagic tesseract-lang
```

The `git checkout ...` command is to revert the repository to when I have personally tested my code addition for my use case successfully. Any new additions and changes to the `marker` repository may break my custom code.

Then install the stuff for python:
```
brew install pipx
pipx ensurepath
pipx install poetry
```

Then install python requirements:
```
poetry env use python3.9
poetry install
poetry shell
```

Note: I had issues with `pytorch` in python 3.12, but python 3.9 worked well.

And in the `marker` directory:
```
brew list tesseract
touch local.env
nano local.env
  include the single line (the path might be different on your system):
    TESSDATA_PREFIX=/usr/local/Cellar/tesseract/5.3.3/share/tessdata
```

Replace the original `marker/cleaners/table.py` with the custom `table.py` in this repository.

## Execution

Store a folder containing your credit card statements in PDF form within the `marker` folder.

Run the below command against your statement PDF file (in this e.g., stored at `credit-card-statements/DBS/202312.pdf`) to generate the markdown file (but disregard the output markdown file), and view the csv output, like so:
```
% export BANK=DBS; export YYYYMM=202312; python convert_single.py credit-card-statements/${BANK}/${YYYYMM}.pdf disregard.md

DBS,202312,24 DEC,KOPITIAM INVESTMENT PT,6.57
DBS,202312,25 DEC,LAZADA SINGAPORE,48.09
DBS,202312,25 DEC,FOODPANDA SINGAPORE,21.00
DBS,202312,27 DEC,KRISPAY*COMFORT TRANSP,14.50
DBS,202312,28 DEC,GRAB* A-ABCXYZ,7.50
DBS,202312,28 DEC,GRAB* A-ABCXYZ,27.50
DBS,202312,28 DEC,LAZADA SINGAPORE,27.57
DBS,202312,28 DEC,CABCHARGE ASIA PTE LTD,26.70
DBS,202312,29 DEC,CABCHARGE ASIA PTE LTD,29.40
DBS,202312,29 DEC,KRISPAY*COMFORT TRANSP,19.60
```

The command also works well for Citibank statements:
```
% export BANK=Citibank; export YYYYMM=202312; python convert_single.py credit-card-statements/${BANK}/${YYYYMM}.pdf disregard.md

Citibank,202312,10 DEC,COLD STORAGE SINGAPORE SG,27.60
Citibank,202312,11 DEC,FOUR LEAVES SINGAPORE SG,19.90
Citibank,202312,13 DEC,SHENGSIONG SINGAPORE SG,10.82
Citibank,202312,14 DEC,SHENGSIONG SINGAPORE SG,2.60
```

The output for OCBC statements are a little wonky, but we can still work with it:
```
% export BANK=OCBC; export YYYYMM=202312; python convert_single.py credit-card-statements/${BANK}/${YYYYMM}.pdf disregard.md

OCBC,202312,18/12,136.00,LAZADA SINGAPORE (PAYM
OCBC,202312,25/12,30.12,LAZADA SINGAPORE (PAYM
```

UOB's statement are pretty badly-formed:
```
% export BANK=UOB; export YYYYMM=202312; python convert_single.py credit-card-statements/${BANK}/${YYYYMM}.pdf disregard.md

UOB,202312,02 DEC,27 NOV ,BUS/MRT 326055609 SINGAPORE
UOB,202312,02 DEC,27 NOV ,BUS/MRT 325945929 SINGAPORE
UOB,202312,03 DEC,29 NOV ,BUS/MRT 326924760 SINGAPORE
UOB,202312,1.64,,1.64
UOB,202312,1.70,,1.70
UOB,202312,2.67,,2.67
[...]
UOB,202312,1.98,10 DEC  06 DEC ,BUS/MRT 330128733 SINGAPORE
UOB,202312,28.19,09 DEC  07 DEC ,DIN TAI FUNG SINGAPORE
UOB,202312,1.56,11 DEC  07 DEC ,BUS/MRT 330566119 SINGAPORE
```

2 dates per transaction are present because UOB statements include both the posting and transaction date.

Some data massaging is needed to obtain the correct output, and you should end up with something like:
```
UOB,202312,02 DEC,BUS/MRT 326055609 SINGAPORE,1.64
UOB,202312,02 DEC,BUS/MRT 325945929 SINGAPORE,1.70
UOB,202312,03 DEC,BUS/MRT 326924760 SINGAPORE,2.67
[...]
UOB,202312,10 DEC,BUS/MRT 330128733 SINGAPORE,1.98
UOB,202312,09 DEC,DIN TAI FUNG SINGAPORE,28.19
UOB,202312,11 DEC,BUS/MRT 330566119 SINGAPORE,1.56
```
