import reedsolo
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt

from validate_code import validate_text


class QRCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 6))
        self.axes = self.fig.add_subplot(111)
        self.axes.axis("off")
        super().__init__(self.fig)
        self.setParent(parent)
        
    def displayQR(self, qrCode):
        self.axes.clear()
        self.axes.imshow(qrCode, cmap="binary", interpolation='nearest')
        self.axes.axis("off")
        self.fig.tight_layout()
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QR Code Generator")
        self.version = 1
        self.size = 21
        self.reserved = [[False for _ in range(self.size)] for _ in range(self.size)]
        
        label = QLabel("Enter string to be encoded: ")
        self.textbox = QLineEdit()
        self.textbox.setPlaceholderText("Type your text here...")
        self.textbox.setToolTip("Version 1 QR Code supports up to 17 characters.\nSupported: Letters (A-Z), numbers (0-9), and basic punctuation.\nPress Enter to generate.")
        self.textbox.textChanged.connect(self.updateCharacterCount)
        self.textbox.returnPressed.connect(self.generateQRCode)
        
        self.charCountLabel = QLabel("0/17 characters (Version 1 QR Code)")
        self.charCountLabel.setStyleSheet("color: gray; font-size: 10pt;")
        
        self.generateBtn = QPushButton("Generate QR Code")
        self.generateBtn.clicked.connect(self.generateQRCode)
        
        self.exampleBtn = QPushButton("Try Example")
        self.exampleBtn.clicked.connect(self.loadExample)
        
        self.qrCanvas = QRCanvas(self)
        
        self.statusLabel = QLabel("")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setWordWrap(True)
        
        self.encodingWarning = QLabel("Note: QR codes are encoded using ISO-8859-1. Some phone scanners may display special characters (¡, ñ, etc.) incorrectly as they default to UTF-8 decoding.")
        self.encodingWarning.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        self.encodingWarning.setWordWrap(True)
        self.encodingWarning.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.textbox)
        layout.addWidget(self.charCountLabel)
        layout.addWidget(self.generateBtn)
        layout.addWidget(self.exampleBtn)
        layout.addWidget(self.qrCanvas)
        layout.addWidget(self.statusLabel)
        layout.addWidget(self.encodingWarning)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def updateCharacterCount(self):
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
        self.textbox.setText("Scan me!")
        self.statusLabel.setText("Example loaded - click 'Generate QR Code' to create")
        self.statusLabel.setStyleSheet("color: blue;")
    
    def generateQRCode(self):
        textToEncode = self.textbox.text()
        
        error = validate_text(textToEncode)
        
        if error:
            self.statusLabel.setText(error)
            self.statusLabel.setStyleSheet("color: red;")
            return
        
        self.reserved = [[False for _ in range(self.size)] for _ in range(self.size)]
        
        result = self.dataEncoding(textToEncode)
        if result is None:
            return
        
        finderArray = self.getFinder()
        qrCode, size = self.positionFinders(finderArray)
        
        qrCode = self.addingSeparators(qrCode, size)
        qrCode = self.addTiming(qrCode, size)
        qrCode = self.addDarkModule(qrCode, self.version)
        
        self.reserveFormatAreas(size)
        
        bitString = self.bytesToBits(result)
        
        qrCode = self.placeDataBits(qrCode, size, bitString)
        qrCode = self.Mask0(qrCode, size)
        
        maskPattern = 0
        formatStr = self.generateFormatString(maskPattern, 'L')
        qrCode = self.placeFormatString(qrCode, size, formatStr)
        
        self.qrCanvas.displayQR(qrCode)
        self.statusLabel.setText(f"QR Code generated successfully! ({len(textToEncode)} characters)")
        self.statusLabel.setStyleSheet("color: green;")
        
    def dataEncoding(self, textToEncode):
        binaryString = ""
        
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
        
        targetBits = 152
        
        if len(binaryString) > targetBits:
            bitsOver = len(binaryString) - targetBits
            self.statusLabel.setText(f"Error: Text is too long by {bitsOver} bits. Please use fewer characters.")
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
        return reedsolo.RSCodec(7).encode(dataBytes)

    def getFinder(self):
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
        x, y = pos
        for i in range(7):
            for j in range(7):
                qrSquare[y+i][x+j] = finderArray[i][j]
                self.reserved[y+i][x+j] = True

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

    def addTiming(self, qrSquare, size):
        for x in range(8, size - 8):  
            qrSquare[6][x] = 1 - (x % 2)
            self.reserved[6][x] = True

        for y in range(8, size - 8): 
            qrSquare[y][6] = 1 - (y % 2)
            self.reserved[y][6] = True

        return qrSquare

    def addDarkModule(self, qrSquare, version):
        darkY = 4 * version + 9
        darkX = 8
        qrSquare[darkY][darkX] = 1
        self.reserved[darkY][darkX] = True
        return qrSquare

    def reserveFormatAreas(self, size):
        for x in range(9):
            self.reserved[8][x] = True
        
        for y in range(9):
            if y != 6:
                self.reserved[y][8] = True
        
        for y in range(size - 7, size):
            self.reserved[y][8] = True
        
        for x in range(size - 8, size):
            self.reserved[8][x] = True

    def bytesToBits(self, encodedBytes):
        return ''.join(f'{byte:08b}' for byte in encodedBytes)

    def placeDataBits(self, qrSquare, size, bitString):
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

    def Mask0(self, qrSquare, size):
        for y in range(size):
            for x in range(size):
                if not self.reserved[y][x]:
                    if (y + x) % 2 == 0:
                        qrSquare[y][x] ^= 1
        return qrSquare

    def generateFormatString(self, maskPattern, errorCorrectionLevel='L'):
        ecLevels = {
            'L': 0b01,
            'M': 0b00,
            'Q': 0b11,
            'H': 0b10
        }
        
        ecBits = ecLevels[errorCorrectionLevel]
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
            qrSquare[8][x] = int(bits[bitIndex])
            bitIndex += 1
        
        return qrSquare

def main():
    app = QApplication([])
    
    window = MainWindow()
    window.show()
    window.setMinimumSize(640, 480)
    
    app.exec_()

if __name__ == "__main__":
    main()
