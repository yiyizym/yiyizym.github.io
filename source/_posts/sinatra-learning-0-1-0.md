title: sinatra 0.1.0 源码学习
date: 2016-07-10 14:40:17
description: 通过 sinatra 学习 ruby 编程技巧（系列）
categories: ruby
tags: 
- sinatra
- ruby

---

## 声明

本文系 **sinatra 源码系列**第 2 篇，第 1 篇[见此](/2016/06/12/sinatra-learning-0-0-1/)。系列的目的是通过 sinatra 学习 ruby 编程技巧。文章按程序运行的先后顺序挑重点分析，前一篇文章分析过的略去不说。水平很有限，所写尽量给出可靠官方/讨论链接，不坑路人。

## 重要提醒

**一定要先安装 1.8 版本的 ruby** ，因为 1.9+ 的 ruby ，String 的实例是不响应 each 方法的，这会直接导致 rack 报错。可以使用 [rvm](https://rvm.io/) 安装 1.8.7 版本的 ruby ，如果使用 rvm ，请先升级到最新版本，否则安装 1.8.7 的 ruby 时也会报错。

列一下本人运行 sinatra 0.0.1 用到的 ruby 和关键 gem 的版本：

- ruby-1.8.7-p374
- rack 1.4.1
- mongrel 1.1.5

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

