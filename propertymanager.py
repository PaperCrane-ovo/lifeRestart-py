'''属性管理模块'''
from typing import Dict, Set


class PropertyManager:
    '''属性管理类,用于管理人物的各项属性'''

    def __init__(self, base):
        '''
        用于初始化属性管理类

        Parameters
        ----------
        base : Life
            人生类

        Returns
        -------
        None
        '''
        self._base = base
        self.CHR = 0  # 颜值 charm CHR
        self.INT = 0  # 智力 intelligence INT
        self.STR = 0  # 体质 strength STR
        self.MNY = 0  # 家境 money MNY
        self.SPR = 5  # 快乐 spirit SPR

        self.AGE = -1  # 年龄 age AGE
        self.LIF = 1  # hp

        self.total = 20  # 总属性点数

        self.TMS = 1  # 时间 time TMS
        self.AVT = []  # 天赋 available talent AVT

    def __str__(self):
        '''个人属性字符串化'''
        return f'属性：颜值{self.CHR} 智力{self.INT} 体质{self.STR} 家境{self.MNY} 快乐{self.SPR}'

    @property
    def TLT(self) -> Set[int]:  # 天赋 talent TLT
        return self._base.talent.triggered

    @property
    def EVT(self) -> Set[int]:
        return self._base.event.triggered

    def apply(self, effect: Dict[str, int]):
        '''
        应用属性变化

        Parameters
        ----------
        effect : Dict[str, int]
            属性变化

        Returns
        -------
        None
        '''

        for key in effect:
            # 如果key是RDM则为随机属性,随机选择一个属性进行变化
            if key == "RDM":
                k = ['CHR', 'INT', 'STR', 'MNY', 'SPR'][id(key) % 5]
                setattr(self, k, getattr(self, k) + effect[key])
                continue
            setattr(self, key, getattr(self, key) + effect[key])
