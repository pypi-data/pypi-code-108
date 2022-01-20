'''
Function:
    淘宝商品数据小爬虫
Author:
    Charles
微信公众号:
    Charles的皮卡丘
'''
import os
import time
import pickle
import random
from DecryptLogin import login


# 中国的成本低, 别国的售价高, 可以赚国际价差
# 淘宝/天猫/ebay/亚马逊
# azon 会帮你储存/包装/分发/物流  (特别省人力成本)

# 把货运到 amonzon日本/am美国 就可以了  (做的是全时间的深意)
# 一次性全网站上架的软体: 台湾虾皮网?







# 邮箱: 可以群发. (这个我是有技术的?)
# 促销的时间: (销售地国家的)有纪念日的时间(其实就是找个借口来做促销) (每个月份肯定都有好几个节日, 都是促销的借口)
# 可以发送促销邮件: 发送祝福感谢信, 并折扣券


# 只要有广告, 就有营业额吗?  (这个广告毕竟是很多营销成本的)
# 需要自己做一个网站吗?



# 一键发送所有社交平台上 (这也是需要用到模拟登录的)
# 社交平台上的产品社交文 :  一周中, 至少要提供3次有效干货或者有趣的东西. (脚踏车需不需要保养呢? 使用短视频讲解干货)
# 文章案例: (还在想父亲节送什么吗? 我们这里有很多适合的脚踏车)

'''淘宝商品数据小爬虫'''
class TBGoodsCrawler():
    def __init__(self, **kwargs):
        if os.path.isfile('session.pkl'):
            self.session = pickle.load(open('session.pkl', 'rb'))
            print('[INFO]: 检测到已有会话文件session.pkl, 将直接导入该文件...')
        else:
            self.session = TBGoodsCrawler.login()
            f = open('session.pkl', 'wb')
            pickle.dump(self.session, f)
            f.close()
    '''外部调用'''
    def run(self):
        search_url = 'https://s.taobao.com/search?'
        while True:
            goods_name = input('请输入想要抓取的商品信息名称: ')
            offset = 0
            page_size = 44
            goods_infos_dict = {}
            page_interval = random.randint(1, 5)
            page_pointer = 0
            while True:
                params = {
                            'q': goods_name,
                            'ajax': 'true',
                            'ie': 'utf8',
                            's': str(offset)
                        }
                response = self.session.get(search_url, params=params)
                if (response.status_code != 200):
                    break
                response_json = response.json()
                all_items = response_json.get('mods', {}).get('itemlist', {}).get('data', {}).get('auctions', [])
                if len(all_items) == 0:
                    break
                for item in all_items:
                    if not item['category']:
                        continue
                    goods_infos_dict.update({len(goods_infos_dict)+1:
                                                {
                                                    'shope_name': item.get('nick', ''),
                                                    'title': item.get('raw_title', ''),
                                                    'pic_url': item.get('pic_url', ''),
                                                    'detail_url': item.get('detail_url', ''),
                                                    'price': item.get('view_price', ''),
                                                    'location': item.get('item_loc', ''),
                                                    'fee': item.get('view_fee', ''),
                                                    'num_comments': item.get('comment_count', ''),
                                                    'num_sells': item.get('view_sales', '')
                                                }
                                            })
                print(goods_infos_dict, "\n---\n")
                self.__save(goods_infos_dict, goods_name+'.pkl')
                offset += page_size
                if offset // page_size > 100:
                    print(f"offset:{offset}")
                    break
                page_pointer += 1
                if page_pointer == page_interval:
                    time.sleep(random.randint(30, 60)+random.random()*10)
                    page_interval = random.randint(1, 5)
                    page_pointer = 0
                else:
                    t = random.random()+2
                    time.sleep(t)
                print("aaa...\n")
            print('[INFO]: 关于%s的商品数据抓取完毕, 共抓取到%s条数据...' % (goods_name, len(goods_infos_dict)))
    '''数据保存'''
    def __save(self, data, savepath):
        fp = open(savepath, 'wb')
        pickle.dump(data, fp)
        fp.close()
    '''模拟登录淘宝'''
    @staticmethod
    def login():
        lg = login.Login()
        infos_return, session = lg.taobao()
        return session






'''run'''
if __name__ == '__main__':
    crawler = TBGoodsCrawler()
    crawler.run()

# 500美金
# 最好一月1w美金


# 从1688

product
# 红海产品
# 实体店是要卖人气产品才有销量.
# 真正赚钱的是 利基产品. (小众但有需求量的产品)
# 挑选新的利基产品: 1688
# 20-80块美金之间. (客户购买不会有太多考虑)
# 小于1公斤. 不大于1个鞋盒.
# 还有有周边产品?
place
promote
