# trace_viewer


It is a tool to parse information from /sys/kernel/debug/tracing/trace

## usage

get trace file from uos and sos by cat /sys/kernel/debug/tracing/trace > xxx_trace.log
prepare period_string.json

* trace_viewer -u uos_trace.log -s sos_trace.log -j period_string.json

    > **Case**: timestamp in trace files is second.
    **Result**: create a time_periods.png.

* trace_viewer -u uos_trace.log -s sos_trace.log -j period_string.json -c

    > **Case**: timestamp in trace files is tsc.
    **Result**: create a time_periods.png.

* trace_viewer -u uos_trace.log -s sos_trace.log -i

    > **Case**: only want to merge uos and sos log, sort by time.
    **Result**: create a merged log and retrun.

* trace_viewer -u uos_trace.log -s sos_trace.log -j period_string.json -t

    > **Case**: want to get a n*n table
    **Result**: create table.txt and time_periods.png.

* trace_viewer -u uos_trace.log -s sos_trace.log -j period_string.json -d

    > **Case**: want to get a detail log
    **Result**: create detail.log and time_periods.png.

* trace_viewer -u uos_trace.log -s sos_trace.log -j period_string.json -o

    > **Case**: want to get each period's wave picture.
    **Result**: create n*n xx_xx.png and time_periods.png.

## json file

* "periods": {"key": "shortname"}

    "key" is the unite key string in the log.
    "shrotname": is the short name for "key".

* "spec": ["shortname","sortname",...]

    define the whole sequence for the log, this will be used to pick all log which match the "spec" defined periods in order.

* "draw_index": {"sos", [index in "spec", index in "spec"]} 

    "sos" or "uos" are support.
    range of index is [0, length of "spec")



## make trace_viewer

pyinstaller -F main.py -n trace_viewer
