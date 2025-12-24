import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QRadioButton,
    QButtonGroup, QFileDialog,
    QLineEdit, QCheckBox, QFrame,
    QListWidget, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
import json


class TransposePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        label = QLabel("Coordinate Transposition Tool\n(Placeholder)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px;")

        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()


class DebrisPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        presets = QVBoxLayout()
        config = QVBoxLayout()
        file_panel = QVBoxLayout()

        layout.addLayout(presets, 1)
        layout.addLayout(config, 2)
        layout.addLayout(file_panel, 3)

        self.presets_path = "data/presets.json"
        self.presets = {}

        self.build_presets_panel(presets)
        self.build_config(config)
        self.build_file_panel(file_panel)

        self.load_presets_from_disk()

    def build_presets_panel(self, layout):
        title = QLabel("Presets")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        self.preset_list = QListWidget()
        self.preset_list.itemClicked.connect(self.load_selected_preset)
        layout.addWidget(self.preset_list)

        save_btn = QPushButton("Save preset")
        load_btn = QPushButton("Delete preset")

        save_btn.clicked.connect(self.save_preset)
        load_btn.clicked.connect(self.delete_preset)

        layout.addWidget(save_btn)
        layout.addWidget(load_btn)

        layout.addStretch()

    def load_presets_from_disk(self):
        try:
            with open(self.presets_path, "r") as f:
                self.presets = json.load(f)
        except FileNotFoundError:
            self.presets = {}

        self.refresh_preset_list()

    def refresh_preset_list(self):
        self.preset_list.clear()
        for name in self.presets:
            self.preset_list.addItem(name)

    def save_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name:
            return

        self.presets[name] = {
            k: float(v.text()) for k, v in self.inputs.items()
        }

        with open(self.presets_path, "w") as f:
            json.dump(self.presets, f, indent=2)

        self.refresh_preset_list()

    def load_selected_preset(self, item):
        data = self.presets.get(item.text())
        if not data:
            return

        for k, v in data.items():
            if k in self.inputs:
                self.inputs[k].setText(str(v))

    def delete_preset(self):
        item = self.preset_list.currentItem()
        if not item:
            return

        name = item.text()
        del self.presets[name]

        with open(self.presets_path, "w") as f:
            json.dump(self.presets, f, indent=2)

        self.refresh_preset_list()

    def build_config(self, layout):
        defaults = {
            "mass_kg": "",
            "area_m2": "",
            "Cd": "",
            "rho": "",
            "g": "",
            "dt": "",
            "alt_ft_input": "",
            "ktas": "",
            "terrain_ft": "",
            "vz_bounce_min": ""
        }

        title = QLabel("Config")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        self.inputs = {}

        for key, value in defaults.items():
            lbl = QLabel(key)
            edit = QLineEdit()
            edit.setPlaceholderText(key)
            layout.addWidget(lbl)
            layout.addWidget(edit)
            self.inputs[key] = edit

        self.include_ground_drag = QCheckBox("Include ground drag")
        self.include_ground_drag.setChecked(True)
        layout.addWidget(self.include_ground_drag)

        layout.addStretch()

    def build_file_panel(self, layout):
        self.file_label = QLabel("Drop KML file here\nor click to browse")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setFrameShape(QFrame.Shape.Box)
        self.file_label.setMinimumHeight(200)
        self.file_label.setAcceptDrops(True)

        self.file_label.mousePressEvent = self.browse_file
        self.file_label.dragEnterEvent = self.drag_enter
        self.file_label.dropEvent = self.drop_event

        layout.addWidget(self.file_label)

        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.clicked.connect(self.run_simulation)
        layout.addWidget(self.run_btn)

        layout.addStretch()

    def browse_file(self, _):
        file, _ = QFileDialog.getOpenFileName(
            self, "Open KML", "", "KML Files (*.kml)"
        )
        if file:
            self.kml_input_path = file
            self.file_label.setText(file)

    def drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.kml_input_path = urls[0].toLocalFile()
            self.file_label.setText(self.kml_input_path)

    def run_simulation(self):
        if not hasattr(self, "kml_input_path"):
            QMessageBox.warning(self, "Missing input", "Please load a KML file first.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save output KML",
            "debris_trajectory.kml",
            "KML Files (*.kml)"
        )
        if not save_path:
            return

        config = {k: float(v.text()) for k, v in self.inputs.items()}
        config["include_ground_drag"] = self.include_ground_drag.isChecked()

        self.run_debris_calculator(
            input_kml=self.kml_input_path,
            output_kml=save_path,
            config=config
        )

        QMessageBox.information(self, "Complete", "Debris trajectory KML saved.")

    def run_debris_calculator(self, input_kml, output_kml, config):
        """
        Hook point for Debris_Trajectory_Calculator.py

        input_kml   : path to source aircraft route KML
        output_kml  : path to write debris trajectory KML
        config      : dict of all numeric + boolean parameters
        """

        # Example:
        # from Debris_Trajectory_Calculator import run
        # run(input_kml, output_kml, config)

        print("INPUT:", input_kml)
        print("OUTPUT:", output_kml)
        print("CONFIG:", config)


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Farnborough Tools")
        self.resize(900, 500)
        central = QWidget()
        self.setCentralWidget(central)

        self.root_layout = QVBoxLayout(central)

        self.build_mode_selector()

        self.container = QFrame()
        self.container_layout = QVBoxLayout(self.container)
        self.root_layout.addWidget(self.container)

        self.transpose_page = TransposePage()
        self.debris_page = DebrisPage()

        self.set_page(self.transpose_page)

    # ---------- MODE SELECTOR ----------
    def build_mode_selector(self):
        bar = QHBoxLayout()

        self.mode_group = QButtonGroup(self)

        self.rb_transpose = QRadioButton("Transpose to Farnborough")
        self.rb_debris = QRadioButton("Debris Trajectory")

        self.rb_transpose.setChecked(True)

        self.mode_group.addButton(self.rb_transpose)
        self.mode_group.addButton(self.rb_debris)

        self.rb_transpose.toggled.connect(self.switch_mode)

        bar.addWidget(self.rb_transpose)
        bar.addWidget(self.rb_debris)
        bar.addStretch()

        self.root_layout.addLayout(bar)

    def set_page(self, widget):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        self.container_layout.addWidget(widget)

    def switch_mode(self):
        if self.rb_transpose.isChecked():
            self.set_page(self.transpose_page)
        else:
            self.set_page(self.debris_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())