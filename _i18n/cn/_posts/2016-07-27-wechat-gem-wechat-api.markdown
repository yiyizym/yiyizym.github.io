---
layout: post
title: 一个因挪动 wechat_api 引发的问题，以及问题探究
date: 2016-07-27 07:36:56
excerpt: 本想着减少重复代码，把 wechat_api 从各个具体的 controller 挪动到 ApplicationController ，结果出错啦。为了找出原因，我又踏上了阅读源码的不归路。
categories: ruby
tags:
- ruby
- wechat
---

公司的微信企业号用了 [wechat](https://github.com/Eric-Guo/wechat) 这个 gem 包。如果要在各个 controller 中调用 gem 包提供的 api ，就先得在 controller 里调用 `wechat_api` 。如果要使用微信的 JS-SDK ，也得在 controller 里面调用 `wechat_api` 。

近日新增一个 controller ，没有用到 wechat 提供的 api ，所以就没调用 `wechat_api` ，也因为功能简单没有写测试（事后看来不写测试要打屁屁）；在另一次不相干的改动中，我们把微信 JS-SDK 的配置代码移动到 layout 文件中，跑过了所有测试、手动测试了关键功能没发现问题就上线了；几天后才发觉新增的那个 controller 有严重问题，原因是在 layout 中使用微信的 JS-SDK ，而在 controller 中没有调用 `wechat_api` 。

反思得到的结论，最重要的一个是：新增 controller 没写测试用例，其二是： 新增 controller 没调用 `wechat_api` 。

测试用例是一定要补上的。

问题是要加上 `wechat_api` 的调用。今后每增加一个 controller 都要写一遍，这很人肉啊！于是我尝试把这个调用挪动到所有 controller 的共同超类： ApplicationController 中，结果又引发了新问题。


日志显示错误出现在配置 JS-SDK 时， wechat_config_js 这个方法内 controller.wechat 返回 nil 。

首先要看看 wechat_api 究竟做了什么，很快找到它在 wechat_responder.rb 中定义。

它首先 `include Wechat::ControllerApi` ，这个模块里定义了 `wechat` 实例方法，而它又调用 `self.class.wechat` ，里面的注释标明这样做是为了在实例中调用类方法。 而这个类方法实际是个 `attr_accessor` 。


然后是： `self.wechat = load_controller_wechat(opts)`

先不管 ` load_controller_wechat` 到底做了什么，总之最终就是把它返回的结果赋值给 `self.wechat` ，就是把这个值保存在类单例变量(wechat)当中。

至此，出错的原因算是找到了：如果在 ApplicationController 中调用 `wechat_api` ，当在具体的某个 view 里调用 `controller.wechat` 时，会返回 `nil` ，因为这个值是保存在 ApplicationController 的类单例里面。

这样设计能做到对不同的 controller 应用不同的配置（[见此](https://github.com/Eric-Guo/wechat#configure-individual-responder-with-different-appid)）。



要解决这个新问题，比较稳妥的办法就是在各个具体的 controller 中调用 `wechat_api` 。还有一种办法就是重写 `Wechat::ControllerApi` 中的 `wechat` 实例方法，如果类方法 `wechat` 返回 `nil` ，就调用它的超类的 `wechat` 方法：

    def wechat
      self.class.wechat || self.class.superclass.wechat
      # Make sure user can continue access wechat at instance level similar to class level
    end

测试用都跑过了，就是不知道会不会引发新的 bug 。