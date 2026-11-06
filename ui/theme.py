"""Modern, professional Dark and Light themes with clean typography and polished widgets."""

DARK_THEME_QSS = """
QMainWindow, QDialog, QWidget#centralWidget {
    background-color: #121316;
    color: #E2E8F0;
    font-family: 'Segoe UI', 'SF Pro Text', -apple-system, sans-serif;
    font-size: 13px;
}

/* Sidebar Navigation */
QFrame#sidebar {
    background-color: #1A1C23;
    border-right: 1px solid #282C37;
    min-width: 210px;
    max-width: 210px;
}

QLabel#appTitle {
    color: #38BDF8;
    font-size: 16px;
    font-weight: 700;
    padding: 18px 12px 10px 14px;
}

QLabel#appSubtitle {
    color: #64748B;
    font-size: 11px;
    padding-left: 14px;
    padding-bottom: 16px;
}

QPushButton.navBtn {
    text-align: left;
    padding: 11px 18px;
    border-radius: 8px;
    border: none;
    color: #94A3B8;
    font-size: 13px;
    font-weight: 500;
    margin: 3px 10px;
    background-color: transparent;
}

QPushButton.navBtn:hover {
    background-color: #242936;
    color: #F8FAFC;
}

QPushButton.navBtn:checked {
    background-color: #0284C7;
    color: #FFFFFF;
    font-weight: 600;
}

/* Header & Status Bar */
QFrame#topBar {
    background-color: #16181F;
    border-bottom: 1px solid #282C37;
    padding: 8px 16px;
}

QFrame#statusBar {
    background-color: #16181F;
    border-top: 1px solid #282C37;
    padding: 6px 16px;
}

/* Cards & Content Areas */
QFrame.card {
    background-color: #1A1C23;
    border: 1px solid #282C37;
    border-radius: 10px;
    padding: 16px;
}

QFrame.metricCard {
    background-color: #1E222D;
    border: 1px solid #2D3342;
    border-radius: 10px;
    padding: 14px;
}

QLabel.metricTitle {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel.metricValue {
    color: #F8FAFC;
    font-size: 20px;
    font-weight: 700;
    margin-top: 4px;
}

/* Action Buttons */
QPushButton.primaryBtn {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 18px;
}

QPushButton.primaryBtn:hover {
    background-color: #0369A1;
}

QPushButton.secondaryBtn {
    background-color: #2D3342;
    color: #E2E8F0;
    border: 1px solid #3F475A;
    border-radius: 7px;
    font-weight: 500;
    font-size: 13px;
    padding: 9px 16px;
}

QPushButton.secondaryBtn:hover {
    background-color: #384154;
}

QPushButton.dangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 16px;
}

QPushButton.dangerBtn:hover {
    background-color: #B91C1C;
}

/* Form Controls */
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #1E222D;
    color: #F8FAFC;
    border: 1px solid #384154;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #38BDF8;
}

QComboBox QAbstractItemView {
    background-color: #1E222D;
    color: #F8FAFC;
    selection-background-color: #0284C7;
    border: 1px solid #384154;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: #2D3342;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0284C7;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #38BDF8;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #7DD3FC;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #E2E8F0;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #1E222D;
}

QCheckBox::indicator:checked {
    background-color: #0284C7;
    border-color: #38BDF8;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #16181F;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""

LIGHT_THEME_QSS = """
QMainWindow, QDialog, QWidget#centralWidget {
    background-color: #F8FAFC;
    color: #1E293B;
    font-family: 'Segoe UI', 'SF Pro Text', -apple-system, sans-serif;
    font-size: 13px;
}

QFrame#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
    min-width: 210px;
    max-width: 210px;
}

QLabel#appTitle {
    color: #0284C7;
    font-size: 16px;
    font-weight: 700;
    padding: 18px 12px 10px 14px;
}

QLabel#appSubtitle {
    color: #64748B;
    font-size: 11px;
    padding-left: 14px;
    padding-bottom: 16px;
}

QPushButton.navBtn {
    text-align: left;
    padding: 11px 18px;
    border-radius: 8px;
    border: none;
    color: #64748B;
    font-size: 13px;
    font-weight: 500;
    margin: 3px 10px;
    background-color: transparent;
}

QPushButton.navBtn:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton.navBtn:checked {
    background-color: #E0F2FE;
    color: #0284C7;
    font-weight: 600;
}

QFrame#topBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 8px 16px;
}

QFrame#statusBar {
    background-color: #FFFFFF;
    border-top: 1px solid #E2E8F0;
    padding: 6px 16px;
}

QFrame.card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px;
}

QFrame.metricCard {
    background-color: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px;
}

QLabel.metricTitle {
    color: #64748B;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel.metricValue {
    color: #0F172A;
    font-size: 20px;
    font-weight: 700;
    margin-top: 4px;
}

QPushButton.primaryBtn {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 18px;
}

QPushButton.primaryBtn:hover {
    background-color: #0369A1;
}

QPushButton.secondaryBtn {
    background-color: #F1F5F9;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
    font-weight: 500;
    font-size: 13px;
    padding: 9px 16px;
}

QPushButton.secondaryBtn:hover {
    background-color: #E2E8F0;
}

QPushButton.dangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 16px;
}

QPushButton.dangerBtn:hover {
    background-color: #B91C1C;
}

QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #E2E8F0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0284C7;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #0284C7;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}
"""

def get_theme_stylesheet(theme_name: str = "dark") -> str:
    """Return the stylesheet string matching the chosen theme."""
    if theme_name.lower() == "light":
        return LIGHT_THEME_QSS
    return DARK_THEME_QSS
