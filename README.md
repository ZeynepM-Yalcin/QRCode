# QR Generator
Group section result : 72/78

Individual section result : 21/22

Overall : 93%

Module Code: CS2PP

Assignment report Title: QR Code Generation assignment

Which Artificial Intelligence tools used: Claude AI, Microsoft 365 Co-Pilot, ChatGPT

CSGit
Lab Project Repository URL: https://csgitlab.reading.ac.uk/ac004435/a20
------------------------------------------------------------------------------------------


### Application description and instructions

#### Project Overview
This Python QR code generator creates Version 1 and 2 codes with configurable error correction and mask patterns. Its PyQt5 GUI provides real-time feedback, educational resources, and full error handling.

#### Application Functionality
##### Core features
**QR Generation**
- Version 1 and 2
- Four error correction levels: L, M, Q, H
- Eight mask patterns with automatic best-mask selection
- Reed-Solomon error correction via reedsolo
- Byte mode encoding (ISO-8859-1)

**User Interface**
- Real-time character counter with color feedback
- Automatic or manual version, ECC, and mask settings
- Step-by-step QR generation slideshow
- Tabbed documentation and information utility
- Generation history with analytics
- QR export and customization

**Quality Assurance**
- Input validation and sanitization
- Error handling for invalid characters and length
- Security warnings for phishing/malware risks
- Accessibility presets
- Local processing ensures privacy

### Installation and Setup
Required packages:
- numpy - Matrix operations and QR code data structures
- matplotlib - QR code visualization and rendering
- PyQt5 - GUI framework and user interface components
- reedsolo - Reed-Solomon error correction implementation
- pandas - Generation logging and analytics

**Step 1: Clone the repository**
```
git clone https://csgitlab.reading.ac.uk/ac004435/a20.git
cd a20
```
**Step 2: Create Virtual Environment (Recommended)**
```
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
This step creates an isolated Python environment for the project.

**Why use it?**

1. **Isolation: ** Packages installed for this project won't interfere with other Python projects
1. **Version control:** You can use specific versions of libraries without affecting other projects
1. **Clean setup:** Easy to delete and recreate if something goes wrong
1. **Best practice:** Standard approach for Python development


**Step 3: Install Dependencies**
```
pip install -r requirements.txt
```
**Step 4: Step 4: Run the Application**
`python QrGeneration.py`

### User Operation
_Instructions can also be found in the Information Utility._

1. **Enter Text**: Type your message in the input field
2. **Configure Settings** (Optional):
   - Mode: Automatic (system selects version/ECC) or Manual (choose version 1-2 and ECC L/M/Q/H)
   - Mask Pattern: Auto (best) or Manual (0-7)
1. Generate: Click "Generate QR Code" or press Enter
1. Verify: QR code appears with version, ECC, and mask details
1. Test: Scan with a phone or QR scanner

#### User Options 
| Option | Values | Description |
|--------|--------|-------------|
| **Mode Selection** | Automatic / Manual | Auto selects optimal version and ECC; Manual allows custom configuration |
| **Version** | Auto, 1, 2 | Determines QR code size and capacity: Version 1 (21×21), Version 2 (25×25) |
| **ECC Level** | Auto, L, M, Q, H | Error correction capability: L=7%, M=15%, Q=25%, H=30% |
| **Mask Pattern** | Auto (Best), 0-7 | Data masking pattern; Auto evaluates all patterns using penalty rules and selects optimal |

### Diagram of Code Structure
![Diagram](/uploads/05f98226a606762599b02c7ba920d200/DiagramQR.png)

### ReedSolomon Error Correction Implementation
The reedsolo library was learned from its documentation, GitHub examples, and QR code resources like the Thonky tutorial. Key insight: Reed-Solomon treats data as polynomial coefficients in a Galois field, handled automatically by the library.

#### Implementation in QRGeneration.py

The reedsolo library is used specifically for generating error correction codewords. Here's where and how it's implemented:

```
from reedsolo import RSCodec

def dataEncoding(self, textToEncode):
    # ... (data encoding process)
    
    # 1. Encode text to binary
    binaryString = ""
    modeIndicator = '0100'  # Byte mode
    binaryString += modeIndicator
    
    characterIndicator = format(len(textToEncode), '08b')
    binaryString += characterIndicator
    
    # Convert text to ISO-8859-1 bytes and then to binary
    encMode = textToEncode.encode('iso-8859-1')
    dataString = ''.join(format(byte, '08b') for byte in encMode)
    binaryString += dataString
    
    # 2. Add terminator and padding to reach target length
    # (terminator bits, byte padding, pad bytes)
    # ... padding logic ...
    
    # 3. Determine error correction parameters
    targetBits, ECBytes, index = findEncodingData(self.version, self.level)
    # Example: Version 1, Level L returns targetBits=152, ECBytes=7
    
    # 4. Convert binary string to bytes
    dataBytes = bytes(int(binaryString[i:i+8], 2) 
                     for i in range(0, len(binaryString), 8))
    
    # 5. Apply Reed-Solomon error correction
    # This is where reedsolo is used:
    return reedsolo.RSCodec(ECBytes).encode(dataBytes)
    #      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #      Creates codec with ECBytes error correction symbols
    #      and encodes data, returning data + EC codewords
```
##### The key line:

`reedsolo.RSCodec(ECBytes).encode(dataBytes)`

- `RSCodec(ECBytes)`: Creates a Reed-Solomon encoder
  - `ECBytes` = number of error correction bytes to generate (7 for V1-L, 10 for V1-M, etc.)
  - Automatically configures for GF(256) - the Galois field used in QR codes
  
- `.encode(dataBytes)`: Generates and appends error correction codewords
  - **Input**: `dataBytes` - the data portion only (19 bytes for Version 1, Level L)
  - **Output**: Complete message = data bytes + error correction bytes (26 bytes for V1-L)
  - **Process**: Uses polynomial division in GF(256) to calculate EC codewords

**Example for "known" (5 characters, Version 1, Level L):**

```
Input:  19 data bytes (mode + count + "known" + terminator + padding)
        ↓
RSCodec(7).encode(dataBytes)
        ↓
Output: 26 bytes total (19 original + 7 error correction)
```

The returned bytes are then converted back to binary and placed into the QR code matrix in the zigzag pattern specified by the QR standard.
**Application structure diagram**

### QR generation and Interactive demonstration
https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/demo_1.txt

https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/%20demo_2.txt

https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/demo_3.txt

https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/demo_4.txt

https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/demo_5.txt

### Screen recording, static QR image and CI section .
Screen recording:
https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/Task_2_screen_recording.mp4

This video demonstrates our UI, the 5 inputs required, error handling, the information utlity and gitlab continous integration.

Test String 2 - We've succeeded!:  
[!Test String 2](/uploads/ab24b613698fe911e8e7347a565a9f4f/Test_string_2.png)  

Gitlab Continuous Integration:    
Pipeline success:  
[!Pipeline Succeeding](/uploads/9840a664701c3eb616f405fbabacc1de/Pipeline_success.png)

Pipeline Jobs succeeding:  
[!Jobs Succeeding](/uploads/fe295fecb0bc0874f1fb58f1e5356467/Pipeline_jobs_complete.png)

Pipeline Test Report:  
[!Tests succeeding](/uploads/b3bf2fded05905ed2d26d9733be526d5/Pipeline_tests_complete.png)

### Program paradigms

**Imperative** :  
Ensures operations run in a specific order using iteration, conditionals, and variable assignments. Following the Thonky tutorial, format areas are reserved in a set sequence: below and to the right of the separator, then below, then right.
```
 def reserveFormatAreas(self, size):
        for x in range(9):
            self.reserved[8][x] = True
        
        for y in range(9):
            if y != 6:
                self.reserved[y][8] = True
        
        for y in range(size - 7, size):
            self.reserved[y][8] = True
        
        for x in range(size - 8, size):
            if x != 8:
                self.reserved[8][x] = True
```    
**Functional** :  
Maintains operation order using iteration, conditionals, and variable assignment. Following the Thonky tutorial, features run in a set sequence, e.g., reserving format areas below and to the right of the separator first, then below, then right.

``` 
def addingSeparators(self, qrSquare, size):
        for i in range(8):
            qrSquare[7][i] = 0
            self.reserved[7][i] = True
            qrSquare[i][7] = 0
            self.reserved[i][7] = True

            qrSquare[7][size-8+i] = 0
            self.reserved[7][size-8+i] = True
            qrSquare[i][size-8] = 0
            self.reserved[i][size-8] = True

            qrSquare[size-8][i] = 0
            self.reserved[size-8][i] = True
            qrSquare[size-8+i][7] = 0
            self.reserved[size-8+i][7] = True
        return qrSquare 
```

**Object-oriented** :
Uses classes like QRCanvas, QRLogger, and MaskEvaluator to store data and define actions. MaskEvaluator, for example, includes the apply_mask method and holds pattern_scores and pattern_details. Instances, like evaluator, are initialized in QrGeneration.py.

``` 
class MaskEvaluator:
    """Class to test different QR masks and find the best one"""
    
    def __init__(self):
        # dictionaries to store the scores
        self.pattern_scores = {}
        self.pattern_details = {}
    
    def apply_mask(self, qr_matrix, reserved, mask_num): 
```


### Weaknesses and limitations
Our merged product is limited to version 2 and byte mode, restricting character capacity. Long website links may not generate codes properly.

```
def dataEncoding(self, textToEncode):
        --------
        
        modeIndicator = '0100' # byte mode
        binaryString += modeIndicator
```

Our generator could be misused for phishing. Future updates could include input scanning for security before code generation.
``` 
def generateQRCode(self):
        textToEncode = self.textbox.text() 
        # precondition can be added here
        
        error = validate_text(textToEncode) 
```

Our product resets user settings on exit, forcing manual changes each time. Future versions could save these settings.

The current UI is tall but narrow, making it overwhelming. Future designs could improve layout for easier use.   
`self.qrCanvas.setMinimumSize(350, 350) # can be modified to adjust`


If the input string is invalid, a new QR code is not generated, and any existing QR code remains unchanged.

### Demonstration of all enhancements working in the final application
https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/Final_Merged_product_recording.mp4

This video first shows a qr code being generated using auto encoding and auto mask mode and the version,level and mask pattern results being logged. Also, a seperate window for the qr code slideshow explanation . Then manual mode for the version and ecc level is used aswell as all the accessibility options high contrast, colourblind, low brightness and high visibility yellow. Then mask 1 and 2 are applied to show how users manually chose a mask pattern. Finally, it shows how the system has logged data (timestamp,request_id,text_content,qr_version,ecc_level,mask_pattern,user_options,generation_success) into qr_generation_log.csv with 19 logs it's made during this example use.

### Link to group reflection
https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/96f011b89ee61bf0a501a04bda4efa889bee1f1c/group_reflection.md


### AI tools and references used
**Reedsolo:**

1. reedsolo PyPI page: https://pypi.org/project/reedsolo/
    - Official package page with installation nstructions and basic usage
1. reedsolo GitHub repository: https://github.com/tomerfiliba/reedsolomon
    -  Source code, examples, and more detailed documentation
    -  hows actual implementation details
1. Thonky QR Code Tutorial: https://www.thonky.com/qr-code-tutorial/
    - Comprehensive guide to QR code structure and generation
    - Explains error correction in the context of QR codes specifically
    - Step-by-step breakdown of the entire QR generation process

Generative AI was used through this assignment in order to generate ideas for docstrings and points for readme. Also, it helped us identify errors in our code and allowed members to be able to interpret code that was written by others.

