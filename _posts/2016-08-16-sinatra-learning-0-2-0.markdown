---
layout: post
title: sinatra 0.2.0 源码学习
date: 2016-08-16 21:21:48
excerpt: 通过 sinatra 学习 ruby 编程技巧（系列）
lang: zh_CN
categories: ruby
tags: 
- sinatra
- ruby

---

## 声明

本文系 **sinatra 源码系列**第 4 篇。系列的目的是通过 sinatra 学习 ruby 编程技巧。文章按程序运行的先后顺序挑重点分析，前一篇文章分析过的略去不说。水平很有限，所写尽量给出可靠官方/讨论链接，不坑路人。

## 重要提醒

**一定要先安装 1.8 版本的 ruby** ，因为 1.9+ 的 ruby ，String 的实例是不响应 each 方法的，这会直接导致 rack 报错。可以使用 [rvm](https://rvm.io/) 安装 1.8.7 版本的 ruby ，如果使用 rvm ，请先升级到最新版本，否则安装 1.8.7 的 ruby 时也会报错。

使用命令 `git log -1 --format=%ai 0.2.0` ，查看 0.2.0 版本 sinatra 的“出厂日期”，得到 `2008-04-11 16:29:36 -0700` ；而 1.8.7 版本的 ruby 是 2008 年 5 月发布的，两者兼容性应该比较好。

列一下本人运行 sinatra 0.2.0 用到的 ruby 和关键 gem 的版本：

- ruby-1.8.7-p374
- rack 1.4.1
- mongrel 1.1.5

## change log

- 大重构，把功能模块都压缩在一个文件中
- 增加大量测试用例


## 跑通所有测试用例

首先修改一处代码错误，在 sinatra.rb 文件的 1022 行，将 `Rack::File::MIME_TYPES[ext.to_s] = type` 改为 `Rack::Mime::MIME_TYPES[ext.to_s] = type`

然后安装一些缺少的 gem ：

    gem install builder -v '2.1.2'
    gem install sass -v '3.1.0'
    gem install haml -v '1.8.0'

跑测试用例，发现只有 `sym_params_test.rb` 文件中的一处跑不通过。

此处的测试是验证可以用 String 和 Symbol 访问参数。实现的关键方法是：

    # sinatra.rb 663 行
    h = Hash.new { |h, k| h[k.to_s] if Symbol === k }

调用 `Hash.new` 时传进一个 block ，可以设置当访问某个不存在于 Hash 的 Key 时的一些默认行为，比如上面的代码就是说，当 key 不存在且是 Symbol 时，把 key 转换为字符串再找找（再抢救一下...）

`Hash.new` 还可以用来初始化值为数组的键值对，在记录事件回调时很方便：

    @events = Hash.new { |hash, key| hash[key] = [] }
    
    # 出自这个版本的 sinatra.rb 的 738 行
    # 再也不用先判断 key 是否存在，也不用手动初始化一个空数组了

回过头来修改代码以跑通测试用例，作者这里粗心写错了请求的方法，应该用 `post_it` ，而不是 `get_it` ，还要相应地修改路由：

    specify "should be accessable as Strings or Symbols" do
      post '/' do
        params[:foo] + params['foo']
      end
      
      post_it '/', :foo => "X"
      assert_equal('XX', body)
    end

要在这个版本的 sinatra 的 get 方法中传递参数，需要把参数写在 uri 中，下面的写法也能通过测试：

    specify "should be accessable as Strings or Symbols" do
      get '/' do
        params[:foo] + params['foo']
      end
      
      get_it '/?foo=X'
      assert_equal('XX', body)
    end

## 从 at_exit 说起

还是从 at_exit 开始读代码。

`$!` 记录异常信息，当调用 `raise` 的时候会设置这个变量，详见[此处](http://ruby-doc.org/docs/ruby-doc-bundle/Manual/man-1.4/variable.html#dquote)。

调用 `load_options!` 解释完启动参数后， sinatra 在所有环境设置遇到异常和 404 时的回调方法，在开发环境遇到异常和 404 的回调方法比其他环境暴露更多的信息。

### OpenStruct

值得细看的是在非开发环境遇到异常时的回调方法：

    error do
      raise request.env['sinatra.error'] if Sinatra.options.raise_errors
      '<h1>Internal Server Error</h1>'
    end

`Sinatra.options` 实际上是 `OpenStruct` 的实例。 [`OpenStruct`](http://ruby-doc.org/stdlib-1.9.3/libdoc/ostruct/rdoc/OpenStruct.html) 与 `Hash` 相似，但它通过元编程提供了不少快捷访问、设置值的方法。 `OpenStruct` 用法举例：

    # 1
    person = OpenStruct.new
    person.name    = "John Smith"
    p person.name    #=> "John Smith"

    # 2
    person = OpenStruct.new(:name => "John Smith")
    p person.name    #=> "John Smith"

一个简单版本的 `OpenStruct` 实现：

    class OpenStruct
      attr_accessor :h
      def initialize(hash = {})
        @h = hash

        h.each do |key, value|
          self.class.send(:define_method, key) do
            h[key]
          end
          self.class.send(:define_method, "#{key}=") do |value|
            h[key] = value
          end
        end
      end
      
      def method_missing(m, *args)
        if args.size == 1
          # m is  :name=
          # change m to :name
          h[m.to_s.chop.to_sym] = args[0]
        elsif args.size == 0
          h[m]
        end
      end

      def respond_to?(m)
        h.respond_to?(m) || super
      end

    end

    require 'test/unit'

    class TestOS < Test::Unit::TestCase
      def setup
        @person_1 = OpenStruct.new
        @person_2 = OpenStruct.new(:name => 'zhu')
      end

      def test_case_1
        assert_equal true, @person_1.respond_to?(:name)
        assert_equal nil, @person_1.name
        @person_1.name = 'zhu'
        assert_equal 'zhu', @person_1.name
      end

      def test_case_2
        assert_equal true, @person_2.respond_to?(:name)
        assert_equal 'zhu', @person_2.name
        @person_2.name = 'jude'
        assert_equal 'jude', @person_2.name
      end
    end

以上只是我心血来潮写的， `OpenStruct` 的实现远远不是上面写的那么简单，有兴趣可以看看源码。

`Sinatra.options.raise_errors` 的值只能在代码里设置，当其值不为 nil 或 false 时，默认在非开发环境下直接抛出异常。要想在命令行启动时设置值，只需要在 `load_options!` 方法中添加一行：

    op.on('-r') { |env| default_options[:raise_errors] = true }

在订制开发环境下的异常和 404 页面时，使用到 `%Q(...)` 。 ruby 会特殊处理以百分号 '%' 开头的字符串，帮你省去不少转义引号的麻烦：

> The string expressions begin with % are the special form to avoid putting too many backslashes into quoted strings. [出处](http://ruby-doc.org/docs/ruby-doc-bundle/Manual/man-1.4/syntax.html)

更多相似的用法见[Ruby 里的 %Q, %q, %W, %w, %x, %r, %s, %i](https://ruby-china.org/topics/18512)。

在显示异常信息时，用 `escap_html` 来转义 `&`,`<`,`>`,`/`,`'`,`"` ，把这些 ascii 字符编码成实体编码，防止 XSS 攻击，不过源码有注释说有 bug ：

>  On 1.8, there is a kcode = 'u' bug that allows for XSS otherwhise

源码中用正则表达式替换转义字符的[实现](https://github.com/rack/rack/blob/1.4.1/lib/rack/utils.rb#L181)值得参考。

更多关于 XSS 的知识，可以看看本人之前写的[这篇](http://judes.me/2015/10/02/xss-study/)。


### lookup

接下来看 Application 的 call 方法。

首先由 `lookup` 方法实现根据请求找到正确的路由。

    def lookup(request)
      method = request.request_method.downcase.to_sym
      events[method].eject(&[:invoke, request]) ||
        (events[:get].eject(&[:invoke, request]) if method == :head) ||
        errors[NotFound].invoke(request)
    end

sinatra 在 `Enumerable` 上扩展了 `eject` 方法，因为 `Array` 加载了 `Enumberable` 模块，所以 `Array` 实例能用 `eject` 方法。

    def eject(&block)
      find { |e| result = block[e] and break result }
    end

在 `eject` 方法内部，使用 `find` 方法找到第一个产生非 false 结果的 block ，并返回这个结果。`find` 方法本来会返回第一个符合条件的元素，通过 `break` 可以订制自己的返回值。


这里 `e` 是 Event 的实例。 `block` 是由 Array 实例转化而来的 Proc 。

系列[第一篇文章](http://judes.me/2016/06/12/sinatra-learning-0-0-1/)提到过， 如果跟在 `&` 后面对象的不是 Proc ，首先会调用这个对象的 `to_proc` 方法得到一个 Proc 实例，最后会调用这个 Proc 的 `call` 方法。

sinatra 扩展了 Array 的 `to_proc` 方法：

    def to_proc
      Proc.new { |*args| args.shift.__send__(self[0], *(args + self[1..-1])) }
    end

经过 `to_proc` 转换， `Proc#call` 把参数转换为一个数组，把这个数组第一个元素作为 `receiver` ，把调用 `to_proc` 方法的数组的第一个元素作为方法，把两个数组余下的元素作为方法的参数，拿前面的代码作例子：

    # 在 lookup 方法里下面的这行代码

    &[:invoke, request]

    # 会得到这样一个 Proc

    #=> Proc.new { |*args| args.shift.__send__(:invoke, *(args + [request])) }
    
    # 在 eject 方法定义中

    find { |e| result = block[e] and break result }

    # block[e] 就是把 e 当作参数调用  Proc#call ，做的事情是： 以 `request` 作为参数，调用 `e` 的 `invoke` 方法。


`block[e]` 不能写成 `block(e)` ，否则 ruby 会把 `block` 当作是 main 的一个方法来调用。有三种方法可以调用 [`Proc#call`](https://ruby-doc.org/core-2.2.0/Proc.html#method-i-5B-5D) ：

    # 1
     a_proc.call()
    # 2
     a_proc.()
    # 3
     a_proc[]

### invoke

`Event#invoke` 方法实现路由匹配和参数匹配。除了可以匹配路径，这个版本的 sinatra 还可以匹配 user_agent 和 host :

    if agent = options[:agent] 
      return unless request.user_agent =~ agent
      params[:agent] = $~[1..-1]
    end
    if host = options[:host] 
      return unless host === request.host
    end

用法和测试举例如下：

    require 'sinatra'

    get '/path', :agent => /Windows/
      request.env['HTTP_USER_AGENT']
    end
    # get_it '/', :env => { :agent => 'Windows' }
    # should.be.ok
    # body.should.equal 'Windows'

    # get_it '/', :agent => 'Mac'
    # should.not.be.ok



    get '/path', {}, HTTP_HOST => 'foo.test.com'
      'in foo'
    end

    get '/path', {}, HTTP_HOST => 'bar.test.com'
      'in bar'
    end

    # get_it '/foo', {}, 'HTTP_HOST' => 'foo.test.com'
    # assert ok?
    # assert_equal 'in foo', body

    # get_it '/foo', {}, 'HTTP_HOST' => 'bar.test.com'
    # assert ok?
    # assert_equal 'in bar', body
    
    # get_it '/foo'
    # assert not_found?

`request.user_agent` 最终调用 `env['HTTP_USER_AGENT']` ，在 /lib/sinatra/test/methods.rb 中， sinatra 重写了 `Rack::MockRequest#env_for` 方法：

    class Rack::MockRequest
      class << self
        alias :env_for_without_env :env_for
        def env_for(uri = "", opts = {})
          env = { 'HTTP_USER_AGENT' => opts.delete(:agent) }
          env_for_without_env(uri, opts).merge(env)
        end
      end
    end

这样在测试时就可以传递 `:agent => 'Windows'` 作为 user_agent 的参数，否则要这样写： `'HTTP_USER_AGENT' => 'Windows'` 。

#### call the overridden method from the new

在 ruby 中重写一个方法，新方法中还要调用未被重写前的旧方法，有几个技巧。

一，继承。需要修改每一处用到新方法的 reciever 。

    class Foo
      def say
        'Hello'
      end
    end

    class Bar < Foo
      def say
        super + ' World!'
      end
    end

    Foo.new.say #=> 'Hello'
    Bar.new.say #=> 'Hello World!'
    # 把 reciever 从 Foo 改为 Bar

二，修改祖先链。这与继承类似，但修改的方向不一样。

    moudle Bar
      def say
        super + ' World!'
      end
    end

    class Foo
      prepend Bar
      def say
        'Hello'
      end
    end

    Foo.new.say #=> 'Hello World!'

    # 使用了 prepend 把 Bar 放在 Foo 祖先链的下游，当寻找 say 方法时，首先找到 Bar 定义的 say 方法

三，使用 [UnboundMethod](http://ruby-doc.org/core-1.9.3/UnboundMethod.html#method-i-bind)  和 `define_method` 。

    class Foo
      def say
        'Hello'
      end
    end

    # 在某处重新打开 Foo

    class Foo
      old_say = instance_method(:say)
      define_method(:say) do
        old_say.bind(self)[] + ' World!'
        # 调用 instance_method 得到一个 UnboundMethod ，你需要在调用它之前 bind 一个 Foo 的实例
        # 前面说过调用 Proc#call 的三种方法，调用 Method#call 也是一样。这里采用了 [] ，你也可以用 .()
      end
    end

四， alias 。就是 sinatra 采用的方法。

    class Foo
      def say
        'Hello'
      end
    end

    # 在某处重新打开 Foo

    class Foo
      alias :old_say :say
      def say
        old_say + ' World!'
      end
    end

    Foo.new.say #=> 'Hello World!'
    Foo.new.old_say #=> 'Hello'
    # 使用这种技巧，仍然可以访问旧的方法


更多的技巧，可参考[这里](http://stackoverflow.com/questions/4470108/when-monkey-patching-a-method-can-you-call-the-overridden-method-from-the-new-i)。



继续看 `Event#invoke` 的实现，下面代码这行实现匹配路径：

    return unless pattern =~ request.path_info.squeeze('/')

`String#squeeze` 方法用单个字符替换连续出现的字符，用法很灵活，参见[文档](https://ruby-doc.org/core-2.2.0/String.html#method-i-squeeze)。

sinatra 实现路径匹配的参数匹配的思路是：

- 将用户预先定义的路径转换为正则表达式
- 用这些正则表达式去匹配实际请求的路径
- 如果匹配成功，则把捕获的参数与定义的参数组成键值对保存起来

`Event#initialize` 实现了路径转换正则表达式：

    URI_CHAR = '[^/?:,&#\.]'.freeze unless defined?(URI_CHAR)
    PARAM = /:(#{URI_CHAR}+)/.freeze unless defined?(PARAM)
    SPLAT = /(.*?)/
    attr_reader :pattern

    def initialize(path, options = {}, &b)
      @path = URI.encode(path)
      @param_keys = []
      regex = @path.to_s.gsub(PARAM) do
        @param_keys << $1
        "(#{URI_CHAR}+)"
      end
      
      regex.gsub!('*', SPLAT.to_s)
      
      @pattern = /^#{regex}$/
    end


首先把用户定义的路径编码成 URI ，因为 [rfc1738](http://www.ietf.org/rfc/rfc1738.txt) 文档规定在 URL 中出现的字符只能是 字母和数字[0-9a-zA-Z]、一些特殊符号"$-_.+!*'() 以及一些保留字符：

> only alphanumerics, the special characters "$-_.+!*'(),", and reserved characters sed for their reserved purposes may be used unencoded within a URL.

如果在路径或查询参数中出现其他字符，比如中文，需要先转义。

然后把用户在定义路径中的参数找出来，替换为去掉冒号（:）后的正则表达式字符串。

`PARAM` 正则表达式———— `/:([^/?:,&#\.]+)/`———— 匹配以冒号开头的，接下来的字符不是 `/ ? : , & # .` 当中任意一个字符的字符串。

`$1` 保存了最近一次正则表达式捕获的第一个匹配结果。

用户还可以定义不具名参数： '*' ，这个功能还不完善，现阶段只能作占位符用，没法获取捕获的参数。

接下来的事情就是把捕获的参数与定义的参数组成键值对保存在 `params` 中，之前的系列文章有说过。

保存好参数后，调用 `Result.new(block, params, 200)` 生成 `Result` ，它是 `Struct` 的实例。跟 `OpenStruct` 不同， `Struct` 只能读、写在初始化时设定的 key ，不能新增 key ：

    Bar = Struct.new(a,b)
    bar = Bar.new(1,2)
    bar.a #=> 1
    bar.c #=> undefined method `c' for #<struct Bar a=1, b=2>


sinatra 能正确响应 HEAD 请求方法。根据 [rfc 文档](http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html)， HEAD 方法跟 GET 方法唯一的区别就是，响应 HEAD 方法时，响应报文不能带有 body 。响应报文的头应该跟 GET 方法的一致。 HEAD 方法主要用于验证资源的有效性、可用性以及最近是否修改过。

如上所述，如果是 HEAD 请求， sinatra 会自动去找对应的 GET 方法回调：

    (events[:get].eject(&[:invoke, request]) if method == :head)

在生成 HEAD 请求的响应时，会设置 body 为空字符：

    # line 839
    body = '' if request.request_method.upcase == 'HEAD'

### to_result

在获取响应的 body 时，不论是正常流程，还是异常流程，都调用了 `to_result` 方法。 sinatra 在很多类中都扩展了这个实例方法。

正常流程的代码如下：

    returned = run_safely do
      catch(:halt) do
        filters[:before].each { |f| context.instance_eval(&f) }
        [:complete, context.instance_eval(&result.block)]
      end
    end
    body = returned.to_result(context)
    # 一切正常时， returned 是 [:complete, context.instance_eval(&result.block)]

与此相关的两个 `to_result` 方法是：

    class Array
      def to_result(cx, *args)
        self.shift.to_result(cx, *self)
      end
    end

    class Symbol
      def to_result(cx, *args)
        cx.send(self, *args)
      end
    end

`returned.to_result(context)` 最终是在 `context` 上调用 `complete` 方法，传入的参数是 `context.instance_eval(&result.block)` 的返回值。

异常流程，如在 before filters 中抛出 `:halt` ，在 README.doc 文档中详细说明了多种情况：

> Set the body to the result of a helper method

> throw :halt, :helper_method
    
> Set the body to the result of a helper method after sending it parameters from the local scope
    
> throw :halt, [:helper_method, foo, bar]
      
> Set the body to a simple string

> throw :halt, 'this will be the body'
    
> Set status then the body

> throw :halt, [401, 'go away!']
    
> Set the status then call a helper method with params from local scope

> throw :halt, [401, [:helper_method, foo, bar]]

> Run a proc inside the Sinatra::EventContext instance and set the body to the result

> throw :halt, lambda { puts 'In a proc!'; 'I just wrote to $stdout!' }

在众多应对以上情况的 `to_proc` 中，值得一提的是以下这两个：

    class String
      def to_result(cx, *args)
        args.shift.to_result(cx, *args)
        self
      end
    end

    class NilClass
      def to_result(cx, *args)
        ''
      end
    end

`throw :halt, 'this will be the body'` 之后，最终会用到 `String#to_result` 方法，传入的参数只有一个 `context` ，因此 `args` 是个空数组， `args.shift` 得到 `nil` ，所以得扩展 `NilClass#to_result` ，但它什么也没做，径直返回空字符串。


### context.body

在处理返回报文的正文时，有如下代码：

    context.body = body.kind_of?(String) ? [*body] : body

`kind_of?` 方法跟 `is_a?` 一样，回溯祖先链，找到祖先返回 true ，否则返回 false 。

`[*body]` 中的 `*` （splat operator）有很多用途，之前也说过它可以把函数的多个参数变为一个数组。此处是另外两种用法。

其一是强制类型转换，把当前类型转换为 Array 类型：

    # Range 转换为 Array
    a = *(1..3) #=> [1,2,3]

    # String 转换为 Array
    b = *"one string" #=> ["one string"]

    # Array 仍然是 Array
    c = *[1,2,3] #=> [1,2,3]

    # nil 转换为 Array
    d = *nil #=> []

其二是展平数组：

    e = [*[1,2],*[3,4]] #=> [1,2,3,4]

    # 这跟下面是一样的

    f = [[1,2],[3,4]].flatten

回头看 `[*body]` ，如果只是把字符串强制转换为数组的话， `*body` 就够了。但是这里必须用中括号（`[]`）包着，否则会报语法错误。用中括号包住，解决了语法问题，得到的还是原来的那个数组。


`*` 实际上并不是 operator ，而是 token ，而且很容易就会用错。大致有以下几种用法：

    # 用于赋值
    
    first, *rest = [1,2,3]
    #=> first = 1
    #=> rest = [2,3]

    *rest, last = [1,2,3]
    #=> last = 3
    #=> rest = [1,2]

    first, *m, last = [1,2,3,4]

    # 收集参数，分解参数

    def foo(first, *args); end #=> *args 只能放在最后
    foo(1,2,3,4) #=> args = [2,3,4]

    def bar(a, b); end
    bar(*[1,2]) #=> a = 1, b = 2

    # 强制类型转换，很容易出语法错误，所以最好用中括号包住

`context#body` 由在 Class 类中的 `dslify_writer` 方法实现：写入 body 的值，并返回这个值。

    class Class
      def dslify_writer(*syms)
        syms.each do |sym|
          class_eval <<-end_eval
            def #{sym}(v=nil)
              self.send "#{sym}=", v if v
              v
            end
          end_eval
        end
      end
    end

    class Foo
      dslify_writer :bar
      # 相当于这样写：
      # def bar(v=nil)
      #   self.send('bar=', v) if v
      #   v
      # end
    end

`context` 并没有实现 `body=` 方法，但它有实现 `method_missing` 方法，把找不到的 method 转发给 `@response` ，而 `@response` 是 `Rack::Response` 的实例，可以读写 `body` 。

本小节参考文章：

- [Using splats to build up and tear apart arrays in Ruby](http://blog.honeybadger.io/ruby-splat-array-manipulation-destructuring/)
- [Splat Operator in Ruby](http://jacopretorius.net/2012/01/splat-operator-in-ruby.html)
- [The Strange Ruby Splat](https://endofline.wordpress.com/2011/01/21/the-strange-ruby-splat/)
- [Where is it legal to use ruby splat operator?](http://stackoverflow.com/questions/776462/where-is-it-legal-to-use-ruby-splat-operator)

### context.finish

`context.finish` 也是转发到 `response.finish` ：

    def finish(&block)
      @block = block

      if [204, 205, 304].include?(status.to_i)
        header.delete "Content-Type"
        header.delete "Content-Length"
        [status.to_i, header, []]
      else
        [status.to_i, header, self]
      end
    end

包含以下[状态码](https://zh.wikipedia.org/wiki/HTTP状态码)的响应会被删除响应头的 Content-Type / Content-Length 字段：

- 204 No Content ，服务器成功处理了请求，但不需要返回任何实体内容，浏览器不产生任何文档视图上的变化
- 205 Reset Content ，服务器成功处理了请求，但不需要返回任何实体内容，浏览器要重置文档视图，比如重置表单
- 304 Use Proxy ，被请求的资源必须通过指定的代理——在 location 字段中指定——才能被访问

并且返回数组中的第三个元素是个空数组，表明响应正文为空。

其他状态码返回数组中的第三个元素是 `self` ，能这样做的前提是 response 实现了 `each` 方法。


### 设置 body

application_test.rb 里有一个测试用例如下：

    class TesterWithEach
      def each
        yield 'foo'
        yield 'bar'
        yield 'baz'
      end
    end

    specify "an objects result from each if it has it" do
    
      get '/' do
        TesterWithEach.new
      end
      
      get_it '/'
      should.be.ok
      body.should.equal 'foobarbaz'

    end

如果没有在 get block 中设置 body 值， sinatra 就会用 block 的返回值作为 body ，如果这个返回值不响应 `each` 方法， body 就会被设置为空字符。可以模仿这里的 `TesterWithEach#each` 实现一个简单的 `each` ：

    class Foo
      attr_reader :bar
      
      def initialize(*bar)
        @bar = bar
      end
      
      def each
        return nil unless block_given?
        i = 0
        while i < bar.length
          yield bar[i]
          i += 1
        end
      end
    end

    # foo = Foo.new(1,2,3,4)
    # foo.each { |i| p i  }

目前为止， sinatra 的基本功能都已经实现，剩下的扩展功能——如重定向、渲染xml/erb/sass/haml、传输文件等等——都是通过加载模块来实现。

## Streaming

这一模块取自 ActionPack ，目的是用更少的内存消耗传输更大的文件，大体的做法是用流传输取代一次性输出整个文件。

实现 Streaming 的关键代码如下：

    class FileStreamer
      
      #...

      def to_result(cx, *args)
        self
      end
      
      def each
        File.open(path, 'rb') do |file|
          while buf = file.read(options[:buffer_size])
            yield buf
          end
        end
      end
      #...

    end

    #...

    def send_file(path, options = {})

      #...

      if options[:stream]
        throw :halt, [options[:status] || 200, FileStreamer.new(path, options)]
      else
        File.open(path, 'rb') { |file| throw :halt, [options[:status] || 200, file.read] }
      end

    end

如果 `options[:stream]` 为 true 则通过自身的 `each` 方法每读入 4096 个字节就对外输出，否则一次性读入内存再输出。

### protected

Streaming 模块中有两个 protected 方法。 ruby 的 protected 跟 java 的很像，一般情况下被设置为 protected 的实例方法只能从类（或子类）实例方法中访问。（借助 `send` 方法可以突破这层限制）

    class Person

      def initialize(age)
        @age = age
      end

      def older_than?(other_person)
        if self.class == other_person.class
          age > other_person.age
        end
      end
      
      protected

      attr_reader :age

    end

    class Monkey

      def initialize(age)
        @age = age
      end

      def older_than?(person)
        age > person.age
      end
      
      protected

      attr_reader :age
    end

    p1 = Person.new(10)
    p2 = Person.new(11)
    p1.older_than?(p2) #=> false

    # p1.age #=> protected method `age' called for #<Person:0x007f80cc0263c8 @age=10> (NoMethodError)

    m1 = Monkey.new(13)

    # m1.older_than?(p1) #=> protected method `age' called for #<Person:0x007fd3e4963880 @age=10> (NoMethodError)

ruby 的 protected 方法很少用到，如果要用的话，通常用于同类之间的比较（参见上面的 Person 类）。

本小节参考文章：

- [When to Use Protected Methods in Ruby](http://nithinbekal.com/posts/ruby-protected-methods/)
- [Protected Methods and Ruby 2.0](https://tenderlovemaking.com/2012/09/07/protected-methods-and-ruby-2-0.html)
- [Private and Protected: They might not mean what you think they mean](http://devblog.orgsync.com/2013/05/20/private-and-protected-they-might-not-mean-what-you-think-they-mean/)

## RenderingHelpers

sinatra 渲染的过程大致可以分为两个步骤：

- 根据传进来的参数 (String/Symbol/Proc) ，找到对应的模板
- 调用具体的渲染引擎渲染模板

第一个步骤是共用的，抽出来形成 RenderingHelpers 。

RenderingHelpers 的实现体现了两个软件设计原则： 1. 依赖反转； 2. 开闭原则（对扩展开放，对修改闭合）。

举例说明一下本人所理解的依赖反转：把高层次的模块比作电器，把低层次的模块比作插座。要使两者配合起来为人所用，高层次的模块必须实现低层次模块指定的接口，这个接口就是特定的插头（或两脚或三脚）。

RenderingHelpers 对外提供 `render` 方法，但要使用 `render` 方法，必须实现 `render_renderer` 方法，这个 `render_renderer` 就是特定的插头。

这个版本的 sinatra 增加了多个渲染引擎的支持，这些引擎的实现细节各有不同（如 sass 不支持 layout），但增加这些引擎支持都不用修改 RenderingHelpers 里面的代码。你甚至可以加入自己的引擎，无需改动 RenderingHelpers ，只要它提供的 `render` 方法，并实现自己的 `render_renderer` 方法。这体现了开闭原则。


### use_in_file_templates!

渲染时需要的模板，除了可以放在别的文件中，还可以放在当前文件中：

    get '/stylesheet.css' do
      header 'Content-Type' => 'text/css; charset=utf-8'
      sass :stylesheet
    end

    # 这里需要的模板可以放在 "views/stylesheet.sass" 文件中，假设包含以下内容

      #  body
      #    #admin
      #      :background-color #CCC

    # 也可以放在当前文件中，需要事先调用 use_in_file_templates! ，如下：

    use_in_file_templates！

    __END__
    ## stylesheet
    body
      #admin
        :background-color #CCC

`use_in_file_templates！`实现的细节是首先找到调用 `use_in_file_templates！` 方法的文件。 `caller` 方法会以数组形式返回当前方法的调用栈，形式如下：

    def a(skip)
      caller(skip)
    end
    def b(skip)
      a(skip)
    end
    def c(skip)
      b(skip)
    end
    c(0)   #=> ["prog:2:in `a'", "prog:5:in `b'", "prog:8:in `c'", "prog:10"]
    c(1)   #=> ["prog:5:in `b'", "prog:8:in `c'", "prog:11"]
    c(2)   #=> ["prog:8:in `c'", "prog:12"]
    c(3)   #=> ["prog:13"]

然后把这个文件转换为字符串，定位到字符串的一个特殊标记。这里作者写错了这个特殊标记，应该是 `__END__` ，而不是 `__FILE__` 。虽然写成 `__FILE__` 也能跑过测试用例，但这个标记与 `__END__` 是完全不同的。

ruby 有一个特殊的常量 [`DATA`](https://ruby-doc.org/core-2.3.1/Object.html) ，它是一个 `File` 对象，包含了文件中的数据。你可以把数据和代码放在同一个文件当中， ruby 通过 `__END__` 这个标记分开代码和数据：

    # t.rb
    puts DATA.gets
    __END__
    hello world!

    # ruby t.rb 
    # => hello world!

定位到数据部分后，把这部分字符串转换为 [StringIO](http://stackoverflow.com/questions/12592234/what-are-the-advantages-to-using-stringio-in-ruby-as-opposed-to-string) 对象，以便把字符串当作文件逐行解释。

只要匹配到以 `##` 开头的行，就把捕获的字符串当作新的模板名字，没匹配行的就当作是模板的内容。

全文完。