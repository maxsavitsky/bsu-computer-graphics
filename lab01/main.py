import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys
import math

class ColorConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Конвертер Цветов (RGB-HLS-CMYK)")
        self.geometry("650x650")
        self.resizable(False, False)

        self._is_updating = False

        self.rgb_vars = {comp: tk.IntVar(value=0) for comp in "RGB"}
        self.hls_vars = {comp: tk.DoubleVar(value=0.0) for comp in "HLS"}
        self.cmyk_vars = {comp: tk.DoubleVar(value=0.0) for comp in "CMYK"}

        self._create_widgets()

        self.update_from_rgb()

    def _rgb_to_hls(self, r, g, b):
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        return h * 360, l * 100, s * 100

    def _hls_to_rgb(self, h, l, s):
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        return int(r * 255), int(g * 255), int(b * 255)

    def _rgb_to_cmyk(self, r, g, b):
        if r == 0 and g == 0 and b == 0:
            return 0, 0, 0, 100

        r_prime, g_prime, b_prime = r / 255.0, g / 255.0, b / 255.0

        k = 1.0 - max(r_prime, g_prime, b_prime)

        if k == 1.0:
            return 0, 0, 0, 100

        c = (1.0 - r_prime - k) / (1.0 - k)
        m = (1.0 - g_prime - k) / (1.0 - k)
        y = (1.0 - b_prime - k) / (1.0 - k)

        return c * 100, m * 100, y * 100, k * 100

    def _cmyk_to_rgb(self, c, m, y, k):
        r = 255 * (1 - c / 100) * (1 - k / 100)
        g = 255 * (1 - m / 100) * (1 - k / 100)
        b = 255 * (1 - y / 100) * (1 - k / 100)
        return int(r), int(g), int(b)

    def _create_widgets(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.color_preview = tk.Label(top_frame, text="", bg="#000000", width=20, height=5, relief="groove")
        self.color_preview.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 10))

        btn_pick_color = ttk.Button(top_frame, text="Выбрать цвет из палитры", command=self.pick_color)
        btn_pick_color.pack(side=tk.RIGHT, anchor='center', expand=True, fill=tk.BOTH)

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.rgb_frame = self._create_model_frame(main_frame, "RGB", ["R", "G", "B"], [255, 255, 255], self.rgb_vars, self.update_from_rgb)
        self.hls_frame = self._create_model_frame(main_frame, "HLS", ["H", "L", "S"], [360, 100, 100], self.hls_vars, self.update_from_hls)
        self.cmyk_frame = self._create_model_frame(main_frame, "CMYK", ["C", "M", "Y", "K"], [100, 100, 100, 100], self.cmyk_vars, self.update_from_cmyk)

        self.rgb_frame.pack(pady=5, fill=tk.X)
        self.hls_frame.pack(pady=5, fill=tk.X)
        self.cmyk_frame.pack(pady=5, fill=tk.X)

    def _create_model_frame(self, parent, name, components, max_values, var_dict, update_cmd):
        frame = ttk.LabelFrame(parent, text=name, padding=10)

        frame.columnconfigure(1, weight=3) # Ползунок занимает больше места
        frame.columnconfigure(2, weight=1) # Поле ввода

        for i, comp in enumerate(components):
            label = ttk.Label(frame, text=f"{comp}:")
            label.grid(row=i, column=0, sticky='w', padx=5, pady=5)

            scale = ttk.Scale(frame, from_=0, to=max_values[i], orient=tk.HORIZONTAL, variable=var_dict[comp], command=lambda e, cmd=update_cmd: cmd())
            scale.grid(row=i, column=1, sticky='we', padx=5, pady=5)

            entry = ttk.Entry(frame, width=5, textvariable=var_dict[comp])
            entry.grid(row=i, column=2, sticky='e', padx=5, pady=5)
            entry.bind("<Return>", lambda e, cmd=update_cmd: cmd())
            entry.bind("<FocusOut>", lambda e, cmd=update_cmd: cmd())

        return frame

    def pick_color(self):
        color_tuple = colorchooser.askcolor(color=self.color_preview['bg'])

        if color_tuple and color_tuple[0]:
            r, g, b = color_tuple[0]

            if self._is_updating:
                return
            self._is_updating = True

            self.rgb_vars['R'].set(int(r))
            self.rgb_vars['G'].set(int(g))
            self.rgb_vars['B'].set(int(b))

            self._is_updating = False

            self.update_from_rgb()

    def update_from_rgb(self, event=None):
        if self._is_updating:
            return
        self._is_updating = True

        r = self.rgb_vars['R'].get()
        g = self.rgb_vars['G'].get()
        b = self.rgb_vars['B'].get()

        h, l, s = self._rgb_to_hls(r, g, b)
        c, m, y, k = self._rgb_to_cmyk(r, g, b)

        self.hls_vars['H'].set(round(h, 2))
        self.hls_vars['L'].set(round(l, 2))
        self.hls_vars['S'].set(round(s, 2))

        self.cmyk_vars['C'].set(round(c, 2))
        self.cmyk_vars['M'].set(round(m, 2))
        self.cmyk_vars['Y'].set(round(y, 2))
        self.cmyk_vars['K'].set(round(k, 2))

        self._update_color_preview(r, g, b)
        self._is_updating = False

    def update_from_hls(self, event=None):
        if self._is_updating:
            return
        self._is_updating = True

        h = self.hls_vars['H'].get()
        l = self.hls_vars['L'].get()
        s = self.hls_vars['S'].get()

        r, g, b = self._hls_to_rgb(h, l, s)
        c, m, y, k = self._rgb_to_cmyk(r, g, b)

        self.rgb_vars['R'].set(r)
        self.rgb_vars['G'].set(g)
        self.rgb_vars['B'].set(b)

        self.cmyk_vars['C'].set(round(c, 2))
        self.cmyk_vars['M'].set(round(m, 2))
        self.cmyk_vars['Y'].set(round(y, 2))
        self.cmyk_vars['K'].set(round(k, 2))

        self._update_color_preview(r, g, b)
        self._is_updating = False

    def update_from_cmyk(self, event=None):
        if self._is_updating:
            return
        self._is_updating = True

        c = self.cmyk_vars['C'].get()
        m = self.cmyk_vars['M'].get()
        y = self.cmyk_vars['Y'].get()
        k = self.cmyk_vars['K'].get()

        r, g, b = self._cmyk_to_rgb(c, m, y, k)
        h, l, s = self._rgb_to_hls(r, g, b)

        self.rgb_vars['R'].set(r)
        self.rgb_vars['G'].set(g)
        self.rgb_vars['B'].set(b)

        self.hls_vars['H'].set(round(h, 2))
        self.hls_vars['L'].set(round(l, 2))
        self.hls_vars['S'].set(round(s, 2))

        self._update_color_preview(r, g, b)
        self._is_updating = False

    def _update_color_preview(self, r, g, b):
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.config(bg=hex_color)

if __name__ == "__main__":
    app = ColorConverterApp()
    app.mainloop()
