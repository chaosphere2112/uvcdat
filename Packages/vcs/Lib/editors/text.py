from vcs.vtk_ui import Textbox, Toolbar
import vcs.vtk_ui.text
from vcs.colorpicker import ColorPicker
from vtk import vtkTextProperty
from vcs.vtk_ui.behaviors import ClickableMixin
import priority
import vcs

class TextEditor(ClickableMixin, priority.PriorityEditor):
    def __init__(self, interactor, text, index, configurator):

        self.interactor = interactor
        self.text = text
        self.index = index
        self.configurator = configurator

        # We're going to insert textboxes at each of the locations
        # That way we can edit the text.
        self.old_priority = text.priority
        text.priority = 0
        configurator.changed = True
        configurator.save()
        self.textboxes = None

        self.toolbar = Toolbar(self.interactor, "Text Options")
        self.toolbar.add_slider_button(text.height, 1, 100, "Height", update=self.update_height)
        halign_bar = self.toolbar.add_toolbar("Horizontal Align")

        self.left_align_button = halign_bar.add_toggle_button("Left Align", on=self.align_left, off=self.dealign_left)
        self.center_align_button = halign_bar.add_toggle_button("Center Align", on=self.align_center, off=self.dealign_center)
        self.right_align_button = halign_bar.add_toggle_button("Right Align", on=self.align_right, off=self.dealign_right)

        valign_bar = self.toolbar.add_toolbar("Vertical Align")

        self.top_align_button = valign_bar.add_toggle_button("Top Align", on=self.align_top, off=self.dealign_top)
        self.half_align_button = valign_bar.add_toggle_button("Half Align", on=self.align_half, off=self.dealign_half)
        self.bottom_align_button = valign_bar.add_toggle_button("Bottom Align", on=self.align_bottom, off=self.dealign_bottom)

        self.toolbar.add_slider_button(text.angle, 0, 360, "Angle", update=self.update_angle)
        self.fonts = sorted(vcs.elements["font"].keys())

        font_toolbar = self.toolbar.add_toolbar("Fonts")

        font_buttons = {}

        def font_setter(font):
            def set_font():
                current_font = vcs.getfontname(self.text.font)
                if font != current_font:
                    font_buttons[current_font].set_state(0)
                self.text.font = font
                font_buttons[font].set_state(1)
                self.update()
            return set_font

        deactivate = font_setter("default")

        for ind, font in enumerate(self.fonts):
            # Math fonts render unintelligbly
            if font[:4] != "Math":
                button = font_toolbar.add_toggle_button(font, on=font_setter(font), off=deactivate, font=vcs.elements["font"][font])
            else:
                button = font_toolbar.add_toggle_button(font, on=font_setter(font), off=deactivate)

            if vcs.elements["fontNumber"][self.text.font] == font:
                button.set_state(1)
            font_buttons[font] = button

        self.picker = None
        self.toolbar.add_button(["Change Color"], action=self.change_color)



        super(TextEditor, self).__init__()
        self.register()
        self.toggle_halign_buttons()
        self.toggle_valign_buttons()

    def get_object(self):
        return self.text

    def is_object(self, text):
        return self.text == text

    def place(self):
        self.toolbar.place()
        for box in self.textboxes:
            box.place()

    def update(self):
        if self.textboxes:

            for box in self.textboxes:
                box.stop_editing()
                box.detach()
            del self.textboxes

        self.textboxes = []
        w, h = self.interactor.GetRenderWindow().GetSize()
        cmap = vcs.getcolormap()

        prop = vtkTextProperty()
        vcs.vcs2vtk.prepTextProperty(prop, (w, h), self.text, self.text, cmap)

        # need to subtract text.angle from 360
        prop.SetOrientation(360 - self.text.angle)

        for ind, x in enumerate(self.text.x):
            y = self.text.y[ind]
            string = self.text.string[ind]

            text_width, text_height = text_dimensions(self.text, ind, (w, h))
            x = x * w
            y = h - y * h # mirror the y axis for widgets
            if self.text.valign in ("half", 2):
                y -= text_height / 2.0
            elif self.text.valign in ("bottom", "base", 3, 4):
                y -= text_height

            if self.text.halign in ("right", 2):
                x -= text_width
            elif self.text.halign in ("center", 1):
                x -= text_width / 2.0

            textbox = Textbox(self.interactor, string, left=x, top=y, movable=True, on_editing_end=self.finished_editing, on_move=self.moved_textbox, textproperty=prop, on_click=self.textbox_clicked)
            textbox.show()

            if ind == self.index:
                textbox.start_editing()

            self.textboxes.append(textbox)

    def finished_editing(self, textbox):
        self.text.string[self.textboxes.index(textbox)] = textbox.text
        self.configurator.changed = True

    def in_bounds(self, x, y):
        return inside_text(self.text, x, y, *self.interactor.GetRenderWindow().GetSize(), index=self.index) is not None

    def click_release(self):
        x, y = self.event_position()
        text_index = inside_text(self.text, x, y, *self.interactor.GetRenderWindow().GetSize())

        self.process_click(text_index, x, y)

    def moved_textbox(self):
        box = self.textboxes[self.index]
        w, h = self.interactor.GetRenderWindow().GetSize()

        xcoord, ycoord = box.left, box.top

        text_width, text_height = box.get_dimensions()

        # Adjust for the origin of the textbox
        if self.text.valign in ("half", 2):
            ycoord += text_height / 2.0
        elif self.text.valign in ("bottom", 4):
            ycoord += text_height

        if self.text.halign in ("right", 2):
            xcoord += text_width
        elif self.text.halign in ("center", 1):
            xcoord += text_width / 2.0

        self.text.x[self.index] = xcoord / float(w)
        self.text.y[self.index] = (h - ycoord) / float(h)
        self.configurator.changed = True

    def handle_click(self, point):
        x, y = point
        return self.in_bounds(x, y) or self.toolbar.in_toolbar(x, y) or self.current_modifiers()["alt"]

    def process_click(self, text_index, x, y):

        if text_index == self.index:
            # Adjust cursor position
            self.textboxes[self.index].start_editing((x, y))
            return
        else:
            self.textboxes[self.index].stop_editing()

            if text_index is not None:
                # Change which one we're editing
                self.index = text_index
                self.textboxes[self.index].start_editing((x, y))
            else:
                if self.current_modifiers()["alt"]:

                    self.textboxes[self.index].stop_editing()

                    # Add a new text item to self.text, update, and start editing
                    new_index = len(self.text.x)

                    self.text.x.append(x)
                    self.text.y.append(y)
                    self.text.string.append("New Text")

                    self.index = new_index
                    self.update()

    def textbox_clicked(self, point):
        x, y = point

        winsize = self.interactor.GetRenderWindow().GetSize()

        clicked_on = inside_text(self.text, x, y, *winsize)
        self.process_click(clicked_on, x, y)

    def save(self):
        self.configurator.save()

    def deactivate(self):
        self.text.priority = self.old_priority
        self.configurator.deactivate(self)

    def update_height(self, value):
        self.text.height = value
        self.configurator.changed = True
        self.update()

    def change_color(self, state):
        if self.picker:
            self.picker.make_current()
        else:
            self.picker = ColorPicker(500, 500, vcs.getcolormap(), self.text.color, on_save=self.set_color, on_cancel=self.cancel_color)

    def set_color(self, cmap, color):
        self.text.color = color
        self.configurator.changed = True
        self.update()
        self.picker = None
        #text colormap is currently not in place, will be later.
        #self.text.colormap = cmap

    def cancel_color(self):
        self.picker = None

    def detach(self):
        self.unregister()
        for box in self.textboxes:
            box.detach()
        del self.textboxes
        self.text.priority = self.old_priority
        self.toolbar.detach()

    def toggle_halign_buttons(self):
        halign = self.text.halign
        buttons = [self.left_align_button, self.right_align_button, self.center_align_button]

        if halign in ("left", 0):
            states = [1, 0, 0]
        elif halign in ("right", 2):
            states = [0, 1, 0]
        else:
            states = [0, 0, 1]

        for state, button in zip(states, buttons):
            button.set_state(state)

        self.configurator.changed = True
        self.update()

    def toggle_valign_buttons(self):
        valign = self.text.valign
        buttons = [self.top_align_button, self.bottom_align_button, self.half_align_button]

        if valign in ("top", 0, 'cap', 1):
            states = [1, 0, 0]
        elif valign in ("bottom", 'base', 3, 4):
            states = [0, 1, 0]
        else:
            states = [0, 0, 1]

        for state, button in zip(states, buttons):
            button.set_state(state)
        self.configurator.changed = True
        self.update()


    def align_left(self):
        self.text.halign = "left"
        self.toggle_halign_buttons()
    def dealign_left(self):
        self.toggle_halign_buttons()

    def align_center(self):
        self.text.halign = "center"
        self.toggle_halign_buttons()

    def dealign_center(self):
        self.text.halign = "left"
        self.toggle_halign_buttons()

    def align_right(self):
        self.text.halign = "right"
        self.toggle_halign_buttons()
    def dealign_right(self):
        self.text.halign = "left"
        self.toggle_halign_buttons()

    def align_top(self):
        self.text.valign = "top"
        self.toggle_valign_buttons()
    def dealign_top(self):
        self.toggle_valign_buttons()

    def align_half(self):
        self.text.valign = "half"
        self.toggle_valign_buttons()
    def dealign_half(self):
        self.text.valign = "top"
        self.toggle_valign_buttons()

    def align_bottom(self):
        self.text.valign = "bottom"
        self.toggle_valign_buttons()
    def dealign_bottom(self):
        self.text.valign = "top"
        self.toggle_valign_buttons()

    def update_angle(self, value):
        self.text.angle = int(value)
        for box in self.textboxes:
            box.repr.GetTextActor().GetTextProperty().SetOrientation(360 - self.text.angle)
            box.place()
            box.render()

    def change_font(self, state):
        self.text.font = self.fonts[state]
        self.configurator.changed = True
        self.update()

    def delete(self):
        """Overriding PriorityEditor.delete to make this behave intelligently"""
        if not self.textboxes[self.index].editing:
            self.text.priority = 0
            self.configurator.changed = True
            self.configurator.deactivate(self)

def text_dimensions(text, index, winsize):
    prop = vtkTextProperty()
    vcs.vcs2vtk.prepTextProperty(prop, winsize, text, text, vcs.getcolormap())
    return vcs.vtk_ui.text.text_dimensions(text.string[index], prop)

def inside_text(text, x, y, screen_width, screen_height, index=None):
    import math

    winsize = (screen_width, screen_height)

    if x > 1:
        x = x / float(screen_width)
    if y > 1:
        y = y / float(screen_height)

    for ind, xcoord in enumerate(text.x):
        if index is not None:
            if ind != index:
                continue

        ycoord = text.y[ind]
        text_width, text_height = text_dimensions(text, ind, winsize)
        text_width = text_width / float(screen_width)
        text_height = text_height / float(screen_height)

        local_x, local_y = x, y
        # Adjust X, Y for angle
        if text.angle != 0:
            # Translate to the origin
            translated_x, translated_y = x - xcoord, y - ycoord
            # Rotate about the origin
            theta = math.radians(text.angle)
            txrot = translated_x * math.cos(theta) - translated_y * math.sin(theta)
            tyrot = translated_x * math.sin(theta) + translated_y * math.cos(theta)
            # Translate back to the point
            local_x, local_y = txrot + xcoord, tyrot + ycoord

        # Adjust for alignments
        if text.valign in ("half", 2):
            ycoord -= text_height / 2.0
        elif text.valign in ("top", 0):
            ycoord -= text_height

        if text.halign in ("right", 2):
            xcoord -= text_width
        elif text.halign in ("center", 1):
            xcoord -= text_width / 2.0

        if local_x > xcoord and local_x < xcoord + text_width and local_y < ycoord + text_height and local_y > ycoord:
            return ind

    return None