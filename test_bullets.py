#!/usr/bin/env python3

import re

def test_bullet_detection():
    """Test bullet point detection."""
    test_lines = [
        "●​",
        "●​Programming Languages: C, C++,",
        "JAVA, JavaScript, PHP, Dart",
        "●​Web Technologies: HTML, CSS, Laravel",
        "●​Databases: SQL, Oracle, Microsoft Access",
        "●​Systems and Networks: OSI Model,",
        "Cisco, Packet Tracer",
        "●​Software and Tools: MATLAB, Arduino",
        "IDE",
        "●​System Commands: CMD in Linux and",
        "Windows"
    ]
    
    print("=== TESTING BULLET DETECTION ===")
    
    for line in test_lines:
        print(f"Line: '{line}'")
        
        # Test the regex pattern
        if re.match(r'^[●○•\-\*]\s*', line):
            print(f"  -> BULLET DETECTED")
            content = re.sub(r'^[●○•\-\*]\s*', '', line)
            print(f"  -> Content: '{content}'")
        else:
            print(f"  -> NO BULLET")
        
        print()

if __name__ == "__main__":
    test_bullet_detection()
