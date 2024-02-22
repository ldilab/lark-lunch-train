from typing import Union, Tuple


def detect(s: str) -> Union[Tuple[str, str], None]:
    if not s.startswith("/lunchtrain"):
        return

    if not ("에" in s and "에서" in s):
        return

    s = s.split("/lunchtrain")[1].strip()
    eh_index = s.index("에")
    es_index = s.index("에서")
    if eh_index > es_index:
        # XXX에서 YYY에
        place = s.split("에서")[0].strip()
        time = s.split("에서")[1].split("에")[0].strip()
    else:
        # YYY에 XXX에서
        time = s.split("에")[0].strip()
        place = s.split("에")[1].split("에서")[0].strip()

    # if time is not in form of HH:MM
    if len(time.split(":")) != 2:
        return

    if not time.split(":")[0].isdigit() or not time.split(":")[1].isdigit():
        return

    return place, time
