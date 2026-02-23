## Student ID: 330270255

**Branch name:** 33027025_enhancement

**Individually created module(s):** qr_mask_selector.py, modifications to QrGeneration.py stated in comments

**Link to merge of individual branch to main:** https://csgitlab.reading.ac.uk/ac004435/a20/-/blob/main/QrGeneration.py

**Key function/method(s):** find_best_mask(), apply_mask(), calculate_penalty(), penalty_rule_1(), penalty_rule_2(), penalty_rule_3(), penalty_rule_4()

**Designed to:** Evaluate all 8 QR mask patterns using the 4 penalty scoring rules from the QR specification and automatically select the optimal mask pattern. Users can  manually override and select a specific mask pattern via dropdown menu.  

**Dependencies:** MaskEvaluator class and make_report function are imported into QrGeneration.py. Uses Python's standard library "copy" module for deep copying matrices. Integrates with existing QRLogger for logging mask selection.  

**Not robust to:** The implementation assumes square QR matrices and correctly formatted reserved areas. Performance may degrade for large QR codes due to nested loops in penalty calculations.

----

#### Design Process and Integration

 I used the Thonky QR tutorial to understand how masking improves scan reliability by breaking up large areas of uniform color. Each mask follows a fixed formula and is scored using four penalty rules.

• Rule 1 checks long runs of the same color
• Rule 2 detects 2x2 blocks
• Rule 3 identifies finder-like patterns
• Rule 4 evaluates overall dark to light balance

![maskPatternSelection](/uploads/9036037293722acc07257936b3066e26/maskPatternSelection.png)

Dropdown menu where user can pick which mask pattern they would like to use.

![userInstructions](/uploads/911bdaaaa5e58cd9b0c144f559b479cb/user_instructions.png)

Updated the Information Utility to include instructions for picking masking pattern.

#### Integration Example

```
evaluator = MaskEvaluator()

if mask_selection == 0:  # Auto mode
    maskPattern, qrCode, all_scores = evaluator.find_best_mask(qrCode, self.reserved)
    penalty_report = make_report(all_scores, evaluator.pattern_details)
    print(penalty_report)
else:  # Manual selection
    maskPattern = mask_selection - 1
    qrCode = evaluator.apply_mask(qrCode, self.reserved, maskPattern)
```
The evaluator receives the QR matrix after data placement. In auto mode, it tests all 8 masks and returns the best one. In manual mode, it applies the user's choice. The mask number then generates the correct format string.

#### Most Important Function

##### Function: find_best_mask(qr_matrix, reserved)

Expected Input/Output/Action: Takes an unmasked QR matrix and reserved areas array, evaluates all 8 masks with penalty scoring, and returns the optimal mask number, masked matrix, and all penalty scores.

```
evaluator = MaskEvaluator()
best_mask, masked_qr, all_scores = evaluator.find_best_mask(my_qr_matrix, reserved_cells)
# best_mask: 0-7, masked_qr: processed matrix, all_scores: {0: 245, 1: 198, ...}
```

#### Idiomatic Python Code Snippet

```
def count_run_penalty(self, line):
    if len(line) == 0:
        return 0
        
    penalty = 0
    current_value = line[0]
    run_count = 1
    
    for i in range(1, len(line)):
        if line[i] == current_value:
            run_count += 1
        else:
            if run_count >= 5:
                penalty += 3 + (run_count - 5)
            current_value = line[i]
            run_count = 1
    
    if run_count >= 5:
        penalty += 3 + (run_count - 5)
    
    return penalty
```

This shows good Python style by using for with range() instead of C-style while loops, descriptive variable names, early return for edge cases, and single-purpose functionality. I could have used recursion or while loops, but straightforward iteration is more Pythonic and easier to debug.

#### Development Challenges

Penalty Rule 3 was the most challenging. The 1:1:3:1:1 ratio refers to specific bit patterns such as 10111010000 and 00001011101. An early version mutated the original matrix during mask testing, causing masks to stack incorrectly. Using copy.deepcopy() resolved this issue. Integration also exposed numpy truth value errors, since QrGeneration uses numpy arrays. I detected arrays with hasattr() and converted them to lists without adding a numpy dependency.

If revising, I would write unit tests for each penalty rule first, validate data types earlier, and study the QR specification more carefully upfront.

#### Functionality Demonstration
![maskFunctionality](/uploads/61c9ac87adcbf96a76f9c4569f63179e/maskFunctionality.png)

This image shows the generated QR codes for the word "known" using the masking patterns auto, 0-7. The encoding mode was set to version 1 Level L.
