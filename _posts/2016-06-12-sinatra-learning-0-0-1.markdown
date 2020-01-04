---
layout: post_with_octocat
title: sinatra 0.0.1 源码学习
date: 2016-06-12 20:14:30
excerpt: 通过 sinatra 学习 ruby 编程技巧（系列）
categories: ruby
tags: 
- sinatra
- ruby
---

## 声明

本文系 **sinatra 源码系列**第 1 篇。系列的目的是通过 sinatra 学习 ruby 编程技巧。文章按程序运行的先后顺序挑重点分析，前一篇文章分析过的略去不说。水平很有限，所写尽量给出可靠官方/讨论链接，不坑路人。

## 重要提醒

**一定要先安装 1.8 版本的 ruby** ，因为 1.9+ 的 ruby ，String 的实例是不响应 each 方法的，这会直接导致 rack 报错。可以使用 [rvm](https://rvm.io/) 安装 1.8.7 版本的 ruby ，如果使用 rvm ，请先升级到最新版本，否则安装 1.8.7 的 ruby 时也会报错。

列一下本人运行 sinatra 0.0.1 用到的 ruby 和关键 gem 的版本：

- ruby-1.8.7-p374
- rack 1.4.1
- mongrel 1.1.5

## 前期准备

把 [sinatra](https://github.com/sinatra/sinatra)克隆下来，用 `git tag` 可以看到最开始的版本是 0.0.1 。

checkout 到 0.0.1 分支可以看到目录十分简单

    ├── examples
    │   └── hello
    │       ├── test.rb
    │       └── views
    │           └── index.erb
    ├── files
    │   ├── default_index.erb
    │   └── not_found.erb
    ├── lib
    │   ├── sinatra
    │   │   ├── core_ext
    │   │   │   ├── class.rb
    │   │   │   └── hash.rb
    │   │   ├── dispatcher.rb
    │   │   ├── dsl.rb
    │   │   ├── event.rb
    │   │   ├── logger.rb
    │   │   └── server.rb
    │   └── sinatra.rb
    ├── test
    │   ├── helper.rb
    │   └── sinatra
    │       ├── dispatcher_test.rb
    │       └── event_test.rb
    └── vendor
        └── erb
            ├── init.rb
            └── lib
                └── erb.rb

    12 directories, 17 files




跳到 examples/hello 目录下运行 `ruby test.rb` ，用浏览器打开 localhost:4567 便看到一个提交表单的页面。把文件里的路由都玩一遍，就能感觉到 sinatra 麻雀虽小，但五脏俱全。

test.rb 采用 `$LOAD_PATH.unshift '../../lib/'` 把 lib 目录放进加载路径中。

这种写法会导致如果在别的目录下，比如根目录，执行 `ruby examples/hello/test.rb` 报错，可以改为：

`$LOAD_PATH.unshift File.expand_path('../../lib',File.dirname(__FILE__))`

## rubygems 和 rack

根据 lib/sinatra/sinatra.rb 里加载文件的顺序，逐一看看这个版本的 sinatra 做了些什么。

sinatra.rb 第1到7行加载 两个 gem


    %w(rubygems rack).each do |library|
      begin
        require library
      rescue LoadError
        raise "== Sinatra cannot run without #{library} installed"
      end
    end


- rubygems 对 ruby 1.9+ 来说已经是多余的，见[链接](http://guides.rubygems.org/patterns/#requiring_rubygems)

- rack 是 sinatra 以及 rails 的基础，简介以及基本用法见[官网](http://rack.github.io/)，用一句话描述 rack ：为 web 服务器向 ruby 应用提供简洁的接口。再详细点描述怎样应用 rack ：
  - 运行 rack 时需要提供一个能响应 call 方法的对象
  - 这个对象的 call 方法必须返回一个包含三个元素的数组
  - 这个返回数组第一个元素是 http 状态码，第二个是 http 响应头，第三个是 http body 对象
  - body 对象要求能响应 each 方法

## 核心扩展 core_ext

接下来 sinatra 加载两个核心扩展 core_ext/class.rb 以及 core_ext/hash.rb

**class.rb**

ruby 内置了 `attr_reader/attr_writer/attr_accessor` 方法，可以方便地在类实例中生成 getter/setter 方法，core_ext/class.rb 重新打开了 Class 类，对应地在类中生成 getter/setter 方法。

`class_eval` 在这当中起到重要作用。

在 class.rb 中，因为没有显式调用 `class_eval` ，其 receiver 会指向 self ，而当前的 self 就是 Class 类的实例，即普通类，假设为 class 。 `class_eval` 把 self 指向 class ，也会重新打开 class ，当你需要动态地为类添加方法时很有用。如下例：


    #!/usr/bin/env ruby
    class TestClassEval
    end

    TestClassEval.class_eval do 
      def instance_method
        P 'instance method'
      end
      def self.class_method
        p 'class method'
      end
    end

    TestClassEval.class_method # 'class method'
    TestClassEval.new.instance_mehtod # 'instance method'
    TestClassEval.instance_mehtod # NoMethodError


顺便说说 `instance_eval` ，`instance_eval` 把 self 指向 实例 ，也会重新打开实例的 singleton class ，为其添加单例方法，继续用上面的 TestClassEval 作例，下面的写法在其上定义了另一个类方法。


    #!/usr/bin/env ruby
    TestClassEval.instance_eval do
      def another_class_method
        p 'another class method'
      end
    end

    TestClassEval.another_class_method # 'another class method'  

**hash.rb**

hash.rb 里使用了 inject 方法 symbolize  hash 的 key 

    def symbolize_keys
      self.inject({}) { |h, (k, v)| h[k.to_sym] = v;h}
    end


## 事件处理 event.rb


**EventManager**

EventManager 模块里有一个 extend self 方法调用，值得学习。

extend 方法是把 module 的实例方法加入到 class 的类单例方法中，其常规用法如下：

    module M
      def p_method
        p 'method'
      end
    end

    class C
      extend M
    end

    C.p_method # 'method'


如果不使用 extend ，也有其他途径的实现，如下：


    module M
      def p_method
        p 'method'
      end
    end

    class D
      class << self
        include M
      end
    end

    D.p_method # 'method'


在 EventManager 中，self 指向 module 自身， 因此 extend self 是用来高效地生成单例方法，可见[链接](http://ozmm.org/posts/singin_singletons.html) 

**EventContext**

为 block 提供执行上下文， block 借此可以访问 request/params ，可以设置和访问 status/headers/body

这里用到 alias, `alias :header :headers` ， ruby 中类似的用法还有 alias_method ，如果使用 alias_method ，要这样写 `alias_method :header, :headers` ，多一个逗号。

alias 与 alias_method 还有其他区别，前者是关键字，后者是定义在 Module 的方法，这意味着 alias_method 可以被重写；调用 alias 时，其 self 是在定义时就已经决定下来，而 alias_method 的 self 是在运行时才决定的，见下面的例子[(出自)](http://blog.bigbinary.com/2012/01/08/alias-vs-alias-method.html):

    # alias_method
    class User

      def full_name
        puts "Johnnie Walker"
      end

      def self.add_rename
        alias_method :name, :full_name
      end
    end

    class Developer < User
      def full_name
        puts "Geeky geek"
      end
      add_rename
    end

    Developer.new.name #=> 'Gekky geek'

    # alias
    class User

      def full_name
        puts "Johnnie Walker"
      end

      def self.add_rename
        alias :name :full_name
      end
    end

    class Developer < User
      def full_name
        puts "Geeky geek"
      end
      add_rename
    end

    Developer.new.name #=> 'Johnnie Walker'


基于上面的介绍，社区推荐使用 alias_method 。

**Event**

Event 在定义 initialize 方法时**最后一个参数**是 `&block` ，这表明在调用 Event.new 时如果接收到一个 block ，用 & 操作符把 block 转化为 proc 之后，在 initialize 方法内部可以调用 proc 的 call 方法。

如果没有在方法内部调用 call 方法的需求，或者没有把 block 当成变量传给别的方法的需求，就没必要在定义方法时写上 &block ，直接用 yield 关键字调用就行。

可以用 & 把 proc 转变为 block 。这个技巧用在 attend 方法里面，因为 instance_eval 只有[两种调用方式](http://ruby-doc.org/core-1.9.3/BasicObject.html#method-i-instance_eval)：要么接收一个字符串，要么接收一个 block ，所以要把 proc 转变为 block 当作参数传进去。

如果跟在 & 操作符后面的对象不是 proc ，& 会调用跟在它后面的对象的 :to_proc 方法。 symbol 对象也有自己的 :to_proc 方法，你经常能看到类似下面的代码：

    def tag_names
      @tag_names || tags.map(&:name).join(' ')
    end

事实上这跟下面的代码是等效的：

    def tag_names
      @tag_names || tags.map({ |tag| tag.name }).join(' ')
    end

symbol 对象的 :to_proc 方法最早是 Rails 引进的，后面合并到 ruby 1.8.7 版本：

    class Symbol
      def to_proc
        Proc.new do |obj, *args|
          obj.send self, *args
        end
      end
    end

上面整个例子都出自 [stackoverflow](http://stackoverflow.com/questions/1217088/what-does-mapname-mean-in-ruby)

关于 & ，更多资料可以看看[这篇文章](http://weblog.raganwald.com/2008/06/what-does-do-when-used-as-unary.html)

## 路由请求，封装响应 dispatcher.rb

dispatcher 负责将请求转发到对应的 event ，经 event 处理后，返回符合 rack 要求的响应。

rack 会直接调用 dispatcher 的 call 方法，传入 env ，利用 rack [提供的方法](http://www.rubydoc.info/gems/rack/Rack/Request)可以得到 request 对象。

用 array 的 detect 方法实现转发功能， detect 接受一个 [ifnone 参数](http://ruby-doc.org/core-2.3.1/Enumerable.html#method-i-detect)，如果找不到合适的 event ，就调用 ifnone 的 call 方法，将 call 方法的返回值作为 detect 的返回值，借此实现大家都熟悉的 404 。

这里的 ifnone 是一个 lambda

    lambda { not_found }

调用 lambda 的 call 会执行 not_found 方法，而 not_found 返回一个 Event 实例。

## server.rb

[rack 2.0](https://github.com/rack/rack/tree/2.0.0.alpha) 开始不支持 Mongrel 的 handler 。

`trap("INT") do ... end` 这段代码会捕获用户输入的 `ctrl + c` ，从而调用 Mongrel::HttpServer 的 [stop](https://github.com/mongrel/mongrel/blob/master/lib/mongrel.rb#L344) 方法。

## dsl.rb

重新打开 Kernel ，增加 4 个 http 方法。

所有 ruby 类（除了 BasicObject）都继承模块 Kernel ，这意味着一旦 require 这个文件，就连字符串都带这4个方法。

可以打开 irb 验证一下，查看类的祖先链的方法是 ancestors ，如 `String.ancestors`

## erb

**init.rb** 里有这样一行：

    Sinatra::EventContext.send(:include, Sinatra::Erb::InstanceMethods)

ruby 里的方法调用其实就是向被调用方发送（send）一个方法，所以被调用方又叫 receiver 。 EventContext include 了 Erb::InstanceMethods ，就是把 Erb::InstanceMethods 插入到 EventContext 继承链的父亲节点，这样 EventContext 的实例就都可以调用 Erb::InstanceMethods 里面的方法。你也可以直接打开 EventContext 达到同样的目的：

    class Sinatra::EventContext
      include Sinatra::Erb::InstanceMethods
    end


**erb.rb**

erb.rb 实现找到正确的模板，然后把渲染后的值赋给 EventContext 的实例变量 @body。

在找模板时使用到一个全局变量 `$0` ，官方文档的[描述](http://ruby-doc.org/core-2.0.0/doc/globals_rdoc.html)： 

> Contains the name of the script being executed. May be assignable.

可以用它来实现类似 Python 判断当前文件是否被直接运行的功能（用来写测试用例）：

    if __FILE__ == $0
      # code goes here
    end

sinatra 用它来实现寻找模板的默认路径。

ERB 的 result 方法接收一个 binding 参数，默认值是 TOPLEVEL_BINDING 。 binding 是 Kernel 的方法，它会返回 当前作用域(local scope)。因为 binding 是在 EventContext 的某个实例里面运行，它返回的是那个实例的作用域，所以可以访问实例变量及实例方法，如 params 。举例如下：


    class MyClass
      def initialize(x)
        @x = x
      end
      def get_binding
        binding
      end
      def print
        p 'print out something'
      end
    end

    my_instance = MyClass.new(1)
    my_binding = my_instance.get_binding

    eval '@x', b # 1
    eval 'print', b # 'print out something'

## 最后， at_exit


at_exit 也是 Kernel 里的方法，它接受一个 block ，并将其转换成 Proc ，当程序退出时会调用 Proc 。如果调用了多次 at_exit 。那么这些 Proc 按倒序执行，如：

    at_exit do
      puts '再见！'
    end

    at_exit do
      puts '已经写完，'
    end

    at_exit do
      print 'sinatra 0.0.1 版本源码学习'
    end

