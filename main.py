#!/usr/bin/env python3

import xlsxwriter
import sys
import re
import json
import argparse
import os
from prettytable import PrettyTable
from pyecharts import Line
from pyecharts_snapshot.main import make_a_snapshot
from draw_table import draw
import gc

linestart = "*****************************************"
steps = 1
CPU_FREQ = 1881
tsc = 0

def get_data_list(filename, add_dict, prefix):
    print("open file {}".format(filename))
    whole_list  = []
    if tsc:
        pa = re.compile(r'\d+: .+:')
    else:
        pa = re.compile(r'\d+.\d+: .+:')
    with open(filename, 'r') as f:
        for line in f.readlines():
            tmp_dict={}
            try:
                tmp_dict["additional"] = ""
                if add_dict:
                    for key in add_dict.keys():
                        if key in line:
                            tmp_dict["additional"] = add_dict[key]
                            tmp_dict["fullinfo"] = prefix + line
                            t = pa.findall(line)[0].split(":")
                            tmp_dict["period"] = t[1].strip()
                            tmp_dict["timestamp"] = float(t[0])
                            whole_list.append(tmp_dict)
                else:
                    t = pa.findall(line)
                    if t:
                        t = t[0].split(":")
                        tmp_dict["additional"] = " "
                        tmp_dict["fullinfo"] = prefix + line
                        tmp_dict["period"] = t[1].strip()
                        tmp_dict["timestamp"] = float(t[0])
                        whole_list.append(tmp_dict)
            except Exception as e:
                print("LINE:",line)
                print(e)
                print("ERROR !!! if use tsc timestamp,",
                      "please add '-c' option!!")
                sys.exit()
    print("get {} data".format(len(whole_list)))
    return whole_list

def record_maxvalue_timpstamp(last, current):
    return last if last > current else current

def record_minvalue_timpstamp(last, current):
    return last if last < current else current

def calculate_delta(data, start_s, end_s, len_s):
    delta_list = []
    max_steps = steps

    line = 0
    while line < (len(data)-len_s):
        start = data[line+start_s]["timestamp"]
        end = data[line+end_s]["timestamp"]
        delta = {}
        # change s -> us, keep to 0.1us
        if tsc:
            # tsc
            delta["value"] = round((end-start)/CPU_FREQ,1);
        else:
            # second
            delta["value"] = round((end - start)*1000000,1)
        delta["end_ts"] = end
        delta_list.append(delta)

        line += len_s
    return delta_list



def print_data(data):
    tmp_data = sorted(data, key=lambda x:x["value"])
    try:
        max_value = tmp_data[-1]["value"]
        min_value = tmp_data[0]["value"]
        sum = 0
        for d in data:
            sum = sum + d["value"]
        average_value = round(sum/len(data), 1)
    except:
        print("ERROR: could not print anything, data is None")
        print("ERROR: please check xxx###xxx file, make sure periods json is correct")
        sys.exit()


    print("\033[0;32mLEN {}\nMAX {}us\nMIN {}us\nAVERAGE {}us\n\033[0m".
          format(len(data),
                 max_value,
                 min_value,
                 average_value))
    return "{},{},{}".format(max_value,min_value,average_value)


def wirte_log_with_steps(f, data_list, wholeinfo, end_s):
    for m in data_list:
        suit_list = [x for x in wholeinfo if
                     (x["timestamp"] == m and
                      x["additional"] == end_s)]
        for s in suit_list:
            index = wholeinfo.index(s)
            begin = 0 if (index-steps < 0) else (index-steps)
            end = len(wholeinfo) if (index+steps) > len(wholeinfo) else (index+steps)
            f.write("\n=========== num {} =============\n".
                    format(data_list.index(m)+1))
            for x in range(begin, end):
                if x == index:
                    f.write("###### right here! #######\n")
                f.write(wholeinfo[x]["fullinfo"])

"""
def save_statistic_log(filename, data, wholeinfo, period, end_s):
    if filename is None:
        return

    tmp_data = sorted(data, key=lambda x:x["value"])
    max_value = tmp_data[-1]
    min_value = tmp_data[0]
    # in case there are multi max and min value
    max_list = []
    min_list = []
    for d in tmp_data:
        if d["value"] == max_value["value"]:
            max_list.append(d["end_ts"])
        if d["value"] == min_value["value"]:
            min_list.append(d["end_ts"])

    with open(filename, "a+") as f:
        # max value
        f.write("@ {} @".format(period))
        f.write("\n\nmax value {}: num:{} \n".format(max_value["value"],
                                                 len(max_list)))
        '''
        current only print one record to save time.
        If needed, whole max_list can be print out.
        change max_list[0] -> max_list
        The same with min_list
        '''
        wirte_log_with_steps(f, [max_list[0]], wholeinfo, end_s)
        # min value
        f.write("@ {} @".format(period))
        f.write("\n\nmix value {}: num:{} \n".format(min_value["value"],
                                                 len(min_list)))
        wirte_log_with_steps(f, [min_list[0]], wholeinfo, end_s)
"""

def save_picture(name, data, p_path):
    if len(data) == 0 or p_path is None:
        return
    data_value = [x["value"] for x in data]
    line = Line(name, background_color='#EAEAEA')
    attr = list(range(0, len(data_value)))
    line.add("delta", attr, data_value,
             mark_point=["max", "min"],
             mark_line=["average"])
    render_file = "{}/{}.html".format(p_path, name)
    picture_file = "{}/{}.png".format(p_path, name)
    line.render(path=render_file,)
    make_a_snapshot(render_file, picture_file)
    print("save picture {}.png in {}".format(name, p_path))


def parse_init():
    parser= argparse.ArgumentParser()
    parser.add_argument('-u', '--uosfile',
                        required=True,
                        help='uos file path')
    parser.add_argument('-s', '--sosfile',
                        required=True,
                        help='sos file path')
    parser.add_argument('-j', '--json',
                        required=False,
                        help='period string json file')
    parser.add_argument('-d', '--detaillog',
                        action='store_true',
                        default=False,
                        required=False,
                        dest="detaillog",
                        help='enable detail info store detail.log')
    parser.add_argument('-e', '--errorfile',
                        action='store_true',
                        default=False,
                        required=False,
                        dest="errorfile",
                        help='enable error info error.log ')
    parser.add_argument('-t', '--tablefile',
                        action='store_true',
                        default=False,
                        required=False,
                        dest="tablefile",
                        help="enable delta data table : table.txt")
    parser.add_argument('-o', '--outpicture',
                        action='store_true',
                        default=False,
                        required=False,
                        dest="outpicture",
                        help="enable output all png picture for delta \
                        data in out_picture/xxx")
    parser.add_argument('-c', '--tsc',
                        action='store_true',
                        default=False,
                        required=False,
                        dest="tsc_en",
                        help="timestamp is tsc")
    parser.add_argument('-i', '--ignore_period_only',
                        action='store_true',
                        default=False,
                        required=False,
                        dest="ignoreperiod",
                        help="ignore period in json file, store whole sorted log, then exit!!")
    return parser

def generate_period_pairs(size):
    table = []
    for i in range(0, size):
        for j in range(0, size):
            if j>i:
                table.append("{},{}".format(i,j))
    return table

def save_table(size, table, table_file):
    print("size:",size)
    li = range(0, size)
    li = [str(x) for x in li]
    title = ['runtime/us'] + li
    x = PrettyTable(title)
    x.padding_width =1
    for i in range(1, size+1):
        table[i][0] = i-1
        x.add_row(table[i][:])
    table_txt = x.get_string()
    with open(table_file,'w') as f:
        f.write(table_txt)

def find_whole_flow_data(period_spec, data):
    new_data = []
    print(period_spec)

    step = len(period_spec)  # step, from 1
    raw_add = [x["additional"] for x in data]
    raw_add_len = len(raw_add)  # get data size
    start_l = [x[0] for x in enumerate(raw_add) if x[1] == period_spec[0]] # get all start point
    # get all index which meet condition
    all_index = [list(range(x,x+step)) for x in start_l
                 if x+step < raw_add_len and raw_add[x:x+step] == period_spec]
    indexs = [n for a in all_index for n in a]
    new_data = [data[x] for x in indexs]
    return new_data

def prepare_draw_data(table, period, period_dict, period_spec):
    data = {}
    size = len(table)
    n_table = [[0 for i in range(size)] for i in range(size)]
    for i in range(1, size):
        for j in range(1, size):
            if table[i][j] != 0:
                n_table[i][j] = float(table[i][j].split(",")[-1])
    data["delta"] = n_table
    data["periods"] = period
    data["period_dict"] = period_dict
    data["period_spec"] = period_spec
    return data

def pick_and_sorted(c_file, uos_file, sos_file, period_dict):
    uos_file_data = get_data_list(uos_file, period_dict, "[UOS] ")
    sos_file_data = get_data_list(sos_file, period_dict, "[SOS] ")

    merge_data = uos_file_data + sos_file_data
    print("merge data len: {}".format(len(merge_data)))

    print("start to sort ... ")

    sorted_data = sorted(merge_data, key=lambda x:x["timestamp"])

    print("sort done")

    with open(c_file, "w") as f:
        if period_dict:
            for d in sorted_data:
                line = "{}:\t\t\t{}\t{}\n".format(d["period"], d["timestamp"], d["additional"])
                f.write(line)
        else:
            for d in sorted_data:
                line = "{}\n".format(d["fullinfo"])
                f.write(line)

    return sorted_data

def check_spec(spec, period_dict):
    periods_list = []
    for k in period_dict.keys():
        periods_list.append(period_dict[k])
    for s in spec:
        if s not in periods_list:
            print("ERROR: '{}' is not support in 'periods'".format(s))
            return -1
    return 0


def check_draw_index(draw_index, periods, maxindex):
    avai_idx = range(0, maxindex)
    for k in draw_index.keys():
        for idx in draw_index[k]:
            if len(idx) != 2 or \
                (idx[0] not in avai_idx) or \
                (idx[1] not in avai_idx):
                print("ERROR: index {} is not in range of 'spec'!".format(idx))
                return -1

    return 0

def load_json(json_file):
    with open(json_file, "r", encoding='utf-8') as f:
        info_dict = json.loads(f.read())
        if info_dict is None:
            print("ERROR: please prepare period strings first!")
            sys.exit()
        period_dict = info_dict.get("periods", None)
        period_spec = info_dict.get("spec", None)
        draw_index = info_dict.get("draw_index", None)
        if period_dict is None:
            print("ERROR: please check json file, make sure 'periods' \
                  is provided")
            sys.exit()

        if period_spec is None:
            print("WARNING: as 'spec' not provided,",
                  "will use periods from period_dict")
            # create a period_spec from period_dict
            val = []
            for k in period_dict.keys():
                val.append(int(period_dict[k]))
            val.sort()
            period_spec = [str(x) for x in val]
            print("auto generate spec: {}".format(period_spec))

        if check_spec(period_spec, period_dict):
                sys.exit()

        if draw_index is None:
            print("WARNING: as draw_index not provided, time period table",
                  "will not create!!")
        else:
            if check_draw_index(draw_index, period_dict, len(period_spec)):
                sys.exit()

    return period_dict, period_spec, draw_index


"""
processing will create a n*n table, statistic all delta between each period
n is the length of period_spec + 1
+ 1  is because the first raw and column are use to save period number.

table[]=
---------------------------------------------
runtime(us)   |   0|   1|  2|  3|  4|  5|  6|
--------------+----+----+---+---+---+---+---|
0             |   0|   x|  x|  x|  x|  x|  x|
--------------+----+----+---+---+---+---+---|
1             |    |   0|  x|  x|  x|  x|  x|
--------------+----+----+---+---+---+---+---|
2             |    |    |  0|  x|  x|  x|  x|
--------------+----+----+---+---+---+---+---|
3             |    |    |   |  0|  x|  x|  x|
--------------+----+----+---+---+---+---+---|
4             |    |    |   |   |  0|  x|  x|
--------------+----+----+---+---+---+---+---|
5             |    |    |   |   |   |  0|  x|
--------------+----+----+---+---+---+---+---|
6             |    |    |   |   |   |   |  0|
---------------------------------------------
table[2][1] = index_1_timestamp - index_0_timestamp
"""
def processing(period_spec, period_index, period_dict, complete_data, p_path):
    table = [[0 for i in range(len(period_spec)+1)] for i in range(len(period_spec)+1)]
    print("table: {}*{}".format(len(table),len(table)))
    for p in period_index:
        print(linestart)
        print(p)
        a,b = p.split(",")
        a = int(a)
        b= int(b)
        delta = calculate_delta(complete_data,a,b,len(period_spec))
        a_name = [k for k,v in period_dict.items() if period_spec[a]==v]
        b_name = [k for k,v in period_dict.items() if period_spec[b]==v]
        per = "{}({}_{}) --> {}({}_{})".format(b_name[0],period_spec[b],b,a_name[0],period_spec[a],a)
        print("get delat value for index \033[4;37;44m{},{}\033[0m\n".format(a,b))
        print('\033[4;36;40m'+per+'\033[0m\n')
        table[a+1][b+1]=print_data(delta)
        save_picture("{}_{}-{}_{}".format(period_spec[a],a,period_spec[b],b), delta, p_path)

    return table


def main():
    global steps
    global tsc
    parser = parse_init()
    args = parser.parse_args()

    uos_file = args.uosfile
    sos_file = args.sosfile
    d_file = "detail.log" if args.detaillog else None
    json_file = args.json
    t_file = "table.txt" if args.tablefile else None
    p_path = "out_pictures" if args.outpicture else None
    tsc = 1 if args.tsc_en else 0
    ignore_period = 1 if args.ignoreperiod else 0

    if ignore_period:
        pick_and_sorted("ignore_period.log",uos_file,sos_file,None)
        print("only create ignore_period.log, then exit")
        sys.exit()

    if p_path and not os.path.exists(p_path):
        os.makedirs(p_path)


    c_file = "{}####{}".format(uos_file, sos_file)

    print("load json file {} ...".format(json_file))
    period_dict, period_spec, draw_index = load_json(json_file)
    period_index = generate_period_pairs(len(period_spec))

    print("pick records from log file and sort...")
    sorted_data = pick_and_sorted(c_file,uos_file,sos_file, period_dict)
    print("pick and sorted done")

    print("find whole records match:  {}".format(period_spec))
    complete_data = find_whole_flow_data(period_spec, sorted_data)
    if len(complete_data) != 0:
        print("find {} sets of records :)")
    else:
        print("ERROR: no complete periods, please check {} :(".format(c_file))
        sys.exit()


    # save complete data
    if d_file:
        with open(d_file, "w") as f:
            for d in complete_data:
                line = "{}".format(d["fullinfo"])
                f.write(line)

    print("start to calculate...")
    table = processing(period_spec, period_index, period_dict, complete_data, p_path)
    # save table.txt
    if t_file:
        save_table(len(period_spec), table, t_file)
    # create a time axls table
    if draw_index:
        print("draw periods table")
        data = prepare_draw_data(table, draw_index, period_dict, period_spec)
        draw(data)

if __name__ == "__main__":
    main()

