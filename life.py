'''Life模块'''
import os
import random
import itertools
from typing import Callable, Dict, List, Iterator
import json

from eventmanager import EventManager
from agemanager import AgeManager
from talent import Talent
from propertymanager import PropertyManager
from talentmanager import TalentManager


class HandlerException(Exception):
    '''异常处理,继承了Exception基类'''

    def __init__(self, msg):
        super().__init__(msg)


class Life:
    '''
    人生类

    属性:
        _talent_inherit: 继承的天赋数量
        _talent_finalist: 最终天赋数量
    '''

    _talent_choose = 3
    _talent_finalist = 10

    @property
    def _talent_randomized(self):
        '''为玩家分配的随机天赋的数量,如果有继承就返回非继承数,否则返回最终数'''
        return Life._talent_finalist - 1 if self._talent_inherit else Life._talent_finalist

    @staticmethod
    def load(datapath):
        '''
        将数据加载到各个Manager中

        Parameters
        ----------
        datapath : str
            数据路径

        Returns
        -------
        None
        '''
        with open(os.path.join(datapath, 'talents.json'), encoding='utf8') as fp:
            TalentManager.load(json.load(fp))
        with open(os.path.join(datapath, 'age.json'), encoding='utf8') as fp:
            AgeManager.load(json.load(fp))
        with open(os.path.join(datapath, 'events.json'), encoding='utf8') as fp:
            EventManager.load(json.load(fp))
        # with open(os.path.join(datapath, 'achievement.json'), encoding='utf8') as fp:
        #    EventManager.load(json.load(fp))

    def _init_managers(self):
        '''
        初始化各个Manager并加载到Life类中
        '''
        self.property: PropertyManager = PropertyManager(self)
        self.talent: TalentManager = TalentManager(self, self._rnd)
        self.age: AgeManager = AgeManager(self)
        self.event: EventManager = EventManager(self, self._rnd)

    def __init__(self, rnd=None):
        self._talent_inherit = None                                     # 继承的天赋数量
        self._talenthandler: Callable[[List[Talent]], int] = None       # 天赋处理器
        self._propertyhandler: Callable[[int], Dict[str, int]] = None   # 属性处理器
        self._errorhandler: Callable[[Exception], None] = None          # 异常处理器
        self._rnd = rnd or random.Random()                              # 随机数生成器
        self._init_managers()

    def restart(self, inhert_num=None):
        '''
        重置游戏状态,并重新初始化各个Manager,可以选择继承的天赋数量

        Parameters
        ----------
        inhert_num : int, optional
            继承的天赋数量,默认为None

        Returns
        -------
        None
        '''
        next_tms = self.property.TMS + 1
        if inhert_num:
            self._talent_inherit = self.talent.talents[inhert_num - 1]
        self._init_managers()
        self.property.TMS = next_tms

    def _prefix(self) -> Iterator[str]:
        '''返回当前人物属性的迭代器'''
        yield f'【{self.property.AGE}岁/颜{self.property.CHR}智{self.property.INT}体{self.property.STR}钱{self.property.MNY}乐{self.property.SPR}】'

    def setErrorHandler(self, handler: Callable[[Exception], None]) -> None:
        '''
        设置异常处理器

        Parameters
        ----------
        handler : Callable[[Exception], None]
            处理函数

        Returns
        -------
        None
        '''
        self._errorhandler = handler

    def setTalentHandler(self, handler: Callable[[List[Talent]], int]) -> None:
        '''
        设置收到天赋的处理器

        Parameters
        ----------
        handler : Callable[[List[Talent]], int]
            处理函数

        Returns
        -------
        None
        '''
        self._talenthandler = handler

    def setPropertyhandler(self, handler: Callable[[int], List[int]]) -> None:
        '''
        设置属性分配的处理器

        Parameters
        ----------
        handler : Callable[[int], List[int]]
            处理函数

        Returns
        -------
        None
        '''
        self._propertyhandler = handler

    def _alive(self):
        '''判断是否还活着

        Returns
        -------
        bool
            是否还活着
        '''
        return self.property.LIF > 0

    def run(self) -> Iterator[List[str]]:
        '''
        生成按年拆分的游戏信息的生成器
        使用`age.grow()`增加玩家年龄,添加玩家获得的新天赋,运行事件并生成当年的信息.

        Yields
        -------
        Iterator[List[str]]
            按年拆分的游戏信息的生成器
        '''
        while self._alive():
            self.age.grow()
            for t in self.age.getTalents():
                self.talent.add_talent(t)

            tal_log = self.talent.update_talent()
            evt_log = self.event.runEvents(self.age.getEvents())

            yield list(itertools.chain(self._prefix(), evt_log, tal_log))

    def choose(self):
        '''
        随机选择天赋和属性

        Returns
        -------
        None
        '''
        talents = list(self.talent.gen_talents(self._talent_randomized))
        if self._talent_inherit is not None:
            talents.insert(0, self._talent_inherit)
        tdict = {t.id: t for t in talents}
        while len(self.talent.talents) < Life._talent_choose:
            try:
                t = tdict[self._talenthandler(talents)]
                for t2 in self.talent.talents:
                    if t2.isExclusiveWith(t):
                        raise HandlerException(f'你选择的天赋和{t2}不能同时拥有')
                self.talent.add_talent(t)

                talents.remove(t)
                tdict.pop(t.id)
            except Exception as e:
                self._errorhandler(e)

        self.talent.update_talent_prop()

        while True:
            try:
                eff = self._propertyhandler(self.property.total)
                pts = [eff[k] for k in eff]
                if sum(pts) != max(self.property.total, 0) or max(pts) > 10 or min(pts) < 0:
                    raise HandlerException(
                        f'property allocation points incorrect:{self.property.total}{pts}')
                self.property.apply(eff)
                break
            except Exception as e:
                self._errorhandler(e)
