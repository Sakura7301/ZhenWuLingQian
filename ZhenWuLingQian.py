import random  
import time  
import os   
import io  
import plugins  
from bridge.context import ContextType  
from bridge.reply import Reply, ReplyType  
from common.log import logger 
from plugins import *  

@plugins.register(  
    name="ZhenWuLingQian",  # 插件名称  
    desire_priority=99,  # 插件优先级  
    hidden=False,  # 是否隐藏  
    desc="玄天上帝真武灵签",  # 插件描述  
    version="1.0",  # 插件版本  
    author="sakura7301",  # 作者  
)  
class ZhenWuLingQian(Plugin):  
    def __init__(self):  
        super().__init__()  # 调用父类的初始化 
        self.cards = list(range(1, 50))  
        self.shuffle()  
        # 注册处理上下文的事件  
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context  
        logger.info("[ZhenWuLingQian] 插件初始化完毕")  

    # 洗牌  
    def shuffle(self):  
        """使用当前时间作为种子进行洗牌"""  
        seed = int(time.time() * 1000000) % (2**32)  
        random.seed(seed)  
        random.shuffle(self.cards)  
        logger.debug(f"洗牌完成！使用种子：{seed}")  

    # 抽牌  
    def draw_card(self, n):  
        """抽取第n张牌"""  
        if not isinstance(n, int):  
            return "请输入整数！"  
        if n < 1 or n > 49:  
            return "请输入1-49之间的数字！"  
        return self.cards[n-1]  

    def get_local_image(self, number):  
        """在指定目录下查找指定数字前缀的图片"""  
        if not isinstance(number, int) or number < 1 or number > 59:  
            logger.error(f"数字必须在1-100之间，当前数字：{number}")  
            return None  

        # 获取目标目录的完整路径  
        target_dir = "./plugins/ZhenWuLingQian/image"     
        
        # 确保目录存在  
        if not os.path.exists(target_dir):  
            logger.error(f"目录不存在：{target_dir}")  
            return None  
        
        # 生成匹配的文件名模式  
        patterns = [  
            f"{number:02d}_",     
            f"{number}_"          
        ]  
        
        for filename in os.listdir(target_dir):  
            if filename.endswith('.png'):  
                for pattern in patterns:  
                    if filename.startswith(pattern):  
                        full_path = os.path.join(target_dir, filename)  
                        logger.debug(f"找到匹配图片：{filename}")  
                        return full_path  
                        
        logger.error(f"未找到数字{number}对应的签文图片")  
        return None  

    def ZhenWuLingQian(self):  
        """  
        读取本地图片并返回BytesIO对象  
        """  
        # 随机抽签
        # 获取当前时间戳（微秒级）  
        current_time = time.time()  
        # 取小数部分后的6位  
        microseconds = int(str(current_time).split('.')[1][:6])  
        # 映射到1-49范围  
        gen_random_num = microseconds % 49 + 1
        # 获取图片路径
        image_path = self.get_local_image(gen_random_num)  
        
        if image_path and os.path.exists(image_path):  
            try:  
                # 读取图片内容并创建BytesIO对象  
                with open(image_path, 'rb') as f:  
                    image_content = f.read()  
                image_io = io.BytesIO(image_content)  
                logger.info(f"成功读取图片：{image_path}")  
                return image_io  
            except Exception as e:  
                logger.error(f"读取图片失败：{e}")  
                return None  
        return None 

    def ZhenWuLingQianNum(self, number):  
        """读取本地图片并返回BytesIO对象"""  
        # 抽签  
        card_num = self.draw_card(number)  
        # 获取图片路径  
        image_path = self.get_local_image(card_num)  
        
        if image_path and os.path.exists(image_path):  
            try:  
                # 读取图片内容并创建BytesIO对象  
                with open(image_path, 'rb') as f:  
                    image_content = f.read()  
                image_io = io.BytesIO(image_content)  
                logger.info(f"成功读取图片：{image_path}")  
                return image_io  
            except Exception as e:  
                logger.error(f"读取图片失败：{e}")  
                return None  
        return None  

    def ZhenWuLingQianRequest(self, query): 
        # 定义占卜关键词列表
        divination_keywords = ['抽签','真武灵签', '每日一签']
        return any(keyword in query for keyword in divination_keywords)

    def JieQianRequest(self, query):
        # 定义占卜关键词列表
        divination_keywords = ['解签']
        return any(keyword in query for keyword in divination_keywords)

    def on_handle_context(self, e_context: EventContext):  
        """处理上下文事件"""  
        if e_context["context"].type not in [ContextType.TEXT]:  
            logger.debug("[ZhenWuLingQian] 上下文类型不是文本，无需处理")  
            return  
        
        content = e_context["context"].content.strip()  
        logger.debug(f"[ZhenWuLingQian] 处理上下文内容: {content}")  

        if self.ZhenWuLingQianRequest(content):  
            logger.info("[ZhenWuLingQian] 抽签")  
            reply = Reply()  
            image = self.ZhenWuLingQian()  # 获取灵签  
            reply.type = ReplyType.IMAGE if image else ReplyType.TEXT  
            reply.content = image if image else "抽签失败啦，待会再试试吧~🐾"  
            e_context['reply'] = reply  
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑   
        elif self.JieQianRequest(content):
            logger.info("[ZhenWuLingQian] 解签")
            reply = Reply()
            reply.content = f"签文都给你啦😾！你自己看看嘛~🐾"
            reply.type = ReplyType.TEXT
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑 


    def get_help_text(self, **kwargs):  
        """获取帮助文本"""  
        help_text = "输入'抽签'可得得到灵签哦~🐾\n"  
        return help_text