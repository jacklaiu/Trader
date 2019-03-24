
import StrategyBody as sb
from StrategyBody import TickHandler
import PyBase.Util as util
th = TickHandler()

sb.security = 'L8888.XDCE'

timeArr = util.getTimeSerial(starttime='2019-03-15 14:15:00', count=200000, periodSec=61)
for nowTimeString in timeArr:
    msg = th.handleOneTick(nowTimeString=nowTimeString)