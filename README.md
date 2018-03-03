# dailyfresh
天天生鲜电商项目

1.创建dailyfresh项目


2.创建应用cart,goods,orders,users


3.定义模型类

3.1.分别在users、goods、orders应用中定义好对应的模型类

3.2.cart应用中暂时不定义模型类，其中的数据是使用redis数据库维护的

3.3 安装itsdangerous模块


4.User模型

4.1.users应用中的模型类User是使用Django自带的用户认证系统维护的，Django中默认开启用户认证模块中间件

4.2.迁移前，需要在settings.py文件中设置：AUTH_USER_MODEL = '应用.用户模型类',即AUTH_USER_MODEL = 'users.User'


5.增加导包路径

5.1.原因：在settings.py中设置AUTH_USER_MODEL时，编码规则为'应用.用户模型类'

5.2.但是，应用在apps/文件目录下，为了保证正确的编码，我们需要增加导包路径

5.3.同时，为了配合AUTH_USER_MODEL的配置，应用的安装直接使用users，不要使用apps.users

5.4.
 import sys
  sys.path.insert(1, os.path.join(BASE_DIR, 'apps'))


6.URL配置

6.1.安装pymysql

6.2.配置模板加载路径

6.3.配置静态文件加载路径


7.模型迁移


8.展示注册页面

9.展示注册页面

9.1.在users中定义注册页面视图，使用类视图

9.2.准备模板

9.3.匹配url


10.实现注册逻辑

10.1.获取注册请求参数

10.2.教研注册请求参数

10.2.1前后端的校验需要分离：前端检验完，数据到服务器后继续校验，避免黑客绕过客户端发请求

10.2.2提示：出现异常的处理方式，根据公司具体需求来实现

10.3保存用户注册信息

10.3.1.隐私信息需要加密，可以直接使用django提供的用户认证系统完成，不需要save()

10.3.2.调用create_user(user_name, email, password)实现用户保存和加密隐私信息，参数顺序不能错

10.3.3.IntegrityError异常用于判断用户是否重名、已注册，这样可以减少访问数据库频率

10.3.4.保存完用户注册信息后，需要重置用户激活状态，因为Django用户认证系统默认激活状态为True


11.实现邮件激活

11.1定义邮件激活类视图

11.2使用itsdangerous模块生成激活token

11.2.1生成用户激活token的方法封装在User模型类中.

Serializer()生成序列化器，传入混淆字符串和过期时间.

dumps()生成user_id加密后的token，传入封装user_id的字典.
返回token字符串.

loads()解出token字符串，得到用户id明文.

11.3Celery异步发送激活邮件

11.3.0配置邮件服务器和发件人sender

11.3.1创建Celery异步任务文件celery_tasks/tasks.py

11.3.2.创建应用对象/客户端/client

Celery()：

参数1是异步任务路径.

参数2是指定的broker.

redis://密码@redis的ip:端口/数据库.

redis://192.168.243.191:6379/4.

返回客户端应用对象app.

send_active_email()：内部封装激活邮件内容，并用装饰器@app.task注册.

调用python的send_mail()将激活邮件发送出去.

11.3.3将redis数据库作为中间人borker

11.4实现激活逻辑


12.实现登陆逻辑


13.登陆记住用户

13.1安装django-redis模块，配置django-redis

13.2设置session时间来实现记住用户逻辑


14.退出登陆


15.提供用户地址信息

15.1定义用户地址类视图

15.2限制页面访问

15.2.1@login_required装饰器，实现只允许登陆用户访问的功能

15.2.1.1注意使用@login_required装饰器时需要配置settings.py,添加LOGIN_URL = '/users/login'，指定验证失败后跳转到的路径。

15.2.2如果是登陆用户，则进入被装饰的视图，如果不是登陆用户，则跳转到settings.py中指定的路径，并且在路径中添加?next="进入被装饰视图的匹配路径"

15.2.3装饰类视图时，采取多继承的方法

15.2.4定义一个拓展类用来重写as_view方法，并将装饰器装饰在这个拓展类的as_view方法返回的视图上。将这个拓展类封装为一个模块，放在utils中

15.2.5用户地址类视图继承拓展类和View类，根据MRO排序，拓展类中super().as_view()方法会在View类中找到并调用，以此完成类视图的装饰及调用


16.给登陆视图添加next跳转功能

16.1.?next=""通过GET请求获取相关数据

17收货地址页面视图编写

17.1最新收货地址数据显示，通过模型类获取用户地址数据，通过GET请求渲染模板

17.2提交编辑的新地址，通过POST请求获取提交的数据，向数据库添加新数据


18个人信息页面视图编写

18.1也需要验证登录用户

18.2获取用户信息，方法同收货地址视图

18.3浏览记录获取
18.3.1通过把不同用户的id作为键，商品SKUid作为值存入redis中

18.3.2在个人信息视图中建立与redis的连接，获取对应用户对应的skuid

18.3.3按浏览排序取出GoodsSKU中对应id中相关数据,因为从redis中取数据的顺序和存数据相反，所以要新建一个列表把取出的数据添加进去，保证与存入的顺序即浏览顺序一致

18.3.4渲染模板

19抽离父模板

19.1 继承父模板重写收货地址，个人信息模板

20.安装FastDFS服务器

20.1使用FastDFS服务器存储图片数据。使用nginx读取FastDFS服务器的图片数据

21完成Django对接FastDFS流程

21.1整体流程
21.1.1浏览器后台站点发布图片，向Django发出上传图片请求
21.1.2Django得到上传图片请求信息，调用上传图片方法client.upload_by_buffer(file_data),调用fdfs客户端
21.1.3fdfs客户端得到上传请求信息，传递请求信息到FastDFS服务器,通过client.conf传递到指定的服务器
21.1.4tracker得到请求信息，查询可用的storage，再通过client.conf返回可用的storage的ip和端口到fdfs客户端
21.1.5fdfs客户端把图片传给指定的storage
21.1.6storage接收图片，将上传的图片写入服务器，同时生成存储位置的file_id，把status+file_id+文件名+Storage_IP返回给fdfs客户端
21.1.7fdfs客户端判断是否上传成功，返回file_id到Django
21.1.8Django把file_id存储到数据库
21.1.9用户访问页面，向Django发出html请求，通过模板中的标签查询数据库中图片的file_id
21.1.10使用nginx从服务器磁盘中读取图片数据，渲染html页面

21.2安装fdfs_client,用于fdfs与Django的交互

21.3实现自定义文件存储系统storage

21.3.1建立自定义文件存储系统目录结构utils/fastdfs/client.conf,utils/fastdfs/storage.py

21.3.2配置settings.py中Django自定义的存储系统

21.3.3在storage.py中实现自定义存储系统类的代码逻辑

21.4测试自定义文件存储系统后台站点上传图片
21.4.1本地化
21.4.2注册模型类到后台站点
21.4.3创建超级管理员并登陆进入到后台站点
21.4.4发布内容

22.添加富文本编辑器功能

23.后台站点上传图片数据，数据库加入商品数据

24.主页商品信息展示
24.1定义主页类视图
24.2渲染index.html模板

25.页面静态化
25.1celery生成静态html,在task.py中渲染模板static_index.html
25.2配置nginx访问静态html,在/usr/local/nginx/conf中配置
25.3模型管理类地啊用celery异步方法,在admin.py中封装BaseAdmin类

26.动态主页html缓存
26.1判断是否存在缓存，不存在就执行数据查询缓存
26.2购物车是实时变化的不能被缓存
26.3缓存需设置有效时间，才能让数据更新

27.实现主页购物车，数量统计
27.1购物车数据保存在redis中，使用hash格式cart_userid sku_id count

28.实现详情页面
28.1查询商品SKU信息，查询所有商品分类信息，查询商品订单评论信息，查询新商品推荐，查询其他规格商品，如果已登陆，查询购物车信息
28.2实现存储浏览记录的逻辑

29.实现商品列表页面
29.1查询商品分类信息，查询新品推荐信息，查询商品列表信息，查询商品分页信息，查询购物车信息

30.全文检索
30.1安装haystack应用
30.2在settings.py文件中配置搜索引擎
30.3在要索引的表的应用下创建search_indexes.py文件，定义商品索引类GoodsSKUIndex()，继承自indexes.SearchIndex和indexes.Indexable
30.4在templates下新建目录search/indexes/goods,新建goodssku_text.txt，并编辑要建立索引的字段
30.5 生成索引文件 python manage.py rebuild_index
30.6搜索表单处理
30.7配置搜索地址正则
30.8编写search.html模板
30.9 使用中文分词工具jieba

31.购物车
31.1定义添加购物车视图
31.2实现用户登陆时添加购物车视图和模板渲染，购物车数据存储在redis中
31.3实现未登录时添加购物车视图和模板渲染，购物车数据存储在cookie中
31.4登陆后将cookie中的数据合并到redis中


