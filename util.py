
WEEKS = 7 * 24 * 60 * 60
DAYS = 24 * 60 * 60
HOURS = 60 * 60
MINUTES = 60


def cron_to_seconds(cron: list[int]) -> int:
    res = cron[0]
    res += MINUTES * cron[1]
    res += HOURS * cron[2]
    res += DAYS * cron[3]
    res += WEEKS * cron[4]
    return res


def seconds_to_cron(seconds: int) -> list[int]:
    weeks = seconds // WEEKS
    seconds -= weeks * WEEKS
    days = seconds // DAYS
    seconds -= days * DAYS
    hours = seconds // HOURS
    seconds -= hours * HOURS
    minutes = seconds // MINUTES
    seconds -= minutes * MINUTES
    return [seconds, minutes, hours, days, weeks]


def cron_to_string(cron: list[int]) -> str:
    return str(cron[4]) + " week(s) " + str(cron[3]) + " day(s) " + str(cron[2]) + " hour(s) " + str(cron[1]) + " minute(s) " + str(cron[0]) + " second(s)"


def seconds_to_string(seconds: int) -> str:
    return cron_to_string(seconds_to_cron(seconds))
