"""
FIB Tool UI

Simple Qt dialog. Three buttons, one list. No fancy layouts.
"""

import pya


class FIBToolDialog(pya.QDialog):
    """Main FIB Tool dialog window"""
    
    def __init__(self, parent, plugin):
        # Don't pass parent to avoid type issues
        super().__init__()
        self.plugin = plugin
        self.setWindowTitle("FIB Tool")
        self.resize(300, 500)
        
        # Main layout
        layout = pya.QVBoxLayout(self)
        
        # Operation buttons
        btn_layout = pya.QHBoxLayout()
        
        self.btn_cut = pya.QPushButton("Cut")
        self.btn_cut.clicked(self._on_cut_clicked)
        btn_layout.addWidget(self.btn_cut)
        
        self.btn_connect = pya.QPushButton("Connect")
        self.btn_connect.clicked(self._on_connect_clicked)
        btn_layout.addWidget(self.btn_connect)
        
        self.btn_probe = pya.QPushButton("Probe")
        self.btn_probe.clicked(self._on_probe_clicked)
        btn_layout.addWidget(self.btn_probe)
        
        layout.addLayout(btn_layout)
        
        # Marker list
        list_label = pya.QLabel("Markers:")
        layout.addWidget(list_label)
        
        self.marker_list = pya.QListWidget()
        self.marker_list.itemClicked(self._on_marker_selected)
        layout.addWidget(self.marker_list)
        
        # Action buttons
        action_layout = pya.QHBoxLayout()
        
        self.btn_delete = pya.QPushButton("Delete")
        self.btn_delete.clicked(self._on_delete_clicked)
        self.btn_delete.setEnabled(False)
        action_layout.addWidget(self.btn_delete)
        
        self.btn_save = pya.QPushButton("Save")
        self.btn_save.clicked(self._on_save_clicked)
        action_layout.addWidget(self.btn_save)
        
        self.btn_load = pya.QPushButton("Load")
        self.btn_load.clicked(self._on_load_clicked)
        action_layout.addWidget(self.btn_load)
        
        layout.addLayout(action_layout)
        
        # Report button
        self.btn_report = pya.QPushButton("Generate Report")
        self.btn_report.clicked(self._on_report_clicked)
        layout.addWidget(self.btn_report)
        
        # Status label
        self.status_label = pya.QLabel("Ready")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def _on_cut_clicked(self):
        """Activate cut mode"""
        self.status_label.setText("Creating CUT marker - please enter coordinates...")
        
        # For MVP, use simple input dialogs instead of mouse events
        # This avoids the PluginFactory complexity
        try:
            x = pya.QInputDialog.getDouble(self, "CUT Marker", "Enter X coordinate (um):", 0, -10000, 10000, 3)
            if not x[1]:  # User cancelled
                self.status_label.setText("Cancelled")
                return
            
            y = pya.QInputDialog.getDouble(self, "CUT Marker", "Enter Y coordinate (um):", 0, -10000, 10000, 3)
            if not y[1]:
                self.status_label.setText("Cancelled")
                return
            
            directions = ["up", "down", "left", "right"]
            direction = pya.QInputDialog.getItem(self, "CUT Marker", "Select direction:", directions, 0, False)
            if not direction[1]:
                self.status_label.setText("Cancelled")
                return
            
            # Create marker
            self.plugin.create_cut_marker(x[0], y[0], direction[0])
            self.refresh_marker_list()
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
        
        self._update_button_states(None)
    
    def _on_connect_clicked(self):
        """Activate connect mode"""
        self.status_label.setText("Creating CONNECT marker - please enter coordinates...")
        
        try:
            x1 = pya.QInputDialog.getDouble(self, "CONNECT Marker", "Enter start X coordinate (um):", 0, -10000, 10000, 3)
            if not x1[1]:
                self.status_label.setText("Cancelled")
                return
            
            y1 = pya.QInputDialog.getDouble(self, "CONNECT Marker", "Enter start Y coordinate (um):", 0, -10000, 10000, 3)
            if not y1[1]:
                self.status_label.setText("Cancelled")
                return
            
            x2 = pya.QInputDialog.getDouble(self, "CONNECT Marker", "Enter end X coordinate (um):", 0, -10000, 10000, 3)
            if not x2[1]:
                self.status_label.setText("Cancelled")
                return
            
            y2 = pya.QInputDialog.getDouble(self, "CONNECT Marker", "Enter end Y coordinate (um):", 0, -10000, 10000, 3)
            if not y2[1]:
                self.status_label.setText("Cancelled")
                return
            
            # Create marker
            self.plugin.create_connect_marker(x1[0], y1[0], x2[0], y2[0])
            self.refresh_marker_list()
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
        
        self._update_button_states(None)
    
    def _on_probe_clicked(self):
        """Activate probe mode"""
        self.status_label.setText("Creating PROBE marker - please enter coordinates...")
        
        try:
            x = pya.QInputDialog.getDouble(self, "PROBE Marker", "Enter X coordinate (um):", 0, -10000, 10000, 3)
            if not x[1]:
                self.status_label.setText("Cancelled")
                return
            
            y = pya.QInputDialog.getDouble(self, "PROBE Marker", "Enter Y coordinate (um):", 0, -10000, 10000, 3)
            if not y[1]:
                self.status_label.setText("Cancelled")
                return
            
            # Create marker
            self.plugin.create_probe_marker(x[0], y[0])
            self.refresh_marker_list()
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
        
        self._update_button_states(None)
    
    def _update_button_states(self, active_mode):
        """Highlight active button"""
        self.btn_cut.setStyleSheet("" if active_mode != 'cut' else "background-color: #4CAF50; color: white;")
        self.btn_connect.setStyleSheet("" if active_mode != 'connect' else "background-color: #4CAF50; color: white;")
        self.btn_probe.setStyleSheet("" if active_mode != 'probe' else "background-color: #4CAF50; color: white;")
    
    def _on_marker_selected(self, item):
        """Enable delete button when marker is selected"""
        self.btn_delete.setEnabled(True)
    
    def _on_delete_clicked(self):
        """Delete selected marker"""
        current_item = self.marker_list.currentItem()
        if current_item:
            marker_id = current_item.text()
            self.plugin.delete_marker(marker_id)
            self.refresh_marker_list()
            self.status_label.setText(f"Deleted {marker_id}")
    
    def _on_save_clicked(self):
        """Save markers to XML file"""
        filename = pya.QFileDialog.getSaveFileName(self, "Save FIB Data", "", "XML Files (*.xml)")
        if filename:
            success = self.plugin.save_markers(filename)
            if success:
                self.status_label.setText(f"Saved to {filename}")
            else:
                self.status_label.setText("Error saving file")
    
    def _on_load_clicked(self):
        """Load markers from XML file"""
        filename = pya.QFileDialog.getOpenFileName(self, "Load FIB Data", "", "XML Files (*.xml)")
        if filename:
            success = self.plugin.load_markers(filename)
            if success:
                self.refresh_marker_list()
                self.status_label.setText(f"Loaded from {filename}")
            else:
                self.status_label.setText("Error loading file")
    
    def _on_report_clicked(self):
        """Generate HTML report"""
        filename = pya.QFileDialog.getSaveFileName(self, "Generate Report", "", "HTML Files (*.html)")
        if filename:
            success = self.plugin.generate_report(filename)
            if success:
                self.status_label.setText(f"Report generated: {filename}")
            else:
                self.status_label.setText("Error generating report")
    
    def refresh_marker_list(self):
        """Update marker list display"""
        self.marker_list.clear()
        for marker in self.plugin.markers:
            self.marker_list.addItem(marker.id)
        self.btn_delete.setEnabled(False)
    
    def add_marker(self, marker):
        """Add marker to list"""
        self.marker_list.addItem(marker.id)
        self.status_label.setText(f"Added {marker.id}")
