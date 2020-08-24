---
layout: post
title: sinatra 0.3.0 源码学习
date: 2016-09-06 21:11:15
excerpt: 通过 sinatra 学习 ruby 编程技巧（系列）
categories: ruby
tags: 
- sinatra
- ruby

---

## 声明

本文系 **sinatra 源码系列**第 5 篇。系列的目的是通过 sinatra 学习 ruby 编程技巧。文章按程序运行的先后顺序挑重点分析，前一篇文章分析过的略去不说。水平很有限，所写尽量给出可靠官方/讨论链接，不坑路人。

## 重要提醒

**一定要先安装 1.8 版本的 ruby** ，因为 1.9+ 的 ruby ，String 的实例是不响应 each 方法的，这会直接导致 rack 报错。可以使用 [rvm](https://rvm.io/) 安装 1.8.7 版本的 ruby ，如果使用 rvm ，请先升级到最新版本，否则安装 1.8.7 的 ruby 时也会报错。

列一下本人运行 sinatra 0.3.0 用到的 ruby 和关键 gem 的版本：

- ruby-1.8.7-p374
- rack 1.4.1
- mongrel 1.1.5

## 本文主要内容

- routes splat
- ResponseHelpers
- middleware

## routes splat

上一篇文章说到 sinatra 没有保存路由中由通配符 * 捕获的参数，这个版本用一个数组保存下来，可以用 `params['splat']` 来访问。具体的实现代码：

    PARAM = /(:(#{URI_CHAR}+)|\*)/.freeze unless defined?(PARAM)
    SPLAT = /(.*?)/
    #...
    splats = 0
    regex = @path.to_s.gsub(PARAM) do |match|
      # match 匹配 /(:(#{URI_CHAR}+)|\*)/
      if match == "*"
        @param_keys << "_splat_#{splats}"
        splats += 1
        SPLAT.to_s
      else
        # 如 /(.)(.)(\d(\d))/.match("THX1138.").captures => ["H", "X", "11", "1"]
        # $1 捕获 (:(#{URI_CHAR}+))
        # $2 捕获 (#{URI_CHAR}+)
        @param_keys << $2
        "(#{URI_CHAR}+)"
      end
    end
    #...
    path_params = param_keys.zip($~.captures.map{|s| unescape(s)}).to_hash
    params.merge!(path_params)
    splats = params.select { |k, v| k =~ /^_splat_\d+$/ }.sort.map(&:last)
    unless splats.empty?
      params.delete_if { |k, v| k =~ /^_splat_\d+$/ }
      params["splat"] = splats
    end

## ResponseHelpers

这里定义的几个方法，可以在路由时使用，如 `redirect` ：


    get '/' do
      redirect '/home'
    end

    get '/home' do
      'welcome!'
    end

`last_modified` 和 `entity_tag` 旨在节省网络流量（和节省计算资源,注释是这样说的），假如客户端请求的资源没有发生变化，就返回 304  Not Modified 。

`last_modified` 大体的实现就是在定义路由时，把响应资源的最后修改时间通过响应头传到浏览器，浏览器再次访问时会在请求头带有上一次请求时得到的时间字段，这时再判断响应资源的最后修改时间与传过来的时间时否一致，如果一致则直接抛出异常，返回 304 。

`entity_tag` 跟 `last_modified` 差不多，只不过比较的不是时间，而是更细粒度、更精确的标记。这个标记可以是用散列函数对资源求值得到哈希值，也可以是硬编码的版本号。

以上两个方法只设置响应头和比较请求头，把时间和标记交由用户管理，这不是很智能。 Rails 用户无需在意某个请求涉及到的一系列资源有没有更新，只要它们都没有更新，前端再次请求时就会得到 304 ，只要更新了一个资源（ partial 或者 layout ），再次请求就会得到最新的响应。


## middleware

中间件的概念比较模糊，可以看[这里](http://stackoverflow.com/questions/2256569/what-is-rack-middleware)。简单来说，中间件可以帮你处理比如验证授权、缓存、打 log 等等的事情，这样你可以专心写业务逻辑。

如果你还是觉得困惑，强烈推荐你看这篇[文章](https://codenoble.com/blog/understanding-rack-middleware/)，它用简单明了的代码在实现中间件的层层调用时，还说清楚了中间件的原理。

上一个版本的 sinatra 就已经用到中间件：

    def build_application
      app = application
      app = Rack::Session::Cookie.new(app) if Sinatra.options.sessions == true
      app = Rack::CommonLogger.new(app) if Sinatra.options.logging == true
      app
    end

上面的 `Rack::Session::Cookie` 和 `Rack::CommonLogger` 都是中间件。中间件有如下特征：

- 能响应 `new` 方法， `new` 方法的参数是下一个中间件或者是应用；
- 能响应 `call` 方法，`call` 方法的参数是 `env` ，即 rack 的环境变量。

这个版本的 sinatra 维护一个数组变量 `middleware` ：

    def middleware
      optional_middleware + explicit_middleware
    end

`optional_middleware` 是由 sinatra 提供的可选的中间件，处于 `middleware` 的前面位置， `explicit_middleware` 是由用户自定义的中间件，用户每次调用 `use` 都会往这个数组的末尾插入新增的中间件。

每一个请求到来时，最终会调用： `pipeline.call(env)` ，`pipeline` 是把所有中间件以及业务处理器层层串连起来得到的新应用：

    def pipeline
      @pipeline ||=
        middleware.inject(method(:dispatch)) do |app,(klass,args,block)|
          klass.new(app, *args, &block)
        end
    end

`@pipeline ||= ...` 的写法使调用 `use` 时重置 `pipeline` 变得很简单，只要写 `pipeline = nil` 就行。

`inject` 跟 `reduce` 一样，根据给出的初始值，遍历处理数组的元素，记住每次处理的结果，并把它传到下一次处理中。

`method(:dispatch)` 是业务处理器，请求经过一系列中间件最后会到达此处。它作为 `Method` 的实例对象，能响应 `call` 方法。

可以看到，请求最先被用户自定义的中间件处理，然后是 sinatra 提供的中间件，最后是业务处理器。处于 `middleware` 数组末尾的中间件最先起作用。