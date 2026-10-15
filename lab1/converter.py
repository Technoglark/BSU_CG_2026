def clamp(val, low, high):
    return max(low, min(high, val))


def rgb_to_cmyk(r, g, b):
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    k = 1.0 - max(r_n, g_n, b_n)
    if k >= 1.0:
        return 0.0, 0.0, 0.0, 100.0
    c = (1.0 - r_n - k) / (1.0 - k)
    m = (1.0 - g_n - k) / (1.0 - k)
    y = (1.0 - b_n - k) / (1.0 - k)
    return (
        round(c * 100, 1),
        round(m * 100, 1),
        round(y * 100, 1),
        round(k * 100, 1),
    )


def cmyk_to_rgb(c, m, y, k):
    c_n, m_n, y_n, k_n = c / 100.0, m / 100.0, y / 100.0, k / 100.0
    r = 255.0 * (1.0 - c_n) * (1.0 - k_n)
    g = 255.0 * (1.0 - m_n) * (1.0 - k_n)
    b = 255.0 * (1.0 - y_n) * (1.0 - k_n)
    return int(round(r)), int(round(g)), int(round(b))


def rgb_to_hsv(r, g, b, prev_h=0.0):
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    c_max = max(r_n, g_n, b_n)
    c_min = min(r_n, g_n, b_n)
    delta = c_max - c_min

    if delta == 0:
        h = prev_h
    elif c_max == r_n:
        h = 60.0 * (((g_n - b_n) / delta) % 6)
    elif c_max == g_n:
        h = 60.0 * (((b_n - r_n) / delta) + 2)
    else:
        h = 60.0 * (((r_n - g_n) / delta) + 4)

    if h < 0:
        h += 360.0

    s = 0.0 if c_max == 0 else (delta / c_max) * 100.0
    v = c_max * 100.0
    return round(h, 1), round(s, 1), round(v, 1)


def hsv_to_rgb(h, s, v):
    h_norm = h % 360.0
    s_n, v_n = s / 100.0, v / 100.0
    c = v_n * s_n
    x = c * (1.0 - abs(((h_norm / 60.0) % 2) - 1.0))
    m = v_n - c

    if 0 <= h_norm < 60:
        r1, g1, b1 = c, x, 0.0
    elif 60 <= h_norm < 120:
        r1, g1, b1 = x, c, 0.0
    elif 120 <= h_norm < 180:
        r1, g1, b1 = 0.0, c, x
    elif 180 <= h_norm < 240:
        r1, g1, b1 = 0.0, x, c
    elif 240 <= h_norm < 300:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x

    return (
        int(round((r1 + m) * 255)),
        int(round((g1 + m) * 255)),
        int(round((b1 + m) * 255)),
    )


def convert_all(source, values, prev_h=0.0):
    if source == "rgb":
        r = int(clamp(values["r"], 0, 255))
        g = int(clamp(values["g"], 0, 255))
        b = int(clamp(values["b"], 0, 255))
        c, m, y, k = rgb_to_cmyk(r, g, b)
        h, s, v = rgb_to_hsv(r, g, b, prev_h)
    elif source == "cmyk":
        c = round(clamp(values["c"], 0, 100), 1)
        m = round(clamp(values["m"], 0, 100), 1)
        y = round(clamp(values["y"], 0, 100), 1)
        k = round(clamp(values["k"], 0, 100), 1)
        r, g, b = cmyk_to_rgb(c, m, y, k)
        h, s, v = rgb_to_hsv(r, g, b, prev_h)
    elif source == "hsv":
        h = round(clamp(values["h"], 0, 360), 1)
        s = round(clamp(values["s"], 0, 100), 1)
        v = round(clamp(values["v"], 0, 100), 1)
        r, g, b = hsv_to_rgb(h, s, v)
        c, m, y, k = rgb_to_cmyk(r, g, b)

    hex_color = f"#{r:02X}{g:02X}{b:02X}"
    return {
        "rgb": {"r": r, "g": g, "b": b},
        "cmyk": {"c": c, "m": m, "y": y, "k": k},
        "hsv": {"h": h, "s": s, "v": v},
        "hex": hex_color,
    }