from discord.ext import commands
from util import *

class Quiz(commands.Converter):
    async def convert(self, ctx: commands.Context, arg: str):
        lines = arg.split('\n')
        self.question = lines[0]
        self.ttl = cron_to_seconds([int(x) for x in lines[1].split(' ')])
        self.solution = lines[2]
        self.answers = lines[3:]
        self.emojis = [line[0] for line in lines[3:]]
        print(self.solution)
        if self.solution not in self.emojis:
            raise commands.BadArgument("Solution is not a possible answer")
