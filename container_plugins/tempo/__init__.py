# -*- coding: utf-8; -*-

# Copyright (C) 2015 - 2017 Lionel Ott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xml.etree import ElementTree

from PyQt5 import QtWidgets

import gremlin
import gremlin.ui.input_item


class TempoContainerWidget(gremlin.ui.input_item.AbstractContainerWidget):

    def __init__(self, profile_data, parent=None):
        super().__init__(profile_data, parent)

    def _create_ui(self):
        self.delay_layout = QtWidgets.QHBoxLayout()
        self.delay_layout.addWidget(QtWidgets.QLabel("Long press delay"))
        self.delay_input = QtWidgets.QDoubleSpinBox()
        self.delay_input.setRange(0.1, 2.0)
        self.delay_input.setSingleStep(0.1)
        self.delay_input.setValue(0.5)
        self.delay_input.valueChanged.connect(self._delay_changed_cb)
        self.delay_layout.addWidget(self.delay_input)
        self.delay_layout.addStretch()
        self.main_layout.addLayout(self.delay_layout)

        self.main_layout.addWidget(QtWidgets.QLabel("<b>Short Press</b>"))
        if self.profile_data.actions[0] is None:
            self._add_action_selector(lambda x: self._add_action(0, x))
        else:
            self._create_action_widget(0)
        self.main_layout.addWidget(QtWidgets.QLabel("<b>Long Press</b>"))
        if self.profile_data.actions[1] is None:
            self._add_action_selector(lambda x: self._add_action(1, x))
        else:
            self._create_action_widget(1)

    def _add_action_selector(self, add_action_cb):
        action_selector = gremlin.ui.common.ActionSelector(
            self.profile_data.get_input_type()
        )
        action_selector.action_added.connect(add_action_cb)
        self.main_layout.addWidget(action_selector)

    def _create_action_widget(self, index):
        action_item = self.profile_data.actions[index]
        self.main_layout.addWidget(
            self._add_action_widget(action_item.widget(action_item))
        )

    def _add_action(self, index, action_name):
        plugin_manager = gremlin.plugin_manager.ActionPlugins()
        action_item = plugin_manager.get_class(action_name)(self.profile_data)
        self.profile_data.actions[index] = action_item
        self.modified.emit()

    def _delay_changed_cb(self, value):
        self.profile_data.delay = value

    def _handle_interaction(self, widget, action):
        index = self._get_widget_index(widget)
        if index != -1:
            if index == 0 and self.profile_data.actions[0] is None:
                index = 1
            self.profile_data.actions[index] = None
            self.modified.emit()

    def _get_window_title(self):
        if self.profile_data.is_valid():
            return "Tempo: {} / {}".format(
                self.profile_data.actions[0].name,
                self.profile_data.actions[1].name
            )
        else:
            return "Tempo"


class TempoContainer(gremlin.base_classes.AbstractContainer):

    name = "Tempo"
    tag = "tempo"
    widget = TempoContainerWidget
    input_types = [
        gremlin.common.InputType.JoystickButton,
        gremlin.common.InputType.Keyboard
    ]
    interaction_types = [
        gremlin.ui.input_item.ActionWrapper.Interactions.Edit,
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions = [None, None]
        self.delay = 0.5

    def _parse_xml(self, node):
        pass

    def _generate_xml(self):
        node = ElementTree.Element("container")
        node.set("type", TempoContainer.tag)
        node.set("delay", str(self.delay))
        for action in self.actions:
            node.append(action.to_xml())
        return node

    def _generate_code(self):
        return gremlin.profile.CodeBlock()

    def _is_valid(self):
        return len(self.actions) == 2 and None not in self.actions


# Plugin definitions
version = 1
name = "tempo"
create = TempoContainer