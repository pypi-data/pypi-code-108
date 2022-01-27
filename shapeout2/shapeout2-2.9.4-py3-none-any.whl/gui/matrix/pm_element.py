from . import dm_element


class MatrixElement(dm_element.MatrixElement):
    def mousePressEvent(self, event):
        # toggle selection
        if not self.invalid:
            self.active = not self.active
            self.element_changed.emit()
            self.update_content()
            event.accept()

    def update_content(self, quickview=False):
        if self.invalid:
            color = "#DCDCDC"  # gray
            label = "invalid"
            tooltip = "Incompatible plot settings"
        elif self.active and self.enabled:
            color = "#86E7C1"  # turquois
            label = "active"
            tooltip = "Click to deactivate"
        elif self.active and not self.enabled:
            color = "#C9DAD7"  # gray-turquois
            label = "active\n(unused)"
            tooltip = "Click to deactivate"
        elif not self.active and self.enabled:
            color = "#EFEFEF"  # light gray
            label = "inactive"
            tooltip = "Click to activate"
        else:
            color = "#DCDCDC"  # gray
            label = "inactive\n(unused)"
            tooltip = "Click to activate"

        self.label.setText(label)
        self.setToolTip(tooltip)
        self.label.setToolTip(tooltip)
        self.setStyleSheet(
            "background-color:{};color:black".format(color))
