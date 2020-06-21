import asyncio
import aiosqlite
import Debug
from enum import Enum
import os

instructions = []

player_info = {}


class InstructionType(Enum):
    INCREMENT_WIN = 0
    INCREMENT_LOSS = 1
    INCREMENT_STALE = 2
    UPDATE_PLAYER_STATS = 3
    ADD_PLAYER = 4


class Instruction:
    def __init__(self, uid: int, instruction: InstructionType):
        """
        Object that carries Instructions.

        :param uid: Relevant player id.
        :param stat_to_increment: Indicates which stat to increment.
        """
        self.uid = uid
        self.instruction = instruction


async def update_loop():
    db = await aiosqlite.connect('chesscord.db')
    Debug.log("Successfully connected to database probably")
    queue_instruction(-1, InstructionType.UPDATE_PLAYER_STATS)
    while True:
        if len(instructions) != 0:
            instruction_obj: Instruction = instructions[0]

            if instruction_obj.instruction == InstructionType.ADD_PLAYER:
                cursor = await db.execute('SELECT ? FROM player_info', (instruction_obj.uid,))
                data = await cursor.fetchone()
                if len(data) == 0:
                    cursor = await db.execute('INSERT INTO player_info (id, g_played, g_won, g_lost, g_stale)'
                                              'VALUES (?,0,0,0,0)', (instruction_obj.uid,))
                else:
                    Debug.log("PLAYER %s ALREADY IN DATABASE!" % instruction_obj.uid,Debug.LogType.WARNING)

            elif instruction_obj.instruction == InstructionType.UPDATE_PLAYER_STATS:
                cursor = await db.execute('SELECT * FROM player_info')
                data = await cursor.fetchall()
                for row in data:
                    if not row[0] in player_info.keys():
                        player_info[row[0]] = {'Played': row[1], 'Wins': row[2],
                                                'Losses': row[3], 'Stalemates': row[4]}

            instructions.remove(instruction_obj)
        await asyncio.sleep(.1)


def queue_instruction(uid: int, instruction_type: InstructionType) -> None:
    instructions.append(Instruction(uid, instruction_type))


async def _add_player(db: aiosqlite.Connection, uid: int) -> None:
    await db.execute("INSERT INTO player_info(id,g_played,g_won,g_lost,g_stale) VALUES (?,?,?,?)",
                     (uid, 0, 0, 0))


async def _update_player_stats_dict(db: aiosqlite.Connection, uid: int) -> tuple:
    uid, wins, losses, stalemates = await db.execute("SELECT ? FROM player_info", (uid,))
    return uid, wins, losses, stalemates


if __name__ == "__main__":
    pass
