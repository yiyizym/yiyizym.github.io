title: sinatra 0.1.5 源码学习
date: 2016-08-13 09:57:34
description: 通过 sinatra 学习 ruby 编程技巧（系列）
categories: ruby
tags: 
- sinatra
- ruby

---

## 声明

本文系 **sinatra 源码系列**第 3 篇。系列的目的是通过 sinatra 学习 ruby 编程技巧。文章按程序运行的先后顺序挑重点分析，前一篇文章分析过的略去不说。水平很有限，所写尽量给出可靠官方/讨论链接，不坑路人。

## 重要提醒

**一定要先安装 1.8 版本的 ruby** ，因为 1.9+ 的 ruby ，String 的实例是不响应 each 方法的，这会直接导致 rack 报错。可以使用 [rvm](https://rvm.io/) 安装 1.8.7 版本的 ruby ，如果使用 rvm ，请先升级到最新版本，否则安装 1.8.7 的 ruby 时也会报错。

列一下本人运行 sinatra 0.1.5 用到的 ruby 和关键 gem 的版本：

- ruby-1.8.7-p374
- rack 1.4.1
- mongrel 1.1.5

## change log

- 增加 Mutex
- 支持处理请求前的事件回调


这一版改动主要集中在 event.erb 文件里。

## event.erb

### Mutex 互斥锁

当多个线程读写公共资源时，要使用互斥锁保证每个线程在读或写时都是原子操作。

使用互斥锁首先要区分哪些是公共资源，哪些代码会访问这些公共资源，然后用互斥锁隔离这些代码。

sinatra 自身的代码不会既读又写公共资源（要么只读公共资源，要么每个线程使用自己的变量），因此可以在多线程中运行以同时处理多个请求，但是处理请求时执行的用户自定义的代码，有可能访问公共资源，这部分代码（处理请求的代码、处理请求之前和之后的事件回调）可能需要使用互斥锁。 sinatra 默认不使用互斥锁。

sinatra 是否运行在多线程环境中取决于 Rack handler （这一版本的 sinatra 使用的是  Mongrel ）是否支持多线程，并且以多线程的方式运行。详见[此处](http://stackoverflow.com/questions/6278817/is-sinatra-multi-threaded)

接下来看 sinatra 互斥锁的实现。

用 `Event` 类变量 `@@mutex` 保存 [Mutex](http://ruby-doc.org/core-1.9.3/Mutex.html) 实例，之后调用 `@@mutex.synchronize do ... end` 实现同一时间只有一个线程的代码——这些代码要么是 `Event` 的类方法，要么是 `Event` 的实例方法——能访问公共资源。一旦用上了互斥锁，同一时间 sinatra 只能响应一个请求。

`run_safely` 会先检查用户是否在运行程序时设置 `use_mutex` 为 `true` 。是则在 `synchronize` 中执行代码，否则直接执行代码。`use_mutex` 默认为 `false` 。

另外几篇参考文章：

- [Ruby - Multithreading](http://www.tutorialspoint.com/ruby/ruby_multithreading.htm)
- [Thread Safety With Ruby](http://lucaguidi.com/2014/03/27/thread-safety-with-ruby.html)
- [Signals, Traps and Rescues](http://www.tutorialspoint.com/ruby/ruby_multithreading.htm)


### before_filters

用户可以使用 before_filters 来做授权、验证、参数过滤等等事情。

sinatra 把 before_filters 跟 after_filters 合二为一，分别写成 `setup_filter` 和 `call_filters` 。

得益于前面使用 cattr_accessor 设置了相应的 setter/getter ，  `setup_filter` 可以通过 `send(filter_set_name)` 来动态获取 filters 数组。

只要 before_filters 中没有抛出 `:halt` 异常的方法，请求就会按照正常的流程执行下去。如果抛出了 `:halt` 异常，处理请求的方法会被跳过，但 after_filters 仍然会被执行。

抛出 `:halt` 异常时可以带上参数，如果是 String 或 Symbol 类型的，就会被当作 helper 方法调用，如果是 Fixnum 类型则会被当成状态码。

这里用到 [Object#case](http://ruby-doc.org/docs/keywords/1.9/Object.html#method-i-case) 方法， `case` 判断一个值是否满足某个条件，用的是这个条件的 `===` 方法，传入这个值作为参数，举个例子：

    x = 10

    case x
    when 10
      p 'x is 10'
    end

    # 上面的代码与下面的代码是一样的

    if 10 === x
      p 'x is 10'
    end

    # 因为 Fixnum 实现了自己的 === 方法，所以下面的用法也没有问题

    case x
    when Fixnum
      p 'x is 10'
    end

全文完。