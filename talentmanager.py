'''天赋管理器, 用于管理天赋的生成, 触发, 以及天赋的效果'''

from typing import Dict, List, Set, Iterator
from random import choices, sample
from talent import Talent


class TalentManager:
    '''
    天赋管理器, 用于管理天赋的生成, 触发, 以及天赋的效果

    属性:
        grade_count: 天赋等级概率数
        grade_prob: 天赋等级概率
    '''
    grade_count = 4
    grade_prob = [0.889, 0.1, 0.01, 0.001]

    @staticmethod
    def load(config):
        '''
        用于加载天赋配置

        Parameters
        ----------
        config : Dict[str, Dict[str, Any]]
            天赋配置

        Returns
        -------
        None
        '''
        TalentManager._talents: Dict[int, List[Talent]] = {
            i: [] for i in range(TalentManager.grade_count)}
        TalentManager.talentDict: Dict[int, Talent] = {}

        for k in config.keys():
            _t = Talent(config[k])
            TalentManager._talents[_t.grade].append(_t)
            TalentManager.talentDict[_t.id] = _t

    def __init__(self, base, rnd):
        '''
        初始化天赋管理器

        Parameters
        ----------
        base : Life
            人生对象
        rnd : Random
            随机数生成器

        Returns
        -------
        None
        '''
        self._base = base
        self.talents: List[Talent] = []   # 天赋列表
        self.triggered: Set[int] = set()  # 已触发的天赋
        self._rnd = rnd

    def _gen_grades(self):
        '''根据概率生成天赋等级'''
        # 原来的很巧妙也很清晰,但我想要简洁×

        # rnd = self._rnd.random()
        # result = TalentManager.grade_count
        # while rnd > 0:
        #     result -= 1
        #     rnd -= TalentManager.grade_prob[result]
        # return result
        result = choices(population=range(TalentManager.grade_count),
                         weights=TalentManager.grade_prob, k=1)
        return result[0]

    def gen_talents(self, count: int) -> Iterator[Talent]:
        # should not repeats
        '''
        天赋生成器, 用于生成天赋
        返回一个等级从高到低的指定数量的天赋生成器

        Parameters
        ----------
        count : int
            生成的天赋数量

        Yields
        -------
        Iterator[Talent]
            天赋生成器
        '''
        counts = {i: 0 for i in range(TalentManager.grade_count)}
        # 每个等级的天赋数量
        for _ in range(count):
            counts[self._gen_grades()] += 1
        # 从高到低在每个等级中选择天赋
        for grade in range(TalentManager.grade_count - 1, -1, -1):
            # count:在这个等级应该选多少个,_n:实际有多少个
            count = counts[grade]
            _n = len(TalentManager._talents[grade])
            # 该等级的天赋数不够选,就去下一个天赋补齐
            if count > _n:
                counts[grade - 1] += count - _n
                count = _n
            for talent in sample(TalentManager._talents[grade], k=count):
                yield talent

    def update_talent_prop(self):
        '''更新天赋属性'''
        self._base.property.total += sum(t.status for t in self.talents)

    def update_talent(self) -> Iterator[str]:
        '''更新天赋,将已触发的天赋放入triggered列表'''
        for _t in self.talents:
            if _t.id in self.triggered:
                continue
            for res in _t.runTalent(self._base.property):
                self.triggered.add(_t.id)
                yield res

    def add_talent(self, talent: Talent):
        '''
        添加天赋

        Parameters
        ----------
        talent : Talent
            天赋

        Returns
        -------
        None
        '''
        # 保证不重复添加
        for _t in self.talents:
            if _t.id == talent.id:
                return
        self.talents.append(talent)
