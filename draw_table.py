#!/usr/bin/env python3

import cairo
from basic_method import Paint
import time

TITLE = 300
PERIODPIXEL = 300
TITLESPACE = 200
TIMEALXE = 200
US2PIXEL = 100
SOS2UOSPIXEL = 200
PERIOD_SIZE = 70

class Domain():
    def __init__(self, paint, sx, sy, name):
        self.pat = paint
        self.win_sx = sx
        self.win_sy = sy
        self.ncpu = 1
        self.time_axis_step = 5
        self.name = name

    def init(self, periods, table, period_dict):
        delta_list = []
        for x in periods:
            tmp = {}
            tmp_list = []
            start_p = x[0]
            end_p = x[1]
            tmp_list.append(table[1][start_p])
            tmp_list.append(table[1][end_p])
            tmp["data"] = tmp_list
            start_key = [k for k, v in period_dict.items() if v == str(start_p)]
            end_key = [k for k, v in period_dict.items() if v == str(end_p)]
            tmp["period"] = "[{}us]{}-->{}".format(round(tmp_list[1]-tmp_list[0],1),
                                                   start_key[0],
                                                   end_key[0])
            delta_list.append(tmp)

        self.delta_list = delta_list
        self.nperiod = len(delta_list)
        self.utime = int(table[1][-1])
        self.win_hi = self.ncpu * self.nperiod * PERIODPIXEL
        self.win_wi = self.utime * US2PIXEL


    def fill(self):
        # print title
        title_s = "{} time period".format(self.name)
        sx = self.win_sx - 60
        sy = self.win_sy - TIMEALXE
        self.pat.paint_text(sx, sy, title_s)

        # print time axis 5us
        step = self.time_axis_step
        nline = list(range(0, round(self.utime/step)))
        for x in nline:
            sx = self.win_sx + nline.index(x) * US2PIXEL * step - 60 # -6 move text to centor
            sy = self.win_sy - 30
            self.pat.paint_text(sx, sy, "{}us".format(x*5))
        self.pat.paint_matrix_with_colume(self.win_sx,
                                          self.win_sy,
                                          self.win_wi,
                                          self.win_hi)
        for d in self.delta_list:
            x = d["data"]
            sx = self.win_sx +  \
                x[0] * US2PIXEL
            sy = self.win_sy + 50 +  \
                self.delta_list.index(d) *  \
                PERIODPIXEL # 1us = 10 point
            wi = (x[1] - x[0]) * US2PIXEL
            hi = PERIODPIXEL - 100 # 30-10=20
            self.pat.paint_matrix(sx,sy,wi,hi)
            self.pat.paint_text_size(sx+20, sy+hi-60, d["period"], PERIOD_SIZE)

    def get_end_y(self):
        return self.win_sy + self.win_hi

class Painter():
    def __init__(self, pat):
        self.pat = pat
        self.sos = None
        self.uos = None

    def init(self, data):
        print("Paint sos")
        periods = data["periods"]
        sx = 100
        sy = TITLESPACE + TIMEALXE + TITLE
        sos = Domain(self.pat, sx, sy , "SOS")
        sos.init(periods["sos"], data["delta"], data["period_dict"])
        self.sos = sos

        print("Paint uos")
        end_y = sos.get_end_y()
        sy = end_y + TITLESPACE + TIMEALXE + SOS2UOSPIXEL
        uos = Domain(self.pat, sx, sy, "UOS")
        uos.init(periods["uos"], data["delta"], data["period_dict"])
        self.uos = uos


    def start_painting(self):
        # print title
        sx = 0
        sy = 200
        self.pat.paint_title(sx, sy, "SOS_UOS time periods chart", 200)
        self.sos.fill()
        self.uos.fill()
        # print time
        sx = self.pat.wi - 1500
        sy = self.pat.hi - 100
        time_s = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        self.pat.paint_text(sx, sy, time_s)


def draw(data):
    table = data["delta"]
    wi = table[1][-1]*US2PIXEL + 500 # add 50 pixel
    np = len(data["periods"]["sos"]) + len((data["periods"]["uos"]))
    hi = np*PERIODPIXEL + TITLESPACE*2 + TIMEALXE*2 + SOS2UOSPIXEL + TITLE + 300 # add 30 pixel

    print("draw table:",wi,hi)
    wi = int(wi)
    hi = int(hi)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, wi, hi)
    ctx = cairo.Context(surface)
    pat = Paint(ctx)
    pat.init(wi, hi, US2PIXEL)
    ptr = Painter(pat)
    ptr.init(data)
    ptr.start_painting()
    # cpu number should provide
    surface.write_to_png("time_periods.png")
    print("finish draw table")

def main():

    data={}
    tmp = {}
    tmp["sos"] = [[1,2],[1,3],[1,4],[1,5],[3,5]]
    tmp["uos"] = [[1,2],[1,3],[1,4],[2,5],[3,5]]
    table = [[0,0,0,0,0,0]
             [0,10,12,15,68,100],
             [0,30,31,32,33,35],
             [0,30,31,32,33,35],
             [0,30,31,32,33,35],
             [0,30,31,32,33,35]]

    data["periods"] = tmp
    data["delta"] = table
    draw(data)

if __name__ == '__main__':
    main()
