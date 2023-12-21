import sys, getopt, time
import subprocess as sp
from os import listdir
from os.path import isfile, join, exists

OUTPUT_FILE   = 'consumption.csv'
OUTPUT_HEADER = 'timestamp,domain,measure'
OUTPUT_NL     = '\n'
DELAY_S       = 5
PRECISION     = 5
LIVE_DISPLAY = False
EXPLICIT_USAGE  = None

def print_usage():
    print('python3 nvidiasmi-reader.py [--help] [--live] [--output=' + OUTPUT_FILE + '] [--delay=' + str(DELAY_S) + ' (in sec)] [--precision=' + str(PRECISION) + ' (number of decimal)]')

###########################################
# Read NVIDIA SMI
###########################################
def read_gpu_memory():
    output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
    ACCEPTABLE_AVAILABLE_MEMORY = 1024
    COMMAND = "nvidia-smi --query-gpu=memory.used --format=csv"
    try:
        memory_use_info = output_to_list(sp.check_output(COMMAND.split(),stderr=sp.STDOUT))[1:]
    except sp.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    memory_use_values = [int(x.split()[0]) for i, x in enumerate(memory_use_info)]
    return {}


###########################################
# Main loop, read periodically
###########################################
def loop_read():
    launch_at = time.time_ns()
    while True:
        time_begin = time.time_ns()

        smi_measures = read_gpu_memory()
        output(smi_measures=smi_measures, time_since_launch=int((time_begin-launch_at)/(10**9)))

        time_to_sleep = (DELAY_S*10**9) - (time.time_ns() - time_begin)
        if time_to_sleep>0: time.sleep(time_to_sleep/10**9)
        else: print('Warning: overlap iteration', -(time_to_sleep/10**9), 's')

def output(smi_measures : dict, time_since_launch : int):

    if LIVE_DISPLAY and smi_measures:
        for domain, measure in smi_measures.items():
            print(domain, measure)
        print('---')

    # Dump reading
    with open(OUTPUT_FILE, 'a') as f:
        for domain, measure in smi_measures.items():
            f.write(str(time_since_launch) + ',' + domain + ',' + str(measure) + OUTPUT_NL)
###########################################
# Entrypoint, manage arguments
###########################################
if __name__ == '__main__':

    short_options = 'hlecdv:o:p:'
    long_options = ['help', 'live', 'explicit', 'cache', 'vm=', 'delay=', 'output=', 'precision=']

    try:
        arguments, values = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.error as err:
        print(str(err))
        print_usage()
    for current_argument, current_value in arguments:
        if current_argument in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        elif current_argument in('-l', '--live'):
            LIVE_DISPLAY= True
        elif current_argument in('-o', '--output'):
            OUTPUT_FILE= current_value
        elif current_argument in('-p', '--precision'):
            PRECISION= int(current_value)
        elif current_argument in('-d', '--delay'):
            DELAY_S= float(current_value)

    try:
        # Find domains
        print('>SMI GC found:')
        # Init output
        with open(OUTPUT_FILE, 'w') as f: f.write(OUTPUT_HEADER + OUTPUT_NL)
        # Launch
        loop_read()
    except KeyboardInterrupt:
        print('Program interrupted')
        sys.exit(0)