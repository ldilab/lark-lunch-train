from typing import Union, Tuple


def detect(s: str) -> Union[None, str, tuple[str, str]]:
    if not s.startswith("/lunchtrain"):
        return "Invalid format. Please use `/lunchtrain` [place]에서 [time]에."

    if not ("에" in s and "에서" in s):
        return "Invalid format. Please use /lunchtrain [place]`에서` [time]`에`."

    s = s.split("/lunchtrain")[1].strip()
    eh_index = s.index("에 ")
    es_index = s.index("에서 ")
    if es_index < eh_index:
        # XXX에서 YYY에 ZZZ
        place = s.split("에서")[0].strip()
        time = s.split("에서")[1].split("에")[0].strip()
    else:
        # YYY에 XXX에서 ZZZ
        time = s.split("에")[0].strip()
        place = s.split("에")[1].split("에서")[0].strip()

    # if time is not in form of HH:MM
    if len(time.split(":")) != 2:
        return f"Invalid time format (time: {time}). Please use HH:MM."

    if not time.split(":")[0].isdigit() or not time.split(":")[1].isdigit():
        return f"Invalid time format (time: {time}). Please use HH:MM."

    return place, time
