"""
KidGame — Multi-stage, kid-friendly game built with Kivy
Stages:
 1) Color Match — Tap the color that matches the prompt
 2) Shape Sort  — Drag shapes into matching boxes
 3) Count & Collect — Tap apples to reach a target count

Designed for a 5-year-old: big buttons, simple feedback, touch-first controls.

To run (desktop):
  pip install kivy
  python main.py

Packaging to mobile: see README.md (Buildozer for Android, kivy-ios for iOS).
"""

import random
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.properties import StringProperty, NumericProperty, ListProperty


def try_play_sound(fname):
    try:
        sound = SoundLoader.load(fname)
        if sound:
            sound.play()
    except Exception:
        pass


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Label(text='Welcome!', font_size='40sp'))
        layout.add_widget(
            Label(text='Play a fun learning game', font_size='20sp'))
        btn = Button(text='Start', size_hint=(1, .3), font_size='28sp')
        btn.bind(on_release=lambda *_: self.start_game())
        layout.add_widget(btn)
        self.add_widget(layout)

    def start_game(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'color'


class BigColorButton(Button):
    color_rgb = ListProperty([1, 0, 0])

    def on_color_rgb(self, instance, value):
        with self.canvas.before:
            Color(*value)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *a):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size


class ColorMatchScreen(Screen):
    colors = {
        'Red': (1, 0, 0),
        'Green': (0, 1, 0),
        'Blue': (0, 0, 1),
        'Yellow': (1, 1, 0),
        'Purple': (0.6, 0, 0.6),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target = None
        self.correct_needed = 3
        self.correct = 0
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.prompt = Label(text='', font_size='36sp', size_hint=(1, .2))
        self.layout.add_widget(self.prompt)
        grid = GridLayout(cols=2, spacing=10)
        for name, rgb in self.colors.items():
            b = BigColorButton(text=name, font_size='26sp')
            b.color_rgb = rgb
            b.bind(on_release=self.check_color)
            grid.add_widget(b)
        self.layout.add_widget(grid)
        self.status = Label(
            text='Tap the color that matches the word', font_size='18sp', size_hint=(1, .15))
        self.layout.add_widget(self.status)
        self.add_widget(self.layout)
        Clock.schedule_once(lambda dt: self.new_round(), 0.5)

    def new_round(self):
        self.target = random.choice(list(self.colors.keys()))
        self.prompt.text = f"Find: {self.target}"

    def check_color(self, button):
        if button.text == self.target:
            self.correct += 1
            self.status.text = f"Good! ({self.correct}/{self.correct_needed})"
            try_play_sound('assets/ding.wav')
        else:
            self.status.text = "Try again!"
            try_play_sound('assets/error.wav')
        if self.correct >= self.correct_needed:
            Clock.schedule_once(lambda dt: self.goto_next(), 0.8)
        else:
            self.new_round()

    def goto_next(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'shape'


class DraggableShape(Widget):
    shape = StringProperty('circle')
    color_rgb = ListProperty([1, 0, 0])

    def __init__(self, shape='circle', color=(1, 0, 0), **kwargs):
        super().__init__(**kwargs)
        self.shape = shape
        self.color_rgb = color
        self.size = (120, 120)
        with self.canvas:
            Color(*self.color_rgb)
            if self.shape == 'circle':
                self.g = Ellipse(pos=self.pos, size=self.size)
            else:
                self.g = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *a):
        if hasattr(self, 'g'):
            self.g.pos = self.pos
            self.g.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._touch_offset = (self.center_x - touch.x,
                                  self.center_y - touch.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center_x = touch.x + self._touch_offset[0]
            self.center_y = touch.y + self._touch_offset[1]
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class TargetBox(Widget):
    accept_shape = StringProperty('circle')

    def __init__(self, accept_shape='circle', **kwargs):
        super().__init__(**kwargs)
        self.accept_shape = accept_shape
        self.size = (140, 140)
        with self.canvas:
            Color(.9, .9, .9)
            self.g = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *a):
        if hasattr(self, 'g'):
            self.g.pos = self.pos
            self.g.size = self.size


class ShapeSortScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.prompt = Label(
            text='Drag the shapes to the matching box', font_size='24sp', size_hint=(1, .15))
        self.layout.add_widget(self.prompt)
        playfield = Widget()
        # Create targets
        targets = [('circle', (0.9, 0.5, 0.5)), ('square', (0.5, 0.9, 0.5))]
        self.target_widgets = []
        for i, (shape, col) in enumerate(targets):
            tb = TargetBox(accept_shape=shape)
            tb.pos = (50 + i * 200, 300)
            self.target_widgets.append(tb)
            playfield.add_widget(tb)
        # Add draggable shapes
        shapes = [DraggableShape(shape='circle', color=(1, 0.2, 0.2)), DraggableShape(
            shape='square', color=(0.2, 1, 0.2))]
        for i, s in enumerate(shapes):
            s.pos = (50 + i * 180, 100)
            playfield.add_widget(s)
        self.shapes = shapes
        self.layout.add_widget(playfield)
        self.status = Label(
            text='Place each shape in the right box', font_size='18sp', size_hint=(1, .15))
        self.layout.add_widget(self.status)
        self.add_widget(self.layout)
        # Check placements periodically
        Clock.schedule_interval(self.check_placements, 0.5)
        self.solved = 0
        self.solved_needed = len(self.shapes)

    def check_placements(self, dt):
        for s in list(self.shapes):
            for t in self.target_widgets:
                if s.center_x > t.x and s.center_x < t.x + t.width and s.center_y > t.y and s.center_y < t.y + t.height:
                    if s.shape == t.accept_shape:
                        try_play_sound('assets/ding.wav')
                        self.shapes.remove(s)
                        s.disabled = True
                        self.solved += 1
                        self.status.text = f'Great! ({self.solved}/{self.solved_needed})'
                        s.parent.remove_widget(s)
                        break
                    else:
                        self.status.text = 'Not the right box'
                        try_play_sound('assets/error.wav')
                        # nudge back
                        s.pos = (50, 100)
        if self.solved >= self.solved_needed:
            Clock.schedule_once(lambda dt: self.goto_next(), 1)

    def goto_next(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'count'


class Apple(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (80, 80)
        with self.canvas:
            Color(1, 0.2, 0.2)
            self.g = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *a):
        if hasattr(self, 'g'):
            self.g.pos = self.pos
            self.g.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            try_play_sound('assets/pick.wav')
            if self.parent:
                self.parent.remove_widget(self)
            return True
        return super().on_touch_down(touch)


class CountCollectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target = random.randint(3, 6)
        self.collected = 0
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.prompt = Label(
            text=f'Collect {self.target} apples', font_size='28sp', size_hint=(1, .15))
        self.layout.add_widget(self.prompt)
        self.playfield = Widget()
        self.layout.add_widget(self.playfield)
        self.status = Label(
            text=f'Collected: {self.collected}', font_size='20sp', size_hint=(1, .15))
        self.layout.add_widget(self.status)
        self.add_widget(self.layout)
        Clock.schedule_once(lambda dt: self.spawn_apples(7), 0.5)

    def spawn_apples(self, n):
        for i in range(n):
            a = Apple()
            a.pos = (random.randint(30, 400), random.randint(50, 300))
            self.playfield.add_widget(a)
        # monitor parent removal events
        Clock.schedule_interval(self.check_count, 0.5)

    def check_count(self, dt):
        current = len(
            [w for w in self.playfield.children if isinstance(w, Apple)])
        self.collected = max(0, 7 - current)
        self.status.text = f'Collected: {self.collected} / {self.target}'
        if self.collected >= self.target:
            try_play_sound('assets/ding.wav')
            Clock.schedule_once(lambda dt: self.goto_win(), 1)

    def goto_win(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'win'


class WinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        layout.add_widget(Label(text='You did it!', font_size='40sp'))
        btn = Button(text='Play again', size_hint=(1, .2), font_size='26sp')
        btn.bind(on_release=lambda *_: self.play_again())
        layout.add_widget(btn)
        self.add_widget(layout)

    def play_again(self):
        self.manager.transition = SlideTransition(direction='right')
        # reset screens
        self.manager.get_screen('color').correct = 0
        self.manager.current = 'menu'


class KidGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ColorMatchScreen(name='color'))
        sm.add_widget(ShapeSortScreen(name='shape'))
        sm.add_widget(CountCollectScreen(name='count'))
        sm.add_widget(WinScreen(name='win'))
        return sm


if __name__ == '__main__':
    KidGameApp().run()
