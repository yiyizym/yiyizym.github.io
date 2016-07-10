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