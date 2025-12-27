from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QTextBrowser, QPushButton


class InformationUtil(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Information & Help")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Tab 1: Information Modeling
        modelingTab = QTextBrowser()
        modelingTab.setHtml("""
            <h2>How Information is Modeled</h2>
            
            <h3>QR Code Structure</h3>
            <p>This generator creates <b>Version 1 QR codes</b>, which consist of a 21×21 module (pixel) grid. 
            Each module is either black (1) or white (0), encoding your data in a machine-readable format.</p>
            
            <h3>Data Encoding Process</h3>
            <ol>
                <li><b>Mode Indicator (4 bits):</b> Specifies the encoding mode. This generator uses byte mode (0100).</li>
                <li><b>Character Count Indicator (8 bits):</b> Stores the number of characters in your message.</li>
                <li><b>Data Encoding:</b> Each character is converted to binary using ISO-8859-1 encoding, 
                    where each character becomes 8 bits.</li>
                <li><b>Terminator (up to 4 bits):</b> Adds '0000' to signal the end of data.</li>
                <li><b>Padding:</b> Extra '0' bits are added to make the length a multiple of 8, followed by 
                    alternating pad bytes (11101100, 00010001) until we reach exactly 152 bits (19 bytes).</li>
            </ol>
            
            <h3>Error Correction</h3>
            <p>The system uses <b>Reed-Solomon error correction</b> with Level L (Low), which adds 7 error correction 
            codewords to the 19 data bytes. This allows the QR code to be successfully scanned even if up to 7% 
            of it is damaged or obscured.</p>
            
            <h3>Masking</h3>
            <p>A mask pattern (Mask 0) is applied using XOR operations where (row + column) % 2 == 0. 
            This breaks up patterns that might confuse scanners and improves readability.</p>
            
            <h3>Format String</h3>
            <p>A 15-bit format string is embedded around the finder patterns, containing:
            <ul>
                <li>Error correction level (2 bits)</li>
                <li>Mask pattern identifier (3 bits)</li>
                <li>BCH error correction for the format string itself (10 bits)</li>
            </ul>
            This helps scanners correctly interpret the QR code.</p>
        """)
        
        # Tab 2: Input Management
        inputTab = QTextBrowser()
        inputTab.setHtml("""
            <h2>User Input Management</h2>
            
            <h3>Character Limit</h3>
            <p>Version 1 QR codes support a <b>maximum of 17 characters</b> when using byte mode encoding. 
            The character counter updates in real-time:</p>
            <ul>
                <li><span style="color: gray;">Gray:</span> No input yet</li>
                <li><span style="color: green;">Green:</span> Valid length (1-17 characters)</li>
                <li><span style="color: red;">Red:</span> Too long (over 17 characters)</li>
            </ul>
            
            <h3>Encoding Scheme</h3>
            <p>Text is encoded using <b>ISO-8859-1</b> character encoding. This standard supports:</p>
            <ul>
                <li>Basic Latin alphabet (A-Z, a-z)</li>
                <li>Numbers (0-9)</li>
                <li>Common punctuation and symbols</li>
                <li>Extended Latin characters (é, ñ, ü, etc.)</li>
            </ul>
            
            <h3>Scanner Compatibility Note</h3>
            <p><b>Important:</b> While this generator uses ISO-8859-1 encoding, many phone QR scanners default to 
            UTF-8 decoding. This means special characters (¡, ñ, etc.) may display incorrectly when scanned. 
            For maximum compatibility, stick to basic ASCII characters (A-Z, a-z, 0-9) and common punctuation.</p>
            
            <h3>Real-Time Feedback</h3>
            <p>The interface provides immediate feedback as you type:
            <ul>
                <li>Character count updates with each keystroke</li>
                <li>Visual color coding indicates input validity</li>
                <li>Tooltip guidance on character limits</li>
                <li>Status messages explain any errors</li>
            </ul>
            </p>
        """)
        
        # Tab 3: Data Integrity & Security
        securityTab = QTextBrowser()
        securityTab.setHtml("""
            <h2>Data Integrity & Security</h2>
            
            <h3>Error Handling</h3>
            <p>The system validates all input before generating QR codes:</p>
            <ul>
                <li><b>Empty input:</b> Prevents generation of meaningless QR codes</li>
                <li><b>Length validation:</b> Rejects text exceeding 17 characters</li>
                <li><b>Character validation:</b> Checks for unsupported characters before encoding</li>
                <li><b>Encoding verification:</b> Ensures all characters can be represented in ISO-8859-1</li>
            </ul>
            <p>Clear error messages guide you to fix any issues before generation.</p>
            
            <h3>Input Sanitization</h3>
            <p>The generator validates text through multiple stages:
            <ol>
                <li>Length check against Version 1 capacity</li>
                <li>Character encoding validation</li>
                <li>Binary string generation with overflow protection</li>
            </ol>
            Invalid input is rejected with specific error messages rather than creating malformed QR codes.</p>
            
            <h3>Built-in Error Correction</h3>
            <p>Reed-Solomon error correction (Level L) allows QR codes to remain scannable even with:
            <ul>
                <li>Up to 7% damage or dirt</li>
                <li>Poor lighting conditions</li>
                <li>Slight printing imperfections</li>
                <li>Camera focus issues</li>
            </ul>
            This ensures data integrity from generation through scanning.</p>
            
            <h3>Security Warnings & Best Practices</h3>
            <p><b> QR Code Security Risks:</b></p>
            <ul>
                <li><b>Phishing Attacks:</b> Malicious QR codes can link to fake websites that steal credentials</li>
                <li><b>Malware Distribution:</b> QR codes may direct to sites that download harmful software</li>
                <li><b>Privacy Concerns:</b> QR codes can contain tracking URLs that monitor your activity</li>
                <li><b>Social Engineering:</b> Attackers may place fake QR codes over legitimate ones</li>
            </ul>
            
            <p><b> Safe QR Code Practices:</b></p>
            <ul>
                <li>Always verify the source before scanning any QR code</li>
                <li>Use a scanner app that previews URLs before opening them</li>
                <li>Be cautious of QR codes in public spaces or from unknown sources</li>
                <li>Never encode sensitive information (passwords, credit cards, personal data)</li>
                <li>Verify the destination URL matches the expected website</li>
                <li>Avoid scanning QR codes that promise prizes or urgent actions</li>
            </ul>
            
            <p><b>Data Protection:</b> This generator runs entirely locally - no data is transmitted to external 
            servers. Your text is encoded directly into the QR code without being stored or shared.</p>
        """)
        
        # Tab 4: User Instructions
        instructionsTab = QTextBrowser()
        instructionsTab.setHtml("""
            <h2>User Instructions</h2>
            
            <h3>How to Generate a QR Code</h3>
            <ol>
                <li>Enter your text in the input field (maximum 17 characters)</li>
                <li>Watch the character counter to ensure you're within limits</li>
                <li>Click "Generate QR Code" or press Enter</li>
                <li>The QR code will appear below if generation is successful</li>
                <li>Use your phone's camera or QR scanner app to test it</li>
            </ol>
            
            <h3>Tips for Good QR Codes</h3>
            <ul>
                <li><b>Keep it short:</b> Shorter messages encode more reliably</li>
                <li><b>Use simple characters:</b> Stick to A-Z, 0-9, and basic punctuation for best compatibility</li>
                <li><b>Test before using:</b> Always scan your QR code with a phone to verify it works</li>
                <li><b>Print clearly:</b> Ensure adequate contrast (black on white) when printing</li>
                <li><b>Size matters:</b> Print large enough for easy scanning (at least 2cm × 2cm)</li>
            </ul>
            
            <h3>Testing Your QR Code</h3>
            <p>To test the generated QR code:</p>
            <ol>
                <li>Open your phone's camera app or a dedicated QR scanner</li>
                <li>Point it at the QR code on your screen</li>
                <li>The text should appear within 1-2 seconds</li>
                <li>If it doesn't scan, try adjusting screen brightness or distance</li>
            </ol>
            
            <h3>Common Issues & Solutions</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f0f0f0;">
                    <th>Issue</th>
                    <th>Solution</th>
                </tr>
                <tr>
                    <td>"Text is too long" error</td>
                    <td>Reduce your message to 17 characters or less</td>
                </tr>
                <tr>
                    <td>"Unsupported character" error</td>
                    <td>Remove special characters; use basic Latin letters and numbers</td>
                </tr>
                <tr>
                    <td>QR code won't scan</td>
                    <td>Increase screen brightness, adjust distance, or try a different scanner app</td>
                </tr>
                <tr>
                    <td>Wrong characters appear when scanned</td>
                    <td>Scanner is using UTF-8 decoding - avoid special characters (é, ñ, ©, etc.)</td>
                </tr>
                <tr>
                    <td>QR code looks correct but doesn't scan</td>
                    <td>Ensure adequate size and contrast; try taking a screenshot and scanning that</td>
                </tr>
            </table>
            
            <h3>Example Use Cases</h3>
            <ul>
                <li>WiFi passwords (e.g., "MyWiFi2024")</li>
                <li>Short messages (e.g., "Call me!")</li>
                <li>Simple identifiers (e.g., "Table 5")</li>
                <li>Quick notes (e.g., "Check email")</li>
            </ul>
            
            <p><b>Note:</b> For URLs, phone numbers, or longer content, you'll need a higher version QR code 
            generator that supports more data capacity.</p>
        """)
        
        # Add tabs
        tabs.addTab(modelingTab, "Information Modeling")
        tabs.addTab(inputTab, "Input Management")
        tabs.addTab(securityTab, "Data Integrity & Security")
        tabs.addTab(instructionsTab, "User Instructions")
        
        # Close button
        closeBtn = QPushButton("Close")
        closeBtn.clicked.connect(self.accept)
        
        layout.addWidget(tabs)
        layout.addWidget(closeBtn)
        
        self.setLayout(layout)
