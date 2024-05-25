# hl-perps-data

Generates a heatmap with multiple windows with perp funding rates. Also saves them to file.


## Use

```bash
# Clone repo
git clone https://github.com/mtugan/hl-perps-data
# Make virtualenv in dir
virtualenv hl-perps-data
# activate env
cd hl-perps-data
source bin/activate
# Install deps
pip install matplotlib pandas numpy requests
# Run
python funding_heatmap.py
```