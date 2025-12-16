#!/usr/bin/env python3
"""
File Dialog Helper - Better file save/load dialogs
"""

import os
import pya

class FileDialogHelper:
    """Helper class for file dialogs"""
    
    @staticmethod
    def get_save_filename(parent=None, default_name="project1_markers.json"):
        """Get filename for saving with proper file dialog"""
        try:
            # Try to use QFileDialog for better file selection
            home_dir = os.path.expanduser("~")
            default_path = os.path.join(home_dir, default_name)
            
            # Use KLayout's file dialog
            filename = pya.QFileDialog.getSaveFileName(
                parent,
                "Save FIB Project",
                default_path,
                "JSON Files (*.json);;All Files (*)"
            )
            
            # Handle different return formats
            if isinstance(filename, tuple):
                filename = filename[0] if filename[0] else None
            elif not filename:
                filename = None
            
            if filename:
                # Ensure .json extension
                if not filename.lower().endswith('.json'):
                    filename += '.json'
                
                print(f"[File Dialog] Selected save file: {filename}")
                return filename
            else:
                print("[File Dialog] Save cancelled by user")
                return None
                
        except Exception as e:
            print(f"[File Dialog] Error in save dialog: {e}")
            # Fallback to home directory with default name
            home_dir = os.path.expanduser("~")
            fallback_path = os.path.join(home_dir, default_name)
            print(f"[File Dialog] Using fallback path: {fallback_path}")
            return fallback_path
    
    @staticmethod
    def get_load_filename(parent=None):
        """Get filename for loading with proper file dialog"""
        try:
            # Try to use QFileDialog for better file selection
            home_dir = os.path.expanduser("~")
            
            # Use KLayout's file dialog
            filename = pya.QFileDialog.getOpenFileName(
                parent,
                "Load FIB Project",
                home_dir,
                "JSON Files (*.json);;All Files (*)"
            )
            
            # Handle different return formats
            if isinstance(filename, tuple):
                filename = filename[0] if filename[0] else None
            elif not filename:
                filename = None
            
            if filename and os.path.exists(filename):
                print(f"[File Dialog] Selected load file: {filename}")
                return filename
            elif filename:
                print(f"[File Dialog] File not found: {filename}")
                return None
            else:
                print("[File Dialog] Load cancelled by user")
                return None
                
        except Exception as e:
            print(f"[File Dialog] Error in load dialog: {e}")
            return None
    
    @staticmethod
    def get_writable_path(filename):
        """Ensure the path is writable"""
        try:
            # If absolute path, check if directory is writable
            if os.path.isabs(filename):
                directory = os.path.dirname(filename)
                if os.access(directory, os.W_OK):
                    return filename
                else:
                    print(f"[File Dialog] Directory not writable: {directory}")
            
            # Fallback to home directory
            home_dir = os.path.expanduser("~")
            basename = os.path.basename(filename)
            writable_path = os.path.join(home_dir, basename)
            print(f"[File Dialog] Using writable path: {writable_path}")
            return writable_path
            
        except Exception as e:
            print(f"[File Dialog] Error getting writable path: {e}")
            # Last resort: home directory with default name
            home_dir = os.path.expanduser("~")
            return os.path.join(home_dir, "fib_project.json")
    
    @staticmethod
    def list_recent_files():
        """List recent FIB project files in home directory"""
        try:
            home_dir = os.path.expanduser("~")
            json_files = []
            
            for filename in os.listdir(home_dir):
                if filename.endswith('.json') and ('fib' in filename.lower() or 'marker' in filename.lower()):
                    full_path = os.path.join(home_dir, filename)
                    if os.path.isfile(full_path):
                        # Get file modification time
                        mtime = os.path.getmtime(full_path)
                        json_files.append((filename, full_path, mtime))
            
            # Sort by modification time (newest first)
            json_files.sort(key=lambda x: x[2], reverse=True)
            
            return json_files[:10]  # Return top 10 recent files
            
        except Exception as e:
            print(f"[File Dialog] Error listing recent files: {e}")
            return []