from datetime import datetime
import re

def parse_srt_time_range(time_range):
    match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_range)
    if match:
        start_time = convert_srt_time_to_milliseconds(match.group(1))
        end_time = convert_srt_time_to_milliseconds(match.group(2))
        return start_time, end_time
    return 0, 0

def convert_srt_time_to_milliseconds(srt_time):
    hours, minutes, seconds = map(int, srt_time[:-4].split(':'))
    milliseconds = int(srt_time[-3:])
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
