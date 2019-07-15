from Xlib import X, XK
from Xlib.display import Display, colormap
from os import system


BACKGROUND_IMAGE = "wallpaper.png"
BORDER_COLOR = "#007cbf"
FOCUS_COLOR = "#eda900"
BORDER_WIDTH = 3


class WM:
    def __init__(self):
        self.display = Display()
        self.root = self.display.screen().root
        self.color_map = self.display.screen().default_colormap
        self.root.change_attributes(
            event_mask=X.SubstructureRedirectMask | X.KeyReleaseMask | X.FocusChangeMask)
        self.width = self.root.get_geometry().width
        self.height = self.root.get_geometry().height
        self.windows = []
        self.focused_window = None
        self.actions = [
            [XK.XK_F, lambda:system("rofi -show")],
            [XK.XK_X, lambda:self.destroy(self.focused_window)]
        ]
        self.modifier = X.Mod1Mask
        self.next_position = 0
        self.configure()
        system("feh --bg-scale wallpaper.png")

    def getKeyCodes(self, key):
        codes = set(code for code, i in self.display.keysym_to_keycodes(key))
        return list(codes)

    def configure(self):
        for i in self.actions:
            for j in self.getKeyCodes(i[0]):
                self.root.grab_key(j, self.modifier, True,
                                   X.GrabModeSync, X.GrabModeSync)

    def handleMap(self, event):
        event.window.map()
        # event.window.set_input_focus(X.RevertToParent, X.CurrentTime)
        width = self.width//2 - 40
        height = self.height//2 - 40
        if self.next_position == 4:
            self.next_position = 0
        if self.next_position == 0:
            x = 0
            y = 0
        elif self.next_position == 1:
            x = self.width//2
            y = 0
        elif self.next_position == 2:
            x = 0
            y = self.height//2
        elif self.next_position == 3:
            x = self.width//2
            y = self.height//2
        event.window.configure(
            stack_mode=X.Above,
            width=width,
            height=height,
            x=x,
            y=y
        )
        self.next_position += 1
        self.windows.append(event.window)

    def destroy(self, window):
        window.destroy()
        self.windows.remove(window)
        self.next_position -= 1

        width = self.width//2 - 40
        height = self.height//2 - 40

        for i, window in enumerate(self.windows):
            if i == 0:
                x = 0
                y = 0
            elif i == 1:
                x = self.width//2
                y = 0
            elif i == 2:
                x = 0
                y = self.height//2
            elif i == 3:
                x = self.width//2
                y = self.height//2
            window.configure(
                stack_mode=X.Above,
                width=width,
                height=height,
                x=x,
                y=y
            )

    def handleKey(self, event):
        print("Clicked")
        for i in self.actions:
            if event.detail in self.getKeyCodes(i[0]):
                print("Found")
                i[1]()

    def handleEvent(self):
        if self.display.pending_events() > 0:
            event = self.display.next_event()
            print("Got Event:{}".format(event.type))
            if event.type == X.MapRequest:
                self.handleMap(event)
            elif event.type == X.KeyRelease:
                self.handleKey(event)
            elif event.type == X.FocusIn:
                print("Focusing")

    def updateFocus(self):
        window = self.display.screen().root.query_pointer().child
        if window:
            self.focused_window = window
        else:
            self.focused_window = None

    def close(self):
        self.display.close()

    def drawBorder(self, window):

        if window == self.focused_window:
            color = FOCUS_COLOR
        else:
            color = BORDER_COLOR

        color = self.color_map.alloc_named_color(
            color).pixel
        window.configure(border_width=BORDER_WIDTH)
        window.change_attributes(None, border_pixel=color)
        self.display.sync()

    def loop(self):
        while True:
            self.handleEvent()
            self.updateFocus()
            for i in self.windows:
                self.drawBorder(i)


wm = WM()
try:
    wm.loop()
except KeyboardInterrupt:
    wm.close()
