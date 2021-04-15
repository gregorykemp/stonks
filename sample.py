# sample.py
#
# A Python program to illustrate the stonks library.
# https://github.com/gregorykemp/stonks
# 
#   Copyright 2021 Gregory A. Kemp
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# We need stonks!
from stonks import stonks

def main():
    print("Hello, world!")

    # Read API key from text file. We don't validate the key here. You'll die soon enough if it's bad.
    file = open("api_key.txt", "r")
    api_key = file.read()
    
    # Make a stock object from the library. Prove it works.
    print("Making a stonk for Apple (AAPL)")
    aapl = stonks("aapl", api_key)
    print("EPS = {}".format(aapl.overview["EPS"]))
    myFscore = aapl.fScore()

    print("AAPL's f-score is {}".format(myFscore))
    print("total = {}".format(sum(myFscore)))
    aapl.fScorePrettyPrint(myFscore)

    # now dump object balance sheet.
    # aapl.dumpOverview()

if __name__ == "__main__":
    main()