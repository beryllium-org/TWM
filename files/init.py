vr("j", jcurses())
vr("c", pv[0]["consoles"]["ttyDISPLAY0"])
vr("j").console = vr("c")
vr("j").clear()
vr("p", be.devices["AXP2101"][0])
vr("t", be.devices["ftouch"][0])
vr("d", be.devices["DISPLAY"][0])
vr("b", be.devices["bat"][0])
vr("d").auto_refresh = False

vr("j").trigger_dict = {
    "ctrlC": -1,
    "overflow": 8,
    "rest": "ignore",
    "rest_a": "common",
    "echo": "none",
    "prefix": "",
    "permit_pos": False,
    "idle": 9,
}
vr("c").enable()


def rk() -> tuple:
    return vr("p").power_key_was_pressed


def rt() -> list:
    return vr("t").touches


def tsh() -> None:
    return vr("ri")()[0]


def tlh() -> None:
    return vr("ri")()[1]


def ctop(data: str) -> None:
    vr("j").clear()
    vr("j").write(data)


def waitc() -> None:
    t = vr("rt")()
    while t:
        t = vr("rt")()
        time.sleep(0.02)


def lc() -> None:
    vr("j").nwrite("\r\033[K")


def ditem(item: str, sel: bool) -> None:
    vr("lc")()
    ldat = " - "
    if sel:
        ldat += "[ "
    ldat += item
    if sel:
        ldat += " ]"
    vr("j").write(ldat)


def refr() -> None:
    vr("d").refresh()


def clocker() -> None:
    need_refr = False
    ct = time.localtime()
    d = ct.tm_mday
    o = ct.tm_mon
    y = ct.tm_year
    h = ct.tm_hour
    m = ct.tm_min
    s = ct.tm_sec
    wd = ct.tm_wday
    darr = [d, o, y]
    harr = [h, m, s]
    if darr != vr("last_shown")[:3]:
        need_refr = True
        vr("last_shown", darr + vr("last_shown")[3:])
    if vr("lowpow"):
        if m != vr("last_shown")[4]:
            vr("last_shown", vr("last_shown")[:3] + harr)
            need_refr = True
    else:
        if s != vr("last_shown")[5]:
            vr("last_shown", vr("last_shown")[:3] + harr)
            need_refr = True

    if vr("force_refr"):
        need_refr = True
        vr("force_refr", False)
    if need_refr:
        vr("j").move(y=3)
        vr("lc")()
        d = str(d) if d < 10 else "0" + str(d)
        o = vr("months")[o]
        vr("j").nwrite(vr("days")[wd] + " " + str(d) + "/" + str(o) + "/" + str(y))
        hl = h
        hh = 0
        if hl > 9:
            hl = int(str(h)[1])
            hh = int(str(h)[0])
        ml = m
        mh = 0
        if ml > 9:
            ml = int(str(m)[1])
            mh = int(str(m)[0])
        sl = s
        sh = 0
        if vr("lowpow"):
            sl = 10
            sh = 10
        else:
            if sl > 9:
                sl = int(str(s)[1])
                sh = int(str(s)[0])
        ind = True
        if vr("lowpow"):
            ind = True
        elif not vr("ind"):
            ind = False
            vr("ind", True)
        else:
            vr("ind", False)

        ind = 12 if ind else 11
        for i in range(3):
            vr("j").move(y=6 + i)
            vr("lc")()
            vr("j").nwrite(
                " " * 9
                + vr("bigs")[hh][i]
                + vr("bigs")[hl][i]
                + vr("bigs")[ind][i]
                + vr("bigs")[mh][i]
                + vr("bigs")[ml][i]
                + vr("bigs")[ind][i]
                + vr("bigs")[sh][i]
                + vr("bigs")[sl][i]
            )
        vr("refr")()


def suspend() -> None:
    vr("d").brightness = 0.02
    vr("force_refr", True)
    vr("lowpow", True)
    cpu.frequency = 80_000_000


def resume() -> None:
    cpu.frequency = 240_000_000
    vr("d").brightness = 1
    vr("lowpow", False)
    vr("force_refr", True)


def batu() -> None:
    if time.monotonic() - vr("batc") > 60:
        vr("j").move(y=17, x=30)
        vr("j").nwrite(str(vr("b").percentage) + "%" + " " * 3)
        vr("refr")()
        vr("batc", time.monotonic())


def lm() -> bool:
    vr("j").clear()
    vr("ctop")(
        "T-Watch Manager (T. W. M.)" + " " * 9 + "v1.0" + (vr("c").size[0] * "-")
    )
    vr("j").move(y=13)
    vr("j").nwrite(vr("c").size[0] * "-")
    vr("j").nwrite(" " * 2 + "\n  ".join(vr("logo")))
    vr("j").move(y=15, x=19)
    vr("j").nwrite("| IP Address:")
    vr("j").move(y=16, x=19)
    vr("j").nwrite("| - " + str(be.devices["network"][0].get_ipconf()["ip"]))
    vr("j").move(y=17, x=19)
    vr("j").nwrite("| Battery: ")
    vr("j").move(y=18, x=19)
    gc.collect()
    gc.collect()
    freeb = gc.mem_free()
    if freeb > 1024:
        freeb = str(freeb // 1024) + "k"
    else:
        freeb = str(freeb)
    vr("j").nwrite("| " + freeb + " bytes free")
    lp = time.monotonic()
    press = 0
    try:
        while True:
            if (not vr("lowpow")) and (time.monotonic() - lp > 6):
                if vr("d").brightness > 0.1:
                    vr("d").brightness -= 0.05
                    time.sleep(0.05)
                else:
                    vr("suspend")()
            vr("clocker")()
            vr("batu")()
            gc.collect()
            t = vr("rk")()
            if t[1] and not vr("lowpow"):
                return False
            elif t[0]:
                if vr("lowpow"):
                    vr("resume")()
                    press = time.monotonic()
                    lp = time.monotonic()
                else:
                    if time.monotonic() - press < 0.8:
                        return True
                    else:
                        vr("suspend")()
            elif vr("lowpow"):
                be.api.tasks.run()
    except KeyboardInterrupt:
        if vr("lowpow"):
            vr("resume")()
        return False


vr(
    "bigs",
    [
        [" _ ", "| |", "|_|"],  # 0 | 0
        ["   ", "  |", "  |"],  # 1 | 1
        [" _ ", " _|", "|_ "],  # 2 | 2
        [" _ ", " _|", " _|"],  # 3 | 3
        ["   ", "|_|", "  |"],  # 4 | 4
        [" _ ", "|_ ", " _|"],  # 5 | 5
        [" _ ", "|_ ", "|_|"],  # 6 | 6
        [" _ ", "  |", "  |"],  # 7 | 7
        [" _ ", "|_|", "|_|"],  # 8 | 8
        [" _ ", "|_|", " _|"],  # 9 | 9
        ["   ", " _ ", "   "],  # - | 10
        [" ", " ", " "],  #   | 11
        [" ", ".", "."],  # : | 12
    ],
)
vr(
    "months",
    [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],
)
vr(
    "days",
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
)
vr(
    "logo",
    [
        ",-----------,",
        "| 4    9.01 |",
        "|           |",
        "|           |",
        "| BERYLLIUM |",
        "'-----------'",
    ],
)
vr("last_shown", [0, 0, 0, 0, 0, 0])
vr("force_refr", False)
vr("ind", False)
vr("batc", -70)
vr("rk", rk)
del rk
vr("rt", rt)
del rt
vr("tsh", tsh)
del tsh
vr("tlh", tlh)
del tlh
vr("ctop", ctop)
del ctop
vr("waitc", waitc)
del waitc
vr("lc", lc)
del lc
vr("ditem", ditem)
del ditem
vr("refr", refr)
del refr
vr("tix", 0)
vr("batu", batu)
del batu
vr("clocker", clocker)
del clocker
vr("lowpow", False)
vr("suspend", suspend)
del suspend
vr("resume", resume)
del resume
vr("lm", lm)
del lm

vrp("ok")
