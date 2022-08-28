import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import sse
import sse_plot


def init():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='$', intents=intents)

    @bot.command()
    async def sync(ctx):
        await bot.tree.sync()

    @bot.hybrid_command()
    @app_commands.describe(
        # Descriptions borrowed from sse.f
        mass='mass is in solar units.',
        z='z is metallicity in the range 0.0001 -> 0.03 where 0.02 is Population I.',
        tphysf='tphysf is the maximum evolution time in Myr.',

        neta='neta is the Reimers mass-loss coefficent (neta*4x10^-13; 0.5 normally).',
        bwind='bwind is the binary enhanced mass loss parameter (inactive for single).',
        hewind='hewind is a helium star mass loss factor (1.0 normally).',
        sigma='sigma is the dispersion in the Maxwellian for the SN kick speed (190 km/s).',

        ifflag='ifflag > 0 uses WD IFMR of HPE, 1995, MNRAS, 272, 800 (0).',
        wdflag='wdflag > 0 uses modified-Mestel cooling for WDs (0).',
        bhflag='bhflag > 0 allows velocity kick at BH formation (0).',
        nsflag='nsflag > 0 takes NS/BH mass from Belczynski et al. 2002, ApJ, 572, 407 (1).',
        mxns='mxns is the maximum NS mass (1.8, nsflag=0; 3.0, nsflag=1).',
        idum='idum is the random number seed used in the kick routine.'
    )
    async def evolve(ctx, mass, z, tphysf,
                     neta=0.5, bwind=0.0, hewind=0.5, sigma=190.0,
                     ifflag=0, wdflag=1, bhflag=0, nsflag=1, mxns=3.0, idum=999,
                     pts1=0.05, pts2=0.01, pts3=0.02):
        await sse.construct_evolve_in(mass, z, tphysf,
                                      neta=neta, bwind=bwind, hewind=hewind, sigma=sigma,
                                      ifflag=ifflag, wdflag=wdflag, bhflag=bhflag, nsflag=nsflag, mxns=mxns, idum=idum,
                                      pts1=pts1, pts2=pts2, pts3=pts3)
        stdout = await sse.run_sse()
        if 'STOP' in stdout:
            # An error has occured in evolv1
            await ctx.send(f'```{stdout}```')
        else:
            await ctx.send(f'```{stdout}```', file=discord.File('sse/evolve.dat'))

    @bot.hybrid_command()
    @app_commands.describe(
        # Descriptions borrowed from sse.f except for xbounds and ybounds
        mass='mass is in solar units.',
        z='z is metallicity in the range 0.0001 -> 0.03 where 0.02 is Population I.',
        tphysf='tphysf is the maximum evolution time in Myr.',

        xbounds='x-axis bounds for the plot.',
        ybounds='y-axis bounds for the plot.',

        neta='neta is the Reimers mass-loss coefficent (neta*4x10^-13; 0.5 normally).',
        bwind='bwind is the binary enhanced mass loss parameter (inactive for single).',
        hewind='hewind is a helium star mass loss factor (1.0 normally).',
        sigma='sigma is the dispersion in the Maxwellian for the SN kick speed (190 km/s).',

        ifflag='ifflag > 0 uses WD IFMR of HPE, 1995, MNRAS, 272, 800 (0).',
        wdflag='wdflag > 0 uses modified-Mestel cooling for WDs (0).',
        bhflag='bhflag > 0 allows velocity kick at BH formation (0).',
        nsflag='nsflag > 0 takes NS/BH mass from Belczynski et al. 2002, ApJ, 572, 407 (1).',
        mxns='mxns is the maximum NS mass (1.8, nsflag=0; 3.0, nsflag=1).',
        idum='idum is the random number seed used in the kick routine.'
    )
    async def plot(ctx, mass, z, tphysf,
                   xbounds='default', ybounds='default',
                   neta=0.5, bwind=0.0, hewind=0.5, sigma=190.0,
                   ifflag=0, wdflag=1, bhflag=0, nsflag=1, mxns=3.0, idum=999,
                   pts1=0.05, pts2=0.01, pts3=0.02):
        await sse.construct_evolve_in(mass, z, tphysf,
                                      neta=neta, bwind=bwind, hewind=hewind, sigma=sigma,
                                      ifflag=ifflag, wdflag=wdflag, bhflag=bhflag, nsflag=nsflag, mxns=mxns, idum=idum,
                                      pts1=pts1, pts2=pts2, pts3=pts3)
        stdout = await sse.run_sse()
        await sse_plot.sse_plot(xbounds, ybounds)
        if 'STOP' in stdout:
            # An error has occured in evolv1
            await ctx.send(f'```{stdout}```')
        else:
            await ctx.send(f'```{stdout}```', file=discord.File('hrdiag.png'))

    bot.run(TOKEN)


if __name__ == '__main__':
    init()
