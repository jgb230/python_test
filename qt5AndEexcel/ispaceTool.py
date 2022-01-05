#!/usr/bin/python3
from enum import IntFlag

class SpaceName(IntFlag):
    '这个类定义不同信息空间的名字和对应的值'
    # M_SPACE_EVT      =0x0001 #具体事件
    # M_SPACE_EVTC     =0x0002 #事件类
    # M_SPACE_OBJ      =0x0004 #具体对象
    # M_SPACE_OBC      =0x0008 #对象类
    # M_SPACE_OBJ_RS   =0x0010 #对象间关系
    # M_SPACE_OBC_RS   =0x0020 #对象类间关系
    # M_SPACE_OBJ_LAW  =0x0040 #对象规律
    # M_SPACE_EVT_RS   =0x0080 #事件关系
    # M_SPACE_EVTC_RS  =0x0100 #事件类关系
    # M_SPACE_EVTC_LAW =0x0200 #事件类规律
    # M_SPACE_MD_OBC   =0x0400 #人工定义的对象类
    # M_SPACE_MD_EVTC  =0x0800 #人工定义的事件类
    # M_SPACE_RESP     =0x1000 #反应模式空间
    # M_SPACE_OTHER    =0x8000
    具体事件        =0x00000001 #具体事件
    事件类          =0x00000002 #事件类
    具体对象        =0x00000004 #具体对象
    对象类          =0x00000008 #对象类
    对象间关系       =0x00000010 #对象间关系
    对象类间关系     =0x00000020 #对象类间关系
    对象规律        =0x00000040 #对象规律
    事件关系        =0x00000080 #事件关系
    事件类关系       =0x00000100 #事件类关系
    事件类规律       =0x00000200 #事件类规律
    人工定义的对象类  =0x00000400 #人工定义的对象类
    人工定义的事件类  =0x00000800 #人工定义的事件类
    反应模式        =0x00001000 #反应模式
    宏观行为        =0x00002000 #宏观行为
    一般疑问句       =0x00004000 #一般疑问句
    特殊疑问句       =0x00008000 #特殊疑问句
    基础行为        =0x00010000  #基础行为
    大段表达        =0x00020000 #大段表达
    猜想           =0x00040000 #猜想
    祈使           =0x00080000 #祈使
    选择疑问句      =0x00100000 #选择疑问句
    自省           =0x00200000 #自省
    疑问对象        =0x00400000 #疑问对象
    通用           =0x80000000 #通用
    @staticmethod
    def isInSpaceName(spaceId):
        for space in SpaceName:
            if (space in spaceId):
                return True
        return False

    @staticmethod
    def getAllSpace():
        ret=SpaceName.具体事件
        for space in SpaceName:
            if space in SpaceName.getSelfExaSpace():
                continue
            ret |= space
        return ret

    @staticmethod
    def getDataSpace():
        ret=SpaceName.事件类
        for space in SpaceName:
            if space in SpaceName.getWorkSpace() or space in SpaceName.getSelfExaSpace():
                continue
            ret |= space
        return ret

    @staticmethod
    def getWorkSpace():
        #工作空间
        ret=SpaceName.一般疑问句
        for space in SpaceName:
            if space in  [SpaceName.一般疑问句, SpaceName.特殊疑问句, SpaceName.猜想, SpaceName.选择疑问句, SpaceName.祈使, SpaceName.疑问对象]:
                ret |= space
        return ret

    @staticmethod
    def getEventSpace():
        ret=SpaceName.具体事件
        return ret

    @staticmethod
    def getSelfExaSpace():
        ret=SpaceName.自省
        return ret

    @staticmethod
    def reduceSpace(spaceId):
        ret = []
        for space in SpaceName:
            if (space in spaceId):
                ret.append(space)
        return ret

if __name__ == '__main__':
    print(SpaceName.getDataSpace())
    print(SpaceName.一般疑问句 in SpaceName.getWorkSpace())
    print(SpaceName.getEventSpace())