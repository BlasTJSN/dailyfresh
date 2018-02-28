from django.shortcuts import render,redirect
from django.views.generic import View
from goods.models import GoodsCategory,Goods,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner,GoodsSKU
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.urlresolvers import reverse

# Create your views here.

class DetailView(View):
    """商品详细信息页面"""

    def get(self, request, sku_id):
        # 尝试获取缓存数据
        context = cache.get("detail_%s" % sku_id)

        # 如果缓存不存在
        if context is None:
            # 查询商品SKU信息
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                # from django.http import Http404
                # raise Http404("商品不存在!")
                return redirect(reverse("goods:index"))

            # 查询商品分类信息
            categorys = GoodsCategory.objects.all()

            # 从订单中获取评论
            sku_orders = sku.ordergoods_set.all().order_by("-create_time")[:30]
            if sku_orders:
                for sku_order in sku_orders:
                    sku_order.ctime = sku_order.create_time.strftime("%Y-%m-%d %H:%M:%S")
                    sku_order.username = sku_order.order.user.username
            else:
                sku_orders = []

            # 查询新品推荐信息：查询最新发布的两件商品
            new_skus = GoodsSKU.objects.filter(category=sku.category).order_by("-create_time")[:2]

            # 查询其他规格商品：使用exclude()
            # 对象为SPU模型对象
            other_skus = sku.goods.goodssku_set.exclude(id=sku_id)
            # 构造上下文
            context = {
                'sku': sku,
                'categorys': categorys,
                'sku_orders': sku_orders,
                'new_skus': new_skus,
                'other_skus': other_skus,
            }

            # 设置缓存
            cache.set("detail_%s" % sku_id, context, 3600)

        # 查询购物车信息:目前没有实现,暂时设置成0,不能被缓存
        cart_num = 0

        # 如果是登陆用户，需要查询保存在redis中的购物车数据
        if request.user.is_authenticated():

            # 创建连接到redis的对象
            redis_conn = get_redis_connection("default")

            # 调用hgetall()，查询hash对象中所有的数据,返回字典（字典的key和value是bytes类型）
            user_id = request.user.id
            cart_dict = redis_conn.hgetall("cart_%s" % user_id)

            # 遍历字典，读取商品数量，求和
            for val in cart_dict.values():
                cart_num += int(val)

            # 浏览记录存储
            # 需要先去重
            redis_conn.lrem("history_%s" % user_id, 0, sku_id)
            # 再记录用户浏览信息
            redis_conn.lpush("history_%s" % user_id, sku_id)
            # 最多存储5个
            redis_conn.ltrim("history_%s" % user_id, 0, 4)

        # 更新context
        context.update(cart_num=cart_num)

        # 渲染模板
        return render(request, 'detail.html', context)

class IndexView(View):
    """首页"""


    def get(self, request):
        """查询首页页面需要的数据，构造上下文，渲染首页页面"""

        # 查询是否有缓存：存储数据类型和读取数据类型相同
        context = cache.get("index_page_data")
        if context is None:
            # 没有缓存，查询数据

            # 查询用户个人信息，在request.user中

            # 查询商品分类信息
            categorys = GoodsCategory.objects.all()

            # 查询图片轮播信息：按index进行排序，默认从小到大排序
            goods_banners = IndexGoodsBanner.objects.all().order_by("index")

            # 查询商品活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by("index")

            # 查询商品分类列表展示信息
            for category in categorys:
                # 查询此类别中用图片展示的信息
                image_banners = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=1)
                # 更新categorys中的category中的信息
                category.image_banners = image_banners

                # 查询此类别中用标签展示的信息
                title_banners = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=0)
                category.title_banners = title_banners
                # 构造上下文
                context = {
                    "categorys": categorys,
                    "goods_banners": goods_banners,
                    "promotion_banners": promotion_banners,
                }

                # 缓存context:缓存的key 要缓存的内容 超时时间
                cache.set("index_page_data", context, 3600)
        # 查询购物车信息：目前没有实现，暂设为0
        cart_num = 0

        # 如果是登陆用户，需要查询保存在redis中的购物车数据
        if request.user.is_authenticated():

            # 创建连接到redis的对象
            redis_conn = get_redis_connection("default")

            # 调用hgetall()，查询hash对象中所有的数据,返回字典（字典的key和value是bytes类型）
            user_id = request.user.id
            cart_dict = redis_conn.hgetall("cart_%s" % user_id)

            # 遍历字典，读取商品数量，求和
            for val in cart_dict.values():
                cart_num += int(val)

        # 更新context
        context.update(cart_num=cart_num)

        # 渲染模板
        return render(request, "index.html", context)