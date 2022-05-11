#!/bin/bash
# -m = mirror options
# -k = convert links (for offline viewing)
# -p = page requisites (download all files needed to display page)
# -D = domain list
# -np = no parent
# -E = adjust extension (use .htm(l) for pages saved locally)
wget -m -k -p -D janko.at -np -E --restrict-file-names=windows https://www.janko.at/
