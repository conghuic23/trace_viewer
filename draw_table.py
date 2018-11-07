#!/usr/bin/env python3

import cairo
from basic_method import Paint
import time
import copy

MAX_WIDTH = 10000
WISPACE = 500
HISPACE = 300
TITLE = 300
PERIODPIXEL = 300
TITLESPACE = 20
TIMEALXE = 100
SOS2UOSPIXEL = 200
PERIOD_SIZE = 70

us2pixel = 10



class Domain():
    def __init__(self, paint, sx, sy, name, timeunit):
        self.pat = paint
        self.win_sx = sx
        self.win_sy = sy
        self.ncpu = 1
        self.n_axis = 20
        self.name = name
        self.timeunit = timeunit

    def init(self, periods, table, period_dict, period_spec):
        delta_list = []
        for x in periods:
            tmp = {}
            tmp_list = []
            start_p = x[0]
            end_p = x[1]
            tmp_list.append(table[1][start_p+1])
            tmp_list.append(table[1][end_p+1])
            tmp["data"] = tmp_list
            start_key = [k for k, v in period_dict.items() if v == period_spec[start_p]]
            end_key = [k for k, v in period_dict.items() if v == period_spec[end_p]]
            tmp["period"] = "[{}{}]{}-->{}".format(round(tmp_list[1]-tmp_list[0],1),
                                                   self.timeunit,
                                                   start_key[0],
                                                   end_key[0])
            delta_list.append(tmp)

        self.delta_list = delta_list
        self.nperiod = len(delta_list)
        self.time = int(table[1][-1])
        self.win_hi = self.ncpu * self.nperiod * PERIODPIXEL
        self.win_wi = self.time * us2pixel


    def fill(self):
        # print title
        title_s = "{} time period ({})".format(self.name, self.timeunit)
        sx = self.win_sx - 60
        sy = self.win_sy - TIMEALXE
        self.pat.paint_text_size(sx, sy, title_s, 100)

        # print time axis 5us
        # support axis [5, 50, 500, 5000]
        pre_step = int(self.time/self.n_axis)
        if pre_step < 25:
            step = 5
        elif pre_step < 250:
            step = 50
        elif pre_step < 2500:
            step = 500
        else:
            step = 5000

        nline = list(range(0, round(self.time/step)))
        for x in nline:
            sx = self.win_sx + nline.index(x) * us2pixel * step - 60 # -6 move text to centor
            sy = self.win_sy - 30
            self.pat.paint_text(sx, sy, "{}".format(x*step))
        self.pat.paint_matrix_with_colume(self.win_sx,
                                          self.win_sy,
                                          self.win_wi,
                                          self.win_hi,
                                          step*us2pixel)
        for d in self.delta_list:
            x = d["data"]
            sx = self.win_sx +  \
                x[0] * us2pixel
            sy = self.win_sy + 50 +  \
                self.delta_list.index(d) *  \
                PERIODPIXEL # 1us = 10 point
            wi = (x[1] - x[0]) * us2pixel
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

    def init(self, data, timeunit):
        print("Paint sos")
        periods = data["periods"]
        sx = 100
        sy = TITLESPACE + TIMEALXE + TITLE
        sos = Domain(self.pat, sx, sy , "SOS", timeunit)
        sos.init(periods["sos"], data["delta"], data["period_dict"], data["period_spec"])
        self.sos = sos

        print("Paint uos")
        end_y = sos.get_end_y()
        sy = end_y + TITLESPACE + TIMEALXE + SOS2UOSPIXEL
        uos = Domain(self.pat, sx, sy, "UOS", timeunit)
        uos.init(periods["uos"], data["delta"], data["period_dict"], data["period_spec"])
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
        self.pat.paint_text_size(sx, sy, time_s, 100)

def trans_us2ms(table):
    table_ms = copy.deepcopy(table)
    for i in range(1,len(table)):
        for j in range(1,len(table[0])):
            table_ms[i][j]=round(table[i][j]/1000,1)
    return table_ms

def draw(data):
    global us2pixel

    table = data["delta"]
    wi = MAX_WIDTH + WISPACE
    us2pixel = round((MAX_WIDTH/table[1][-1]),1)
    timeunit = 'us'

    if not us2pixel:
        print("time period is large than 1s, will change unit from us to ms!!!")
        table = trans_us2ms(table)
        print(table)
        timeunit = 'ms'
        us2pixel = round((MAX_WIDTH/table[1][-1]),1)
        print(us2pixel, MAX_WIDTH, table[1][-1])
        data["delta"] = table

    print("us2pixel:",us2pixel)
    if "uos" not in data["periods"].keys():
        data["periods"]["uos"] = []

    if "sos" not in data["periods"].keys():
        data["periods"]["sos"] = []

    np = len(data["periods"]["sos"]) + len((data["periods"]["uos"]))
    hi = np*PERIODPIXEL + TITLESPACE*2 + TIMEALXE*2 + SOS2UOSPIXEL + TITLE + HISPACE# add 30 pixel

    print("draw table:",wi,hi)
    wi = int(wi)
    hi = int(hi)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, wi, hi)
    ctx = cairo.Context(surface)
    pat = Paint(ctx)
    pat.init(wi, hi, us2pixel)
    ptr = Painter(pat)
    ptr.init(data, timeunit)
    ptr.start_painting()
    # cpu number should provide
    surface.write_to_png("time_periods.png")
    print("finish draw table")

def main():

    data={}
    tmp = {}
    tmp["sos"] = [[1,2],[1,3],[1,4],[1,5],[3,5]]
    tmp["uos"] = [[1,2],[1,3],[1,4],[2,5],[3,5]]
    table = [[0,0,0,0,0,0],
             [0,10,12,150,68,50000],
             [0,30,31,32,303,35000],
             [0,30,31,302,330,35000],
             [0,30,31,32,33,35],
             [0,30,31,32,33,35]]

    data["periods"] = tmp
    data["delta"] = table
    data["period_dict"] = {
        "period 1":"1",
        "period 2":"2",
        "period 3":"3",
        "period 4":"4",
        "period 5":"5"
    }
    draw(data)

if __name__ == '__main__':
    main()
