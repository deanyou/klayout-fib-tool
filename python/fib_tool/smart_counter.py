#!/usr/bin/env python3
"""
Smart Counter - Intelligent marker numbering system
Automatically finds the next available number for each marker type
"""

import re

class SmartCounter:
    """Smart counter that finds the next available number for each marker type"""
    
    def __init__(self, panel):
        self.panel = panel
    
    def get_next_number(self, marker_type):
        """Get the next available number for the given marker type"""
        try:
            # Get all existing markers of this type
            existing_numbers = self.get_existing_numbers(marker_type)
            
            # Find the smallest available number starting from 0
            next_number = 0
            while next_number in existing_numbers:
                next_number += 1
            
            print(f"[Smart Counter] Next {marker_type.upper()} number: {next_number} (existing: {sorted(existing_numbers)})")
            return next_number
            
        except Exception as e:
            print(f"[Smart Counter] Error getting next number: {e}")
            # Fallback to simple counter
            return self.get_fallback_counter(marker_type)
    
    def get_existing_numbers(self, marker_type):
        """Get all existing numbers for the given marker type"""
        existing_numbers = set()
        
        try:
            # Check all markers in the panel
            for marker in self.panel.markers_list:
                marker_id = marker.id
                
                # Extract number from marker ID using regex
                # Pattern: TYPE_NUMBER or TYPE_NUMBER_LAYER_INFO
                pattern = f"^{marker_type.upper()}_(\d+)"
                match = re.match(pattern, marker_id)
                
                if match:
                    number = int(match.group(1))
                    existing_numbers.add(number)
                    print(f"[Smart Counter] Found existing {marker_type} number: {number} (ID: {marker_id})")
            
        except Exception as e:
            print(f"[Smart Counter] Error parsing existing numbers: {e}")
        
        return existing_numbers
    
    def get_fallback_counter(self, marker_type):
        """Fallback counter using global marker_counter"""
        try:
            import sys
            if 'marker_counter' in sys.modules['__main__'].__dict__:
                global_counter = sys.modules['__main__'].__dict__['marker_counter']
                return global_counter.get(marker_type, 0)
            else:
                return 0
        except (KeyError, AttributeError) as e:
            print(f"[Smart Counter] Fallback counter error: {e}")
            return 0
    
    def update_global_counter(self, marker_type, number):
        """Update the global counter to be at least the given number + 1"""
        try:
            import sys
            if 'marker_counter' in sys.modules['__main__'].__dict__:
                global_counter = sys.modules['__main__'].__dict__['marker_counter']
                # Set counter to be at least number + 1
                global_counter[marker_type] = max(global_counter.get(marker_type, 0), number + 1)
                print(f"[Smart Counter] Updated global {marker_type} counter to: {global_counter[marker_type]}")
        except Exception as e:
            print(f"[Smart Counter] Error updating global counter: {e}")
    
    def reset_counters(self):
        """Reset all counters to start from existing markers"""
        try:
            for marker_type in ['cut', 'connect', 'probe']:
                existing_numbers = self.get_existing_numbers(marker_type)
                if existing_numbers:
                    max_number = max(existing_numbers)
                    self.update_global_counter(marker_type, max_number)
                else:
                    self.update_global_counter(marker_type, -1)  # Will become 0
            
            print("[Smart Counter] All counters reset based on existing markers")
            
        except Exception as e:
            print(f"[Smart Counter] Error resetting counters: {e}")
    
    def get_marker_info(self):
        """Get information about all existing markers"""
        info = {
            'cut': [],
            'connect': [],
            'probe': []
        }
        
        try:
            for marker in self.panel.markers_list:
                marker_id = marker.id
                
                # Determine marker type from class name
                marker_class = marker.__class__.__name__.lower()
                if 'cut' in marker_class:
                    marker_type = 'cut'
                elif 'connect' in marker_class:
                    marker_type = 'connect'
                elif 'probe' in marker_class:
                    marker_type = 'probe'
                else:
                    continue
                
                # Extract number
                pattern = f"^{marker_type.upper()}_(\d+)"
                match = re.match(pattern, marker_id)
                
                if match:
                    number = int(match.group(1))
                    info[marker_type].append({
                        'id': marker_id,
                        'number': number,
                        'marker': marker
                    })
            
            # Sort by number
            for marker_type in info:
                info[marker_type].sort(key=lambda x: x['number'])
            
        except Exception as e:
            print(f"[Smart Counter] Error getting marker info: {e}")
        
        return info