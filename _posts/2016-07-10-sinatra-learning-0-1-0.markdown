---
layout: post_with_octocat
title: sinatra 0.1.0 源码学习
date: 2016-07-10 14:40:17
description: 通过 sinatra 学习 ruby 编程技巧（系列）
categories: ruby
tags: 
- sinatra
- ruby

---

## 声明

本文系 **sinatra 源码系列**第 2 篇。系列的目的是通过 sinatra 学习 ruby 编程技巧。文章按程序运行的先后顺序挑重点分析，前一篇文章分析过的略去不说。水平很有限，所写尽量给出可靠官方/讨论链接，不坑路人。

## 重要提醒

**一定要先安装 1.8 版本的 ruby** ，因为 1.9+ 的 ruby ，String 的实例是不响应 each 方法的，这会直接导致 rack 报错。可以使用 [rvm](https://rvm.io/) 安装 1.8.7 版本的 ruby ，如果使用 rvm ，请先升级到最新版本，否则安装 1.8.7 的 ruby 时也会报错。

列一下本人运行 sinatra 0.1.0 用到的 ruby 和关键 gem 的版本：

- ruby-1.8.7-p374
- rack 1.4.1
- mongrel 1.1.5

## change log

- 支持设置运行环境
- 支持 session
- 支持在路由的资源路径中传入变量
- 增加测试用例
- 支持直接输出静态资源
- 支持渲染 layout
- 增加处理请求完成后的事件回调
- 支持后台日志实时打印

## loader.rb

sinatra 用 Loader 模块来加载/重新加载文件。用到 Set ，无需担心重复加载相同的文件。把 `load_file` 重命名为 `load_files`，也拯救了有强迫症的程序员。

sinatra 接下来将会这样使用 Loader ：

    Sinatra::Loader.load_files Dir.glob(SINATRA_ROOT + '/lib/sinatra/core_ext/*.rb')

要注意如果 core_ext 目录下有多个文件， Dir.glob 是不保证按一定顺序（比如字母顺序）加载文件的，讨论[见此](http://stackoverflow.com/questions/6220753/does-dir-glob-guarantee-the-order)， 1.8.7 版本的 ruby ，其 Set 也不保证 each 的顺序一致，来源[见此](http://stackoverflow.com/questions/6590152/is-the-each-iterator-in-ruby-guaranteed-to-give-the-same-order-on-the-same-elem)。

## kernel.rb

这里扩展了一个很有意思的方法 silence_warnings ，如你所见，就是屏蔽警告用的，用法如下：

    silence_warnings do
      value = noisy_call # no warning voiced
    end

sinatra 只想在调用 silence_warnings 时屏蔽警告，其他时候显示警告。有时候我们也有类似的需求：调用某个方法之前改变某个配置，调用完了再把配置改回去。这涉及到保存配置和处理异常，可以借鉴 sinatra 在此处的做法。

## 继承关系及至对象模型

sinatra 在 core_ext 目录下，先后扩展了 Class, Module, Kernel, Object, Hash 等多个类，它们之间是什么关系呢？这个问题又牵扯到另一个终极问题： ruby 的对象模型是什么？当你清楚 ruby 的对象模型后，众多类之间的关系就不在话下了。

空说无益，先教大家几个探索对象模型的方法，打开 irb ，写两个简单的类：

    class A; end
    class B < A; end

我们知道 B 继承自 A ，B 有一个方法可以显示自己的父类是谁：

    B.superclass #=> A
    # 当 B 继承了 A ，我们就说 A 是 B 的超类（这是 ruby 的中文术语吧，一般都叫父类的）

我们从 B 实例化出一个对象 b ，b 也有方法可以打印自己是属于哪个类的实例：

    b = B.new
    b.class #=> B

我们要知道 ruby 中，类也是实例，如果在类上面调用 class 方法会打印什么呢？

    A.class #=> Class
    B.class #=> Class
    Hash.class #=> Class
    Class.class #=> Class
    Module.class #=> Class

就连在 Class 上调用 class 方法也得到 Class 。这里得出一个结论，所有类都是 Class 类的实例。

我们再回到继承这个话题，除了有办法看到一个类的超类，还有办法看到一个类的祖先链：

    B.ancestors #=> [B, A, Object, Kernel, BasicObject]
    #=> 上面的结果是在 ruby 2.0.0 版本中得到的，你的版本可能有少许不同

可以看到 B 继承自 A ，A 继承自 Object , Object 继承自 Kernel , Kernel 继承自 BasicObject 。嗯，这种说法是不对的，实际上 Object 继承自 BasicObject ， Kernel 模块是被 Object include 进来的：

    class Object < BasicObject
      include Kernel
    end

被 include 进来的模块，都是刚好插入到类的祖先链的超类位置。

你会发现，几乎所有的类的祖先链都包含 Object, Kernel, BasicObject 这三个类：

    A.ancestors #=> [A, Object, Kernel, BasicObject]
    Array.ancestors #=> [Array, Enumerable, Object, Kernel, BasicObject]
    Fixnum.ancestors #=> [Fixnum, Integer, Numeric, Comparable, Object, Kernel, BasicObject]
    String.ancestors #=> [String, Comparable, Object, Kernel, BasicObject]

这三个类可是继承链的发源地啊。

你会发觉我们还没有讲到 Module ， Module 是 Class 的超类：

    Class.ancestors #=> [Class, Module, Object, Kernel, BasicObject]

以上是基础版的 ruby 对象模型，其实也没说多少。

## metaid.rb

sinatra 在这个里做了一个相当顶层的——Object——扩展，要理解这样做的目的，首先要明白 ruby 是怎样寻找一个方法的。打开 irb ，输入：

    class A
      def method_1
        puts 'I am instance method'
      end
    end


首先要知道：方法都是存放在 类 ，而不是类的实例中的。如果类实例调用了某个方法，而在实例的类中找不到该方法，那么会沿着祖先链一直往上面找。如果最终还是找不到，就会转而调用该类的 method_missing 方法，如果该类没定义 method_missing 方法，也会沿祖先链一直往上找，直到 BasicObject(2.3.1 版 ruby ，1.8.7 版 ruby 是在 Kernel 上定义) 的 method_missing 方法。拿上面的例子来说：

    a = A.new
    a.method_1 #=> 'I am instance method'
    class A
      def method_missing(method_name, *args, &block)
        puts "you have called method #{method_name}"
      end
    end

    a.method_2 #=> 'you have called method method_2'

    class B < A; end

    b = B.new
    b.method_1 #=> 'I am instance method'
    b.method_3 #=> 'you have called method method_3'

有时候我们还会定义这样的方法：

    class A
      def self.method_4
        puts 'I am singleton method method_4'
      end

      class << self
        def method_5
          puts 'I am singleton method method_5'
        end  
      end

      def A.method_6
        puts 'I am singleton method method_6'
      end
    end

以上三种方法不同之处只在于名字不同，它们都是类的单例方法（singleton method）。刚说过：“方法都是存放在 类 ，而不是类的实例中的”，单例方法也是如此，它存在于实例的 metaclass 中（或者叫做 eigenclass ，官方称作 singleton class）。metaclass 一直待在我们的视野范围之外，官方没有提供让它们现形的方法， sinatra 要做的就是扩展一套这样的方法。

metaid.rb 第 6、7 行的写法很帅气，但也很难看懂，稍为整理一下：

    def metaclass
      #1
      class << self #2
        #3
        self
      end
    end

    def meta_eval &blk
      metaclass.instance_eval &blk
    end

分析 metaclass 方法，在 #1 处，如果把 self 打印出来，这个 self 会是 Object 的实例（具体得看是谁调用 metaclass 方法）；在 #2 处，运用 ruby 提供的语法 `class << self` ，把 `class << self; self; end` 块中的 self 设置为 Object 实例的 metaclass ；所以在 #3 处，如果把 self 打印出来，这个 self 会是 Object 实例的 metaclass ，而这个 self 会作为块的结果返回， metaclass 方法又将块的结果返回，最终得到 Object 实例的 metaclass 。

附上对 metaclass 的分析参考资料：
- [Metaprogramming Ruby 2: Program Like the Ruby Pros (Facets of Ruby)](https://www.amazon.com/Metaprogramming-Ruby-Program-Like-Facets/dp/1941222129)
- [seeingMetaclassesClearly](http://viewsourcecode.org/why/hacking/seeingMetaclassesClearly.html)
- [Metaprogramming in Ruby: It's All About the Self](http://yehudakatz.com/2009/11/15/metaprogramming-in-ruby-its-all-about-the-self/)

## symbol.rb

在系列第 1 篇文章说过，可以给 Symbol 定义一个 to_proc 方法，方便与 & 操作符配合使用。 sinatra 定义了一个看上去不一样的 to_proc ：

    def to_proc
      Proc.new { |*args| args.shift.__send__(self, *args) }
    end

但做的事情跟第 1 篇文章中的一样。

`*` （splat operator）出现了两次，意义刚好相反，第一次出现是把调用方法时传进来的参数变为一个数组，第二次出现是把一个数组拆散成一个个的参数传到方法中。在 1.8 版本的 ruby ，只要是能响应 to_ary 方法的对象都可以这样用：

    class Foo
      def to_ary
        [1,2,3]
      end
    end

    a, *b = Foo.new #=> a = 1, b = [2,3]

    def some_method(p1,p2,p3)
      p "#{p1} #{p2} #{p3}"
    end

    some_method(*Foo.new) #=> 1 2 3

上面这个例子出自[此处](https://blog.pivotal.io/labs/labs/ruby-pearls-vol-1-the-splat)。

`args.shift` 会删除并返回 args 数组第一个元素。

`__send__` 方法跟 `send` 方法做的事情一样。因为 send 这个单词太普通、常用了，很容易被程序员覆写，所以 ruby 又另外提供一个 `__send__` ，如果不小心覆写这个方法， ruby 会提示警告：

    warning: redefining `__send__' may cause serious problem


附上对这个方法讨论的[链接](http://stackoverflow.com/questions/4658269/ruby-send-vs-send)

## module.rb

module.rb 在 Module 扩展了一个 attr_with_default 方法，这个方法类似 Class 中的 cattr_accessor ，只不过多了个默认值。

这里出现元编程中常见的 `define_method` 方法，它是定义在 Module 中的私有方法，用来动态地生成方法。完整文档可以看[这里](http://ruby-doc.org/core-2.2.0/Module.html)。

一般情况下 `define_method` 只能在定义类时直接调用（此时 self 指向类本身），如：

    class A
      define_method(:m_a) { p 'm_a' }
    end

    A.new.m_a #=> m_a

如果要在实例方法里调用 `define_method` ，这样写会出报找不到方法错误：

    class B
      def create_mehtod(sym, &block)
        define_method(sym, &block)
      end
    end

    B.new.create_method(:m_b) {p 'm_b'} #=> NoMethodError: undefined method `define_method'

回顾 ruby 寻找方法的步骤：先到实例的类中找，找不到就沿着类的祖先链找，打印 B 的祖先链，里面并没有 Module ，这就是出错的原因：

    B.ancestors #=> [B, Object, Kernel]

而在定义类时直接调用 `define_method` 不报错，是因为此时 self 指向 A ，而 A 作为实例的话，它的类是 Class ，打印 Class 的祖先链，里面就有 Module：

    Class.ancestors #=> [Class, Module, Object, Kernel]

在调用 `define_method` 时把 self 指向 B ，还是会报错：

    class B
      def create_mehtod(sym, &block)
        self.class.define_method(sym, &block)
      end
    end

    B.new.create_method(:m_b) {p 'm_b'} #=> NoMethodError: private method `define_method' called for B:Class

因为 `define_method` 是私有方法，不能显式调用，官方文档给出了解决办法：

    class B
      def create_mehtod(sym, &block)
        self.class.send(:define_method, sym, &block)
      end
    end

    b = B.new.create_method(:m_b) {p 'm_b'}
    b.m_b #=> m_b

## request.rb

这里重新打开了 Rack::Request ，扩展了 request_method 方法。这样做的缘由是：html 的 form 元素只支持 GET 和 POST 方法， RESTful 定义的方法至少有 GET/POST/PUT/DELETE 四种，为了让 form 也用上 PUT 和 DELETE 方法， sinatra 检测 POST 请求中的 _method 参数，如果是 PUT 或者 DELETE ，就直接替换 POST 。相关讨论[见此](http://stackoverflow.com/questions/16805956/why-dont-browsers-support-put-and-delete-requests-and-when-will-they)

## environment.rb

在加载完 core_ext 和 rack_ext 目录下的文件后，会加载 sinatra 目录下的文件，一时不知从何下手分析，看到后面有行代码：

    Sinatra::Environment.prepare

就从 environment.rb 说起吧。

**ARGV**

Environment 的 prepare 方法用来解释参数。 `ARGV` 是定义在 Object 中的常量，并且是 Array 的实例，表示在命令行运行脚本文件时传入的参数列表。

## options.rb

parse! 实际上没有用到传进来的参数，它用的还是 ARGV 。

这个版本的 sinatra 开始区分运行脚本的环境（test/development/production），如果当前处在 test 环境， parse! 方法立即返回。

接下来解释参数的任务就交给 [OptionParser](http://ruby-doc.org/stdlib-1.8.7/libdoc/optparse/rdoc/OptionParser.html) 了。

这里有一句 `env.intern` 。 env 是一个 String 实例， intern 方法获取字符串在 ruby 的内部实现（internal representation）。 ruby 最终会把字符串转换为符号，所以这个方法跟 to_sym 方法做一样的事情。 参见[相关讨论](https://www.codecademy.com/en/forum_questions/512a675cf116c52d0d00674b) (PS. 讨论中提及为什么 ruby 给同一个方法取不同的名字，很有启发意义)

## logger.rb

与前一个版本相比，这个文件多了一行代码：

    define_method n do |message|
      @stream.puts message
      @stream.flush #多了这一行
    end

@stream 是一个 IO 实例， flush 方法将 IO 实例中缓存的数据写到操作系统中去（[官方文档](http://ruby-doc.org/core-2.2.3/IO.html#method-i-flush)中解释操作系统仍然有可能缓存起来，所以并没有保证写到设备/文件中）。举个例子，在早期的 ruby 中，下面这段代码会等待 10 秒，然后在同一行打印 5 个点：

    5.times do
      print '.'
      sleep 2
    end

要想每 2 秒打印一个点，可以在 `print '.'` 下面加上一句 `$stdout.flush`。

缓存输出，直到打印换行符或者缓存满了，这个特性来源于 c 言语标准库，初衷应该是减少系统调用。后来不知道是 c 言语标准库还是 ruby 作了改动，修复了上面那个问题。

推荐几篇有关 Ruby IO 的文章：
- [IO in Ruby](https://robots.thoughtbot.com/io-in-ruby)
- [Use of STDOUT.flush after puts](https://www.ruby-forum.com/topic/208856)
- [puts vs print in ruby](https://matt.berther.io/2009/02/11/puts-vs-print-in-ruby/)

## irb.rb

在运行 sinatra 时加上 -c 参数，就会用 console 模式启动 sinatra 。

这个文件只定义了 start! 方法。在 ruby 中定义末尾带感叹号(!)的方法，意味着这个方法比不带感叹号的危险，要小心使用。

start! 方法首先让 Object 加载 TestMethods 模块， `include` 方法是 Object 的私有方法，所以要使用 Object.send 加载（还记得这个技巧在 module.rb 那一节说过吗）。

接着给 Object 类扩展了 reload! 和 show! 两个方法（建议现在就运行 sinatra 的 console 模式，动手玩玩这两个方法）。

show! 调用了 IO.popen 方法。如果你想开一个子进程来调用外部命令，而且还想把外部命令的标准输入和标准输出跟 ruby 连接起来，那这个方法能满足你的需求。 popen 里的 p 指代 pipeline （管道）。管道是进程间通信的一种方式。

举个使用 popen 的例子：

    IO.popen('tail -3', 'w+') do |pipe|
      
      # ruby 会开一个子进程来运行这个 block 
      # 管道中属于 ruby 的这一头会作为参数传进来

      1.upto(100) do { |i| pipe.puts "line #{i}" } 
      pipe.close_write #在读取流之前一定要先把写入关闭，否则读取会阻塞
      puts pipe.read
    end

    # line 98
    # line 99
    # line 100

show! 方法的意图是打开文本编辑器，并写入 TestMethods 模块中的几个方法 status / headers / body 的返回结果。

举个例子，假设你能在命令行使用 `subl` 命令打开 sublime text 。你可以先跳转到 examples/hello 目录下，输入：

    EDITOR=subl ruby hello.rb -c

这时你会进入 irb ，然后输入：

    show!

这时你的 sublime text 就会被打开，里面已经写入了一些内容：

    <!--
            # Status: 404
            # Headers: {"Content-Type"=>"text/html", "Content-Length"=>"0"}
    -->

推荐一本用 ruby 来描述的关于进程的入门书 [理解Unix进程](http://www.ituring.com.cn/minibook/347)，里面有提及进程间通信的方式。

还有几个关于 popen 的文档/讨论
- [IO.popen](http://www.rubydoc.info/stdlib/core/IO.popen)
- [Driving an External Process with popen](https://www.safaribooksonline.com/library/view/ruby-cookbook/0596523696/ch20s08.html)


接下来 sinatra 先清空 ARGV 。如果当前目录（启动 sinatra 时所在的目录，而不是当前文件所在的目录， 运行 `Dir.pwd` 可以看到）下有 '.irbrc' 文件，就把它保存到环境变量中， irb 会在启动时加载这个文件。

当用户退出 irb 时，立即运行 `exit!` ，这样就退出了 sinatra 。

`exit!` 和 `exit` 的区别是前者会跳过退出时的处理程序(比如 at_exit )，前者默认的退出状态是 false ，而后者默认的退出状态是 true ( ruby 不同版本有不同的退出返回值， 1.8.7 版本 `exit` 默认返回 0 ， `exit!` 默认返回 -1 。 unix 会把返回值 0 当成 true ，其它返回值当成 false )。

## server.rb

Server#start 方法首先调用 Server#tail 方法打印 log file 里面的内容。 tail 方法另开一个线程打开 log file ，然后不断地检查（ 1 秒 1 次）它有没有被改动，如果有则打印自上一次文件流的位置到最新文件流的末尾之间的内容。这段代码可以再精简一点：

    File.open(log_file, 'r') do |f|
      loop do
        if f.mtime > last_checked
          last_checked = f.mtime
          puts f.read
        end
      end
    end

IO#read 方法会把 cursor 的位置定位到流的末尾，所以不需要手动调用 IO#seek 重新定位 cursor 的位置，这一点可以在调用 IO#read 之后再 打印 IO#pos 的结果证明。

Server#start 最后调用 Thread#kill 方法杀掉这个线程。这一步很有可能是多余的，因为如果当前线程（ main thread ）结束了，所有其他线程都将会被杀死。

sinatra 用到多进程和多线程，两者的区别以及使用时机可参考[这篇文章](http://jayant7k.blogspot.com/2010/01/for.html)和[这篇文章](http://stackoverflow.com/questions/18575235/what-do-multi-processes-vs-multi-threaded-servers-most-benefit-from)

stackoverflow 的一些讨论：

- [Thread.join blocks the main thread](http://stackoverflow.com/questions/3481866/thread-join-blocks-the-main-thread)

## dispatcher.rb

在开发环境(development)中，sinatra 响应每一个请求前都会重新加载依赖文件以及在命令行中被 ruby 直接执行的脚本文件:

    Loader.reload! if Options.environment == :development

这样在开发环境中改动文件不需要重启就生效。 `Loader.reload!` 方法会重新加载被执行的脚本文件，看上去会产生循环加载的问题，举个例子，跳转到 examples/hello/ 目录下，在命令行中输入：

    ruby hello.rb -c
    # => 通过 require 'sinatra' ， 加载 /lib/sinatra 目录下的相关文件，也把这些文件加载到 loaded_files 中

此时在命令行中输入：

    reload!
    # => 重新加载 loaded_files 中的文件，然后加载 hello.rb 文件

hello.rb 文件中有 `require 'sinatra'` ，这会不会导致 ruby 重新加载 sinatra 呢？

不会。

`Kernel#require` 方法会在 `$LOAD_PATH` 中查找要加载的文件，它也会帮你加上 .rb 或者 .so 文件后缀。比如此处的 `require 'sinatra'` ，它会在 lib/ 目录下找到 sinatra.rb 文件。

已经被 `Kernel#require` 加载过的文件会保存在 `$"` 变量中，`Kernel#require` 不会再次加载已经加载过的文件。

`Kernel#load` 方法要求在使用时写上文件路径以及文件后缀，如果文件路径不是绝对路径，会在 `$LOAD_PATH` 中查找文件。

`Kernel#load` 会再次加载已经加载过的文件。

想关讨论可参考[How does load differ from require in Ruby?](http://stackoverflow.com/questions/3170638/how-does-load-differ-from-require-in-ruby)

ruby 预先定义了不少变量、常量，[这是列表](http://ruby-doc.org/docs/ruby-doc-bundle/Manual/man-1.4/variable.html#dquote)

## sessions.rb

Rack::Session::Cookie 实现了基于 cookie 的 session 管理功能，只要浏览器发过来的 cookie 中有 key 为 session_id 的键值对，Rack 就能借此保存、读取数据。


Rack::Session::Cookie 最初并没有实现基于 session_id 读写数据，所有数据都保存在 env['rack.session'] 下面，源码[见此](https://github.com/rack/rack/commit/417ac6a3d6b394dc2a2d30d9e1235148170dec50)。 0.1.0 的 sinatra 应该就是使用这个最初的实现，通过控制台可以看到 cookie 中直接使用 rack.session 保存加密后的数据。

cookie 功能默认开启，如果要关闭它，可以在加载之后调用 dsl.rb 中定义的 `sessions` 方法：

    sessions :off

sinatra 还提供 `session` 方法返回已保存的 session ，方便使用 cookie 功能，下面是一个例子：

    #!usr/bin/env ruby
    #file examples/you_say.rb
    require 'sinatra'

    get '/' do
      session[:you_say] = params[:you_say] || 'no'
      # 注意 session 和 params 都要用 symbol 作 key
      'hello'
    end

    get '/session' do
      session[:you_say]
    end

先访问 `localhost:4567/?you_say=hi` ，再访问 `localhost:4567/session` ，能看到页面显示 'hi' 。

## event.rb

**EventManager** 负责注册事件、匹配事件。

它调用 `determine_event` 匹配路由、方法，如果匹配不到，就调用 `present_error` 去找用户自定义的 404 路由处理器，如果用户没有预先定义，就调用 `not_found` ，使用默认的 404 处理器。

[Object#method](http://ruby-doc.org/core-1.8.7/Object.html#method-i-method) 根据名字返回方法（或者抛出 NameError 异常），被返回方法的 receiver 就是调用 Object#method 的对象，而且被返回方法就像闭包一样，能访问此对象的实例变量以及方法。举例如下：

    class A
      def initialize(v)
        @k = v
      end

      def get_put_k_method
        method(:put_k)
      end

      def put_k
        puts "k value is #{@k}"
      end

      def get_another
        method(:set_put_k)
      end

      def set_put_k(new_k=nil)
        @k = new_k
        put_k
      end
    end

    a = A.new('hi')
    m = a.get_put_k_method
    m.call #=> k value is hi

    m2 = a.get_another
    m2.call('hello') #=> k value is hello


Event 类把路由匹配交由 Route 处理，还增加了事件处理回调 after_filters 。

StaticEvent 负责处理静态资源，用法跟其他路由一样：

    get '/', 'home'
    static '/p', 'public'
    #请求 '/p/css/bootstrap.css' 会被映射到 'public/css/bootstrap.css'

StaticEvent 的 `attend` 方法中有这样一行： `context.body self` ，之后还定义了 `each` 方法。这样做全因为 Rack 要求 http body 对象响应 each 方法。

`each` 方法用二进制读取模式打开静态文件。 [IO#read](http://ruby-doc.org/core-2.2.0/IO.html#method-i-read) 接受字节长度作为参数，从流中读取指定长度的字节，如果一开始就读到 EOF ，会返回 nil 。

8192 字节（8KB）是常用的 chunk size 。

在设置响应头的 Content-Type 时，用到了`#[]`方法：

    File.extname(@filename)[1..-1]
    # '.rb'[1..-1] => 'rb'

此处传入的 Range 参数（(1..-1)），表示的范围是：从左边数起第 2 个元素到右边数起第 1 个元素。

## renderer.rb

EventContext 加载了 Sinatra::Renderer 模块，此模块为其他渲染方法提供基础方法，比如 Sinatra::Erb 和 Sinatra::Haml ，你还可以定制自己的渲染方法。注释里写了一个定制的例子，如果还有不清楚的地方，可以查看对应的测试用例： renderer_test.rb 。 

`render` 方法会根据参数 renderer ，动态调用真正实现渲染的方法 result_method 。

`render` 方法把传进来的 block 当作 layout 的来源之一。如果请求有对应的 layout ，在第二次调用 result_method 方法时把 layout 当成是 template 参数传进去。

## route.rb

在实例化每个 Event 时，会一并实例化一个 Route 。而每一次调用 `Event#attend` ，会先把 `@route.params` 合并到 `request.params` 中。这就把用户具体的请求路径与路由的 symbol 对应起来。如：

    get '/:controller/:method' do
      "you #{params[:controller]} #{params[:method]}"
    end
    # 当用户请求 '/say/hi' 时
    # 会返回 "you say hi"

`Route#extract_keys` 把路由中的 symbol 提取出来，如：

    temp_arr = "/:some/:words".scan(/:\w+/)
    #=> temp_arr = [":some",":words"]
    temp_arr.map { |raw| eval(raw) } #=> [:some, :words]

`Route#genereate_route` 生成用于匹配用户请求的路由。路由又分两种，带格式(format)和不带格式的，默认格式是 html 。

`Route#to_regex_route` 把路由转换成正则表达式，在点(.)前面加上反斜杠，把 `symbol` 替换成 `'([^\/.,;?]+)'`。在匹配成功后可以用 `captures` 方法找到用户请求的路径。如：

    class A
      def to_regex_route(template)
        /^#{template.gsub(/\./,'\.').gsub(/:\w+/,'([^\/.,;?]+)')}$/
      end
    end
    a = A.new
    reg = a.to_regex_route('/:path/:to/:file.html')
    # reg => (?-mix:^\/([^\/.+,;?])\/([^\/.+,;?])\/([^\/.+,;?])\.html$)
    '/a/b/c.html'.match(reg).captures
    # => ['a','b','c']

`/([^\/.,;?]+)/` 匹配不是斜杠(/)，点(.)，逗号(,)，分号(;)，问号(?)的其他字符。

`Route#recognize` 会在 `Event#attend` 中调用，所以每次都得先清空 `@params` 。

如果成功匹配用户请求的路径，接下来就把 symbol 和具体的路径组合起来：

    @keys.zip(param_values).to_hash

`Array#zip` 方法用法举例：
    
    [1,2,3].zip([4,5,6]) #=> [[1,4],[2,5],[3,6]]

`Array#to_hash` 方法是 sinatra 扩展的。


一些方法参考： 
- [Object#freeze](http://ruby-doc.org/core-1.8.7/Object.html)
- [Array#compact](http://ruby-doc.org/core-1.8.7/Array.html#method-i-compact)
- [Object#dup](http://ruby-doc.org/core-1.8.7/Object.html)
- [What's the difference between Ruby's dup and clone methods?](http://stackoverflow.com/questions/10183370/whats-the-difference-between-rubys-dup-and-clone-methods)

## dsl.rb

dsl.rb 文件的最后调用 `include Sinatra::Dsl` 把 Sinatra::Dsl 模块放到 main 对象祖先链的父节点位置，这样就可以把 Sinatra::Dsl 定义的方法当作实例方法调用。

也可以把 `include Sinatra::Dsl` 替换成 `extend Sinatra::Dsl` ，后者把 Sinatra::Dsl 定义的方法当作单例方法调用。

看出问题了吗？

main 对象同时作为 Object class 的实例以及 Object class 本身去调用方法，否则不能解释它既可以调用实例方法又可以调用单例方法。

有一篇[文章](https://banisterfiend.wordpress.com/2010/11/23/what-is-the-ruby-top-level/)展示了神奇 main 对象。

## test

这一版本补充了单元测试。跑测试用例之前要先安装两个 gem ： mocha(0.5.6), test-spec(0.10.0) 。

还要在 test/helper.rb 文件中，加载 mocha 和 test/sepc 时把 `stringio` 也加载进来，否则 request_test.rb 会跑不过。

helper.rb 里把 `Sinatra::TestMethods` `include` 到 `Test::Unit::TestCase` 中，因而每个测试都可以使用 Sinatra::TestMethods 提供的方法。

`Rack::MockRequest` 让 `Sinatra::TestMethods` 模块里的几个方法不需要产生真实的 http 请求，就能调用到 sinatra 定义的请求处理器。详见[ MockRequest 的文档](http://www.rubydoc.info/github/rack/rack/Rack/MockRequest)。

要跑所有测试用例，可以在根目录下运行：

    find ./test/sinatra -name '*.rb' | xargs -n1 ruby


全文完。