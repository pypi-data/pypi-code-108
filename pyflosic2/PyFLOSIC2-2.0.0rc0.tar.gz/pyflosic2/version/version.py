#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>
#
__doc__ = """ Contains version information """

# Version
__major__, __minor__, __patch__ = 2, 0, 0
version_number = "{}.{}.{}".format(__major__, __minor__, __patch__)
dct_major = {0: "orc", 1: "knight", 2: "magician", 3: "king", 4: "fairy", 5: "devil"}
dct_minor = {0: "space", 1: "valley", 2: "mountain", 3: "castle", 4: "heaven", 5: "hell"}
version_name = "{}-{}".format(dct_major[__major__], dct_minor[__minor__])

# Logos
code_name = """
  ____        _____ _     ___  ____ ___ ____ ____  
 |  _ \ _   _|  ___| |   / _ \/ ___|_ _/ ___|___ \ 
 | |_) | | | | |_  | |  | | | \___ \| | |     __) |
 |  __/| |_| |  _| | |__| |_| |___) | | |___ / __/ 
 |_|    \__, |_|   |_____\___/|____/___\____|_____|
        |___/                                      
PyFLOSIC2
version: {}//{}
""".format(version_name, version_number)
# Ref.: [1] https://patorjk.com/software/taag/#p=display&h=2&v=2&f=Standard&t=PyFLOSIC2 

goodbye = """                                      

                                      _     
 _ __   _____      _____ _ __ ___  __| |    
| '_ \ / _ \ \ /\ / / _ \ '__/ _ \/ _` |    
| |_) | (_) \ V  V /  __/ | |  __/ (_| |    
| .__/ \___/ \_/\_/ \___|_|  \___|\__,_|    
|_|                                         
 _                        __  __            
| |__  _   _    ___ ___  / _|/ _| ___  ___  
| '_ \| | | |  / __/ _ \| |_| |_ / _ \/ _ \ 
| |_) | |_| | | (_| (_) |  _|  _|  __/  __/ 
|_.__/ \__, |  \___\___/|_| |_|  \___|\___| 
       |___/  

          ██    ██    ██
        ██      ██  ██
        ██    ██    ██
          ██  ██      ██
          ██    ██    ██

      ████████████████████
      ██                ██████
      ██                ██  ██
      ██                ██  ██
      ██                ██████
        ██            ██
    ████████████████████████
    ██                    ██
      ████████████████████


"""
# Ref.: [1] http://patorjk.com/software/taag/#p=display&f=Ogre&t=powered%20%0Aby%20coffee%20
#       [2] https://textart.sh/topic/coffee

if __name__ == '__main__':
    print(code_name)
