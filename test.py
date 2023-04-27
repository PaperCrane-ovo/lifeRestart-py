import random
import traceback
import msvcrt

from talent import Talent
from life import Life
from talentmanager import TalentManager

Life.load('data')


def genp(prop):
    ps = []
    for i in range(3):
        ps.append(id(i) % (int(prop * 2 / (4 - i)) + 1))
        if(10 < ps[-1]):
            ps[-1] = 10
        prop -= ps[-1]
    if(10 < prop):
        prop += sum(ps)
        ps = [int(prop / 4)] * 3
        prop -= sum(ps)
    return {
        'CHR': ps[0],
        'INT': ps[1],
        'STR': ps[2],
        'MNY': prop
    }


def run():
    life = Life()
    life.set_error_handler(lambda e: traceback.print_exc())
    life.set_talent_handler(lambda ts: random.choice(ts).id)
    life.set_property_handler(genp)

    life.choose()
    #life.property.INT = 10

    life.talent.talents.append(TalentManager.talentDict[1048])
    life.talent.talents.append(TalentManager.talentDict[1065])
    life.talent.talents.append(TalentManager.talentDict[1134])

    # life.event.triggered.add(40063)

    for t in life.talent.talents:
        print(t)

    return life.run()


while True:
    i = 0
    for x in run():
        print(f'\n{x[0]}{"——".join(x[1:])}', end='', flush=True)
        if(0 < i):
            i -= 1
            continue
        if(msvcrt.getch() == b' '):
            i = 9
    print("\n\n[人生重开了]")
    if (msvcrt.getch() == b'q'):
        break
