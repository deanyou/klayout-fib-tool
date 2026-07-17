#!/usr/bin/env python3
"""
Smart Counter - Intelligent marker numbering system
Automatically finds the next available number for each marker type
"""

from .core.logging_utils import safe_print as print
from .business.marker_codec import (
    marker_id_number,
    marker_id_to_type,
    marker_type_name,
)

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
                try:
                    if marker_id_to_type(marker_id) != marker_type:
                        continue
                    number = marker_id_number(marker_id)
                except (TypeError, ValueError):
                    continue
                existing_numbers.add(number)
                print(f"[Smart Counter] Found existing {marker_type} number: {number} (ID: {marker_id})")
            
        except Exception as e:
            print(f"[Smart Counter] Error parsing existing numbers: {e}")
        
        return existing_numbers
    
    def get_fallback_counter(self, marker_type):
        """Read the counter from the panel's shared runtime state."""
        return self.panel.state.marker_counters.get(marker_type, 0)
    
    def update_global_counter(self, marker_type, number):
        """Advance the shared counter without moving it backwards."""
        counters = self.panel.state.marker_counters
        counters[marker_type] = max(counters.get(marker_type, 0), number + 1)
        print(f"[Smart Counter] Updated global {marker_type} counter to: {counters[marker_type]}")
    
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
                try:
                    marker_type = marker_type_name(marker).replace('multipoint_', '')
                    if marker_id_to_type(marker_id) != marker_type:
                        continue
                    number = marker_id_number(marker_id)
                except (TypeError, ValueError):
                    continue

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
