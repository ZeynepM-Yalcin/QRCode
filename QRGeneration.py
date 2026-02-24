import reedsolo
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
    QVBoxLayout, QWidget, QMessageBox, QComboBox,
    QGroupBox, QRadioButton, QSizePolicy, QScrollArea
)

from PyQt5.QtCore import Qt

from informationUtility import InformationUtil
from logic.validate_code import validate_text # input validation
from qr_logger import QRLogger # analytics and logging
from qr_mask_selector import MaskEvaluator, make_report # 33027025 mask selection logic
from qr_automaticVersionECC import findInfo
from qr_automaticVersionECC import placeAlignment
from qr_automaticVersionECC import findVersionEcc
from qr_automaticVersionECC import findEncodingData # version/ECC calculations
from qr_slideshow import QRSlideshow # step-by-step qr slideshow
from qr_customisation import render_qr # 31825794 colour and accessibility

class QRCanvas(FigureCanvas): 
    """
    A custom Matplotlib canvas embedded in a PyQt5 widget.
    
    This class is responsible for displaying the generated QR code
    inside the GUI using a Matplotlib figure.
    """
    def __init__(self, parent=None):
        """
        Initialises the Matplotlib figure and axes used to display the QR code.
    
        Args:
            parent, The parent Qt widget (usually the main window)
        """
        self.fig = Figure(figsize=(6, 6))
        self.axes = self.fig.add_subplot(111)
        self.axes.axis("off")
        super().__init__(self.fig)
        self.setParent(parent)

    def displayQR(self, qrCode):
        """
        Displays the generated QR code on the embedded canvas.
    
        Parameters:
            qrCode, A 2D array or image representing the QR code to be displayed.
        """
        self.axes.clear()
        self.axes.imshow(qrCode, interpolation="nearest")
        self.axes.axis("off")
        self.axes.set_position([0, 0, 1, 1])
        self.draw()

class MainWindow(QMainWindow):
    """
    Main application window for the QR Code Generator.
    
    This class manages:
    - The graphical user interface (GUI)
    - User interactions (buttons, inputs, options)
    - Coordination between QR generation logic and visual output
    """
    def __init__(self): # Initialises the main window and sets up all UI components
        super().__init__()

        self.setWindowTitle("QR Code Generator") # set application window title
        self.logger = QRLogger() # handles analytics and logging
        
        # Alvia modified - dynamic version/size/level
        self.version = -1
        self.size = 0
        self.level = ''
        
        # Allows the user to enter the string that will be encoded into the QR code
        label = QLabel("Enter string to be encoded: ")
        self.textbox = QLineEdit()
        self.textbox.setPlaceholderText("Type your text here...")
        self.textbox.setToolTip("Version 1 QR Code supports up to 17 characters and Version 2 supports up to 32.\nSupported: Letters (A-Z), numbers (0-9), and basic punctuation.\nPress Enter to generate.")
        self.textbox.textChanged.connect(self.updateCharacterCount) # character counter
        self.textbox.returnPressed.connect(self.generateQRCode) # generate QR with enter key
        
        self.charCountLabel = QLabel("0/17 characters (Version 1 QR Code)")
        self.charCountLabel.setStyleSheet("color: gray; font-size: 10pt;")
        
        # Action buttons for generating a QR code or loading an example
        self.generateBtn = QPushButton("Generate QR Code")
        self.generateBtn.clicked.connect(self.generateQRCode)
        
        self.exampleBtn = QPushButton("Try Example")
        self.exampleBtn.clicked.connect(self.loadExample)

        # Lase added qr customisation and accessibility presets
        # colour options given can improve contrast or readability
        self.presetLabel = QLabel("QR Colour & Accessibility Preset:")

        self.presetCombo = QComboBox()
        self.presetCombo.addItem("High Contrast", "high_contrast")
        self.presetCombo.addItem("Colour-blind Friendly", "colour_blind_friendly")
        self.presetCombo.addItem("Low Brightness", "low_brightness")
        self.presetCombo.addItem("High Visibility (Yellow)", "high_visibility_yellow")

        self.presetCombo.setToolTip(
    "Choose a colour preset designed for different accessibility needs"
)

        # Canvas used to render and display the generated QR code
        self.qrCanvas = QRCanvas(self)
        
        # Alvia Modified this
        self.qrCanvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Alvia modified this
        self.qrCanvas.setMinimumSize(350, 350)
        
        # Status message area for errors, warnings, and success messages
        self.statusLabel = QLabel("")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setWordWrap(True)
        
        # Warning about character encoding limitations 
        self.encodingWarning = QLabel("Note: QR codes are encoded using ISO-8859-1. Some phone scanners may display special characters (¡, ñ, etc.) incorrectly as they default to UTF-8 decoding.")
        self.encodingWarning.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        self.encodingWarning.setWordWrap(True)
        self.encodingWarning.setAlignment(Qt.AlignCenter)

        # Buttons for help information and usage analytics
        self.infoBtn = QPushButton("Information & Help")
        self.infoBtn.clicked.connect(self.showInformationDialog)

        self.analyticsBtn = QPushButton("View Analytics") #Nina edited this 
        self.analyticsBtn.clicked.connect(self.showAnalytics)

        # Alvia added the encoding option section
        # -----------------------------------------------
        self.modeGroup = QGroupBox("Encoding Mode")

        self.autoModeRadio = QRadioButton("Automatic (recommended)")
        self.manualModeRadio = QRadioButton("Manual")
        self.autoModeRadio.setChecked(True)
        self.autoModeRadio.toggled.connect(self.updateMode)

        modeLayout = QVBoxLayout()
        modeLayout.addWidget(self.autoModeRadio)
        modeLayout.addWidget(self.manualModeRadio)
        self.modeGroup.setLayout(modeLayout)

        # Dropdowns for selecting QR version and error correction level
        # These are only enabled when manual mode is selected
        self.versionCombo = QComboBox()
        self.versionCombo.addItems(["Auto", "1", "2"])
        self.versionCombo.setEnabled(False)

        self.eccCombo = QComboBox()
        self.eccCombo.addItems(["Auto", "L", "M", "Q", "H"])
        self.eccCombo.setEnabled(False)

        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(QLabel("Version:"))
        optionsLayout.addWidget(self.versionCombo)
        optionsLayout.addWidget(QLabel("ECC:"))
        optionsLayout.addWidget(self.eccCombo)
        #-------------------------------------------------
        #---- MASK SELECTOR ENHANCEMENT (33027025) ----
        self.maskLabel = QLabel("Mask Pattern Selection:")
        self.maskComboBox = QComboBox()
        self.maskComboBox.addItem("Auto (Best)") # Automatically selects the lowest penalty mask
        for i in range(8):
            self.maskComboBox.addItem(f"Mask {i}")
        self.maskComboBox.setToolTip("Select 'Auto' to automatically choose the best mask pattern,\nor manually select a specific pattern (0-7)")
        #----
        self.maskInfoLabel = QLabel("")
        self.maskInfoLabel.setStyleSheet("color: #0066cc; font-size: 9pt;")
        self.maskInfoLabel.setWordWrap(True)
        self.maskInfoLabel.setAlignment(Qt.AlignCenter)

        # Main vertical layout
        # Organises all UI components from top to bottom
        layout = QVBoxLayout()
        layout.addWidget(self.presetLabel) # Lase added preset label and combo to help qr customisation
        layout.addWidget(self.presetCombo)
        layout.addWidget(label)
        layout.addWidget(self.textbox)
        layout.addWidget(self.charCountLabel)
        layout.addWidget(self.generateBtn)
        layout.addWidget(self.exampleBtn)
        layout.addWidget(self.statusLabel)
        layout.addWidget(self.encodingWarning)
        layout.addWidget(self.modeGroup)
        layout.addLayout(optionsLayout)
        layout.addWidget(self.infoBtn)
        layout.addWidget(self.analyticsBtn)

        #----MASK SELECTOR UI (33027025) ----

        layout.addWidget(self.maskLabel)
        layout.addWidget(self.maskComboBox)
        layout.addWidget(self.maskInfoLabel)
        #----
        layout.addWidget(self.qrCanvas, stretch=1)

        # Container widget to hold the layout
        # Required to set a layout as the central widget of the window
        container = QWidget()
        container.setLayout(layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(container)
        scrollArea.setWidgetResizable(True)  
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  

        self.setCentralWidget(scrollArea) 
        
    def updateCharacterCount(self):
        """
        Updates the character counter as the user types in the text box.

        Changes the label colour and message depending on whether
        the input is within the supported QR character limit.
        """

        text = self.textbox.text()
        charCount = len(text)
        maxChars = 17
        
        if charCount == 0:
            self.charCountLabel.setText(f"{charCount}/{maxChars} characters (Version 1 QR Code)")
            self.charCountLabel.setStyleSheet("color: gray; font-size: 10pt;")
        elif charCount <= maxChars:
            self.charCountLabel.setText(f"{charCount}/{maxChars} characters")
            self.charCountLabel.setStyleSheet("color: green; font-size: 10pt;")
        else:
            self.charCountLabel.setText(f"{charCount}/{maxChars} characters - Too long!")
            self.charCountLabel.setStyleSheet("color: red; font-size: 10pt;")
    
    def loadExample(self): 
        """
        Loads an example string into the input field to demonstrate
        QR code generation.
        """

        self.textbox.setText("Scan me!")
        self.statusLabel.setText("Example loaded - click 'Generate QR Code' to create")
        self.statusLabel.setStyleSheet("color: blue;")

    # Alvia created this function
    def updateMode(self):
        """
        Enables or disables manual QR configuration options
        based on the selected encoding mode.
        """

        isManual = self.manualModeRadio.isChecked() # Check if manual mode is enable

        self.versionCombo.setEnabled(isManual)
        self.eccCombo.setEnabled(isManual)

        if not isManual:
            self.versionCombo.setCurrentIndex(0)
            self.eccCombo.setCurrentIndex(0)
    
    def generateQRCode(self): 
        """
        Controls the full QR code generation process.

        This includes input validation, version and error correction
        selection, data encoding, QR matrix construction, masking,
        and final rendering.
        """

        # Get the text entered by the user for QR encoding
        textToEncode = self.textbox.text()
        
        error = validate_text(textToEncode)

        # If validation fails, log the failed attempt and display an error message
        # Nina edited the log event part
        if error:
            self.logger.log_event(
            text_content=textToEncode,
            qr_version=self.version,
            ecc_level=self.level if self.level else 'L',
            mask_pattern=0,
            user_options={"encoding": "ISO-8859-1"},
            success=False
            )
            self.statusLabel.setText(error)
            self.statusLabel.setStyleSheet("color: red;")
            return

        # Stores intermediate QR construction steps for slideshow visualisation
        # (Nadya did this) for QR slideshow support    
        steps = []
        
        def add_step(title, desc, matrix): 
            """
            Individual enhancement. 
            Stores an immutable snapshot of the QR matrix at the current
            construction stage for later slideshow visualisation.
             """
            steps.append({
                "title": title,
                "desc": desc,
                "matrix": np.array(matrix).copy()
            })

        # Determine whether QR settings are selected manually or automatically
        # Alvia modified this section
        #----------------------------------------
        manual = self.manualModeRadio.isChecked()

        versionChoice = self.versionCombo.currentText()
        eccChoice = self.eccCombo.currentText()

        self.version, self.level, self.size = findVersionEcc(manual, versionChoice, eccChoice, textToEncode)
        
        # Reserved matrix tracks areas that must not be overwritten by data bits
        self.reserved = [[False for _ in range(self.size)] for _ in range(self.size)]
        #---------------------------------------------
        
        # Encode input text into data and error correction codewords
        result = self.dataEncoding(textToEncode)
        if result is None:
            return
        
        self.reserved = [[False for _ in range(self.size)] for _ in range(self.size)]
        
        # Generate the standard QR finder pattern
        finderArray = self.getFinder()
        qrCode, size = self.positionFinders(finderArray)

        add_step(
            "Finder patterns",
            "Finder patterns added to the three corners to help scanners detect orientation.",
            qrCode
        )

        # Add separator zones around finder patterns
        qrCode = self.addingSeparators(qrCode, size)
        
        # Alvia modified this
        if (self.version == 2):
            qrCode,self.reserved = placeAlignment(qrCode,(16,16),self.reserved)
        
        qrCode = self.addTiming(qrCode, size) # Add timing patterns to help scanners determine module spacing
        qrCode = self.addDarkModule(qrCode, self.version) # Add the fixed dark module required by the QR standard

        self.reserveFormatAreas(size)
        
        bitString = self.bytesToBits(result)
        
        # Alvia modified this
        if self.version == 2:
            bitString += '0' * 7
        
        qrCode = self.placeDataBits(qrCode, size, bitString)
        
        # ---- MASK SELECTOR ENHANCEMENT (33027025) ----
        # Determine which mask to use based on user selection
        mask_selection = self.maskComboBox.currentIndex()
        
        evaluator = MaskEvaluator()
        
        if mask_selection == 0:  # Auto mode
            maskPattern, qrCode, all_scores = evaluator.find_best_mask(qrCode, self.reserved)
            penalty_report = make_report(all_scores, evaluator.pattern_details)
            print(penalty_report)  # Log to console
            
            mask_info = f"Auto-selected Mask {maskPattern} (Penalty: {all_scores[maskPattern]})"
            self.maskInfoLabel.setText(mask_info)
        else:  # Manual selection
            maskPattern = mask_selection - 1  # Adjust for "Auto" at index 0
            qrCode = evaluator.apply_mask(qrCode, self.reserved, maskPattern)
            penalties = evaluator.calculate_penalty(qrCode)
            
            mask_info = f"Using Mask {maskPattern} (Penalty: {penalties['total']})"
            self.maskInfoLabel.setText(mask_info)
        
        # Generate and place format string
        formatStr = self.generateFormatString(maskPattern)
        qrCode = self.placeFormatString(qrCode, size, formatStr)
        
        preset_name = self.presetCombo.currentData()

        # Apply colour and accessibility preset to the QR code
        coloured_image = render_qr(qrCode, preset_name)

        # Display the final QR code in the application canvas
        self.qrCanvas.displayQR(coloured_image)

        # (33021637) Individual enhancement – launch QR construction slideshow
        if steps:
            QRSlideshow(steps, self).exec_()


        # Update user with successful generation message
        self.statusLabel.setText(
    f"QR Code generated successfully! ({len(textToEncode)} characters)"
)
        self.statusLabel.setStyleSheet("color: green;")

        # Alvia added this
        #-----------------------------------------
        print("-----------------------------------------------")
        print("Version: " + str(self.version))
        print("EC Level: " + str(self.level))
        #----------------
        
        # ---- MASK SELECTOR ENHANCEMENT - Updated logging (33027025) ----
        self.logger.log_event(
        text_content=textToEncode,
        qr_version=self.version,
        ecc_level=self.level,
        mask_pattern=maskPattern,  # Log the actual mask used
        user_options={"encoding": "ISO-8859-1", "mask_selection": self.maskComboBox.currentText()},
        success=True
        )
        
    # Nina edited this for analytics visualisation support to evaluate QR generation behaviour
    # using logged data (ECC frequency and success trends).
    def showAnalytics(self):
        """
        Description:
        Displays analytics visualisations related to QR code generation.

        This method retrieves logged QR generation data and presents
        graphical summaries to help analyse system usage and behaviour.
        The analytics include error correction level frequency and
        generation success trends over time.
        """ 
        # Displays analytics visualisations for QR code generation usage.
        self.logger.plot_ecc_frequency()
        # Display a time-series chart comparing
        # successful and failed QR generation attempts
        self.logger.plot_success_over_time()
        
    def showInformationDialog(self): # Opens the information and help dialog window.
        dialog = InformationUtil(self)
        dialog.exec_()
        
    def dataEncoding(self, textToEncode): # Encodes the input text into QR compatible data
        """
        Encodes input text into QR-compatible binary data and
        applies Reed-Solomon error correction.

        Parameters: textToEncode, The string entered by the user to be encoded.

        Returns: A byte array containing encoded data and error correction codewords, or None if encoding fails.
        """
        versionsCapacity = [[17, 14, 11, 7], [32, 26, 20, 14]]
        binaryString = ""
        targetBits = 0
        ECBytes = 0
        index = -1
        
        modeIndicator = '0100'
        binaryString += modeIndicator
        
        characterIndicator = format(len(textToEncode), '08b')
        binaryString += characterIndicator
        
        try:
            encMode = textToEncode.encode('iso-8859-1')
        except UnicodeEncodeError as e:
            problematicChar = textToEncode[e.start:e.end]
            self.statusLabel.setText(f"Error: Unsupported character '{problematicChar}' found. Please use standard Latin characters only.")
            self.statusLabel.setStyleSheet("color: red;")
            return None
            
        dataString = ''.join(format(byte, '08b') for byte in encMode)
        binaryString += dataString
        
        targetBits, ECBytes, index = findEncodingData(self.version, self.level)  # Alvia modified this
        
        if len(binaryString) > targetBits:
            bitsOver = len(binaryString) - targetBits
            self.statusLabel.setText(f"Error: Version {self.version} with ECC level {self.level} supports {versionsCapacity[self.version-1][index]} characters, you are {len(textToEncode) - versionsCapacity[self.version-1][index]} characters over. So text is too long by {bitsOver} bits.")  # Alvia modified this
            self.statusLabel.setStyleSheet("color: red;")
            return None
        
        bitsShort = targetBits - len(binaryString)
        if bitsShort >= 4:
            binaryString += '0000'
        else:
            binaryString += '0' * bitsShort
        
        if len(binaryString) % 8 != 0:
            paddingToCompleteByte = 8 - (len(binaryString) % 8)
            binaryString += '0' * paddingToCompleteByte
        
        padBytes = [0b11101100, 0b00010001]
        padIndex = 0
        
        while len(binaryString) < targetBits:
            binaryString += format(padBytes[padIndex % 2], '08b')
            padIndex += 1
        
        binaryString = binaryString[:targetBits]
        
        dataBytes = bytes(int(binaryString[i:i+8], 2) for i in range(0, len(binaryString), 8))
        return reedsolo.RSCodec(ECBytes).encode(dataBytes)  # Alvia modified this

    def getFinder(self): 
        """
        Generates the standard 7x7 QR finder pattern.

        Returns: A 2D list representing the finder pattern matrix.
        """
        line1 = [1,1,1,1,1,1,1]
        line2 = [1,0,0,0,0,0,1]
        line3 = [1,0,1,1,1,0,1]
        finderArray = [
            line1,
            line2,
            line3,
            line3,
            line3,
            line2,
            line1
        ]
        return finderArray

    def positionFinders(self, finderArray): 
        """
        Places finder patterns into the required corners of the QR matrix.

        Parameters: finderArray, A 7x7 matrix representing the finder pattern.

        Returns: A tuple containing the QR matrix with finder patterns placed and the matrix size.
        """

        qrSquare = np.zeros((self.size, self.size), dtype=int)
        
        positions = [
            (0, 0),
            (self.size - 7, 0),
            (0, self.size - 7)
        ]

        for pos in positions:
            self.placeFinder(qrSquare, finderArray, pos)
        
        return qrSquare, self.size

    def placeFinder(self, qrSquare, finderArray, pos): 
        """
        Inserts a finder pattern into the QR matrix at a given position.

        Parameters:
            qrSquare: The QR matrix being constructed.
            finderArray: The finder pattern matrix.
            pos: A tuple (x, y) indicating where to place the finder.
        """
        x, y = pos
        for i in range(7):
            for j in range(7):
                qrSquare[y+i][x+j] = finderArray[i][j]
                self.reserved[y+i][x+j] = True

    def addingSeparators(self, qrSquare, size): 
        """
        Adds separator zones around finder patterns to prevent
        interference with data modules.

        Parameters:
            qrSquare: The QR matrix.
            size: The size of the QR matrix.

        Returns: The updated QR matrix.
        """
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

    def addTiming(self, qrSquare, size):
        """
        Adds horizontal and vertical timing patterns to the QR matrix.

        Parameters:
            qrSquare: The QR matrix.
            size: The size of the QR matrix.

        Returns: The updated QR matrix.
        """

        for x in range(8, size - 7):  # Alvia modified this line
            if not self.reserved[6][x]:
                qrSquare[6][x] = 1 - (x % 2)
                self.reserved[6][x] = True

        for y in range(8, size - 7):  # Alvia modified this line
            if not self.reserved[y][6]:
                qrSquare[y][6] = 1 - (y % 2)
                self.reserved[y][6] = True

        return qrSquare

    def addDarkModule(self, qrSquare, version):
        """
        Adds the fixed dark module required by the QR code standard.

        The dark module is placed at a specific position depending
        on the QR version and must always be present.

        Parameters:
            qrSquare: The QR matrix being constructed.
            version: The QR version number.

        Returns: The updated QR matrix.
        """

        darkY = 4 * version + 9
        darkX = 8
        qrSquare[darkY][darkX] = 1
        self.reserved[darkY][darkX] = True
        return qrSquare

    def reserveFormatAreas(self, size):
        """
        Marks matrix positions reserved for format information bits.

        These areas must not be overwritten by data or masking.

        Parameters:
            size: The size of the QR matrix.
        """

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

    def bytesToBits(self, encodedBytes):
        """
        Converts encoded byte data into a binary string.

        Parameters:
            encodedBytes: Byte data containing encoded QR information.

        Returns: A string of binary digits.
        """

        return ''.join(f'{byte:08b}' for byte in encodedBytes)

    def placeDataBits(self, qrSquare, size, bitString):
        """
        Places encoded data bits into the QR matrix using the
        QR zig-zag placement algorithm.

        Parameters:
            qrSquare: The QR matrix.
            size: The size of the QR matrix.
            bitString: Binary string of encoded data bits.

        Returns: The updated QR matrix.
        """
        bitIndex = 0
        x = size - 1 
        upward = True

        while x > 0:
            if x == 6:      
                x -= 1

            col1 = x
            col2 = x - 1

            column_range = range(size - 1, -1, -1) if upward else range(size)

            for y in column_range:
                if not self.reserved[y][col1]:
                    if bitIndex < len(bitString):
                        qrSquare[y][col1] = int(bitString[bitIndex])
                        bitIndex += 1
                if not self.reserved[y][col2]:
                    if bitIndex < len(bitString):
                        qrSquare[y][col2] = int(bitString[bitIndex])
                        bitIndex += 1

            upward = not upward  
            x -= 2              

        return qrSquare

    def generateFormatString(self, maskPattern):
        """
        Generates the QR format string containing error correction
        level and mask pattern information.

        Parameters:
            maskPattern: The selected QR mask pattern.

        Returns: A 15-bit binary string representing the format information.
        """
        ecLevels = {
            'L': 0b01,
            'M': 0b00,
            'Q': 0b11,
            'H': 0b10
        }
        
        ecBits = ecLevels[self.level]  # Alvia modified this line
        formatData = (ecBits << 3) | maskPattern
        
        generator = 0b10100110111
        bchData = formatData << 10
        
        for i in range(4, -1, -1):
            if bchData & (1 << (i + 10)):
                bchData ^= generator << i
        
        formatString = (formatData << 10) | bchData
        
        maskXOR = 0b101010000010010
        formatString ^= maskXOR
        
        return format(formatString, '015b')

    def placeFormatString(self, qrSquare, size, formatString): 
        """
        Places the format string bits into their designated positions
        in the QR matrix.

        Parameters:
            qrSquare: The QR matrix.
            size: The size of the QR matrix.
            formatString: The 15-bit format string.

        Returns: The updated QR matrix.
        """

        bits = list(formatString)
        bitIndex = 0
        
        for x in [0, 1, 2, 3, 4, 5, 7, 8]:
            qrSquare[8][x] = int(bits[bitIndex])
            bitIndex += 1
        
        for y in [7, 5, 4, 3, 2, 1, 0]:
            qrSquare[y][8] = int(bits[bitIndex])
            bitIndex += 1
        
        bitIndex = 0
        
        for y in range(size - 1, size - 8, -1):
            qrSquare[y][8] = int(bits[bitIndex])
            bitIndex += 1
        
        for x in range(size - 8, size):
            if x == 8:
                continue
            qrSquare[8][x] = int(bits[bitIndex])
            bitIndex += 1
        
        return qrSquare

def main(): 
    """
    Entry point of the QR Code Generator application.

    Initialises the Qt application, creates the main window,
    and starts the event loop.
    """
    
    app = QApplication([])
    
    window = MainWindow()
    window.show()
    window.setMinimumSize(640, 800)
    
    app.exec_()

if __name__ == "__main__":
    main()
