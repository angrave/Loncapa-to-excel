## Overview

This project converts a Loncapa server data into anonymized csv data

## Requirements

Uses Python 3 and Pandas

## Optional preprocessing step (required for older versions of Loncapa)

The utility "dbreader.c" (also by Angrave in the same repository) can be used to first extract key-value pairs from the deprecated .db binary format.

## License

Loncapa to Excel

This software was originally developed by Lawrence Angrave in 2019 and 2020. First pubished version Dec 1, 2019.

Licensed under the NCSA Open source license Copyright (c) 2019-2020 Lawrence Angrave, All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal with the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimers. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimers in the documentation and/or other materials provided with the distribution. Neither the names of Lawrence Angrave, University of Illinois nor the names of its contributors may be used to endorse or promote products derived from this Software without specific prior written permission.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE. 

## Main Features

* In addition to native unix epoch millisecond timestamps, timestamps are recorded as readable UTC strings
* Loncapa userid are converted into anonymous ids

## Citations and acknowledgements

In a presentation, report or paper please recognise and acknowledge the the use of this software. Please contact angrave atat illinois.edu for a Bibliography citation. For presentations, the following is sufficient

Loncapa to Excel (https://github.com/angrave/Loncapa-to-excel) by Lawrence Angrave. 
Loncapa-to-excel is project from The Illinois iLearn Group, supported in part by the Institute of Education Sciences Award R305A180211

If you use this in your project, a quick email to the author would be welcomed!
