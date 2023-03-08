from discord.ext import commands

WEEKS = 7 * 24 * 60 * 60
DAYS = 24 * 60 * 60
HOURS = 60 * 60
MINUTES = 60


class QuizRequest(commands.Converter):
    async def convert(self, ctx: commands.Context, arg: str):
        lines = arg.split('\n')
        self.question = lines[0]
        self.ttl = cron_to_seconds([int(x) for x in lines[1].split(' ')])
        self.solutions = lines[2].split()
        self.answers = lines[3:]
        self.emojis = [line[0] for line in lines[3:]]
        if not set(self.solutions).issubset(set(self.emojis)):
            raise commands.BadArgument(
                "At least one solution is not a possible answer")
        self.creator_id = ctx.author.id
        self.channel_id = ctx.channel.id
        self.message_id = ctx.message.id
        return self


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
