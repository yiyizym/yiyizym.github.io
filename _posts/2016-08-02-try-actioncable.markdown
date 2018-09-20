---
layout: post_with_octocat
title: 试用 Action Cable
date: 2016-08-02 20:54:33
description: Rails 5 出来很久了，学习一下 Action Cable
categories: ruby
tags:
- ruby
- rails
- websocket
- action cable
---

## Action Cable 有什么用

Action Cable 是一项满足客户端与服务器端实时通讯需求的功能，它基于 WebSocket 协议。在此之前 web 端要满足类似的需求，有 轮询、长轮询、SSE（Server Sent Events ，sinatra 自带一个简单的实现，有兴趣可以看看） 等方法，综合考虑开销和兼容性，基于 WebSocket 的实现是最好的。

## WebSocket 的基本知识

websocket 是建立在 TCP 协议上面应用层的协议，整个协议由两部分组成： 握手建立连接，数据传输。要建立 websocket 连接，得先由客户端发送一个 http get 请求，带上相关的请求头，只有当服务器端带上正确的响应头回复时，连接才能建立。之后客户端和服务器端可以向对方发送数据。

更详细的说明，可以看[这里](https://tools.ietf.org/html/rfc6455)

如果想简单地动手玩玩 websocket ，请参考[这篇文章](https://www.rails365.net/articles/websocket-zhi-ke-hu-duan-yu-fu-wu-qi-duan-di-jiao-hu-er)

## Action Cable 基础概念

用户打开的每个浏览器标签页都会跟服务器建立一条新连接(connection)，Rails 会为这条连接实例化一个 connection 对象，这个对象负责管理此后发生的订阅事件，它不处理具体的业务逻辑。

客户端可以通过一个连接订阅多个频道(channel)。每个频道都提供多个 websocket 的回调方法，方便写业务逻辑代码。

一个频道可以包含一个或多个流(stream)，如果把频道比作网络游戏平台中的某个分区，那么流就是分区下面的某个房间。流是 Action Cable 中发送、接收消息的最小单位。


服务器可以在建立连接时设置验证（用异步的方式），一旦验证失败，将关闭已建立的连接。

整个 Action Cable 的架构粗略看起来就是下面的样子：

    connections  <==   channels  <==   streams <--> subscriptions  ==>   connections

    <== 表示 一 对 多 的关系

    <--> 表示 一对一 的关系

    ==> 表示 多对一 的关系


## Action Cable 基本配置

**以下代码、说明仅在 Rails 5.0.0 版本（不是 beta 版本）测试过，不同版本间 Action Cable 的表现有稍许区别。**

既然 websocket 需要由客户端发起(握手请求)，先从前端需要做的事情说起。

运行 `rails new my_actioncable` 新建一个 Rails 项目。

在 `app/assets/javascripts/cable.js` ，Rails 已经替你准备好前端的 connection 实例：

    (function() {
      this.App || (this.App = {});

      App.cable = ActionCable.createConsumer();

    }).call(this);


为方便调试，你可以添加一行启用调试的代码：

    (function() {
      this.App || (this.App = {});

      App.cable = ActionCable.createConsumer();
      ActionCable.startDebugging(); // 启用调试

    }).call(this);

连接创建好之后，接着创建一个订阅。在 `assets/javascripts/channels` 目录下新建 `room.js` 文件，内容如下：

    App.room = App.cable.subscriptions.create("RoomChannel", {
      connected: function(){
        // Called when the subscription is ready for use on the server
        },
      disconnected: function() {
        // Called when the subscription has been terminated by the server
      },

      received: function(data) {
        // Called when there's incoming data on the websocket for this channel
      }
    });

create 方法第一个参数可以是字符串，也可以是对象；如果是字符串，它表示要订阅的频道，如果是对象，则一定要带有 key 为 channel 的字段，其他字段可以传给后台别作它用（比如创建流），如：

    {
      channel: 'RoomChannel',
      label: '1st'
    }

create 方法第二个参数包含一系列的回调方法，各自用途注释都写得很清楚。

前端的事情就做完了，开始设置后台。

Action Cable 可以独立于我们的应用运行，也可以作为[引擎](http://guides.ruby-china.org/engines.html)挂载到我们的应用中。这里我们选择挂载。

在 `routes.rb` 添加一行：

    mount ActionCable.server => '/cable'

这样发向 '/cable' 的请求将由 Action Cable 处理。

在 `app/channels` 目录下新建 `room_channel.rb` ，内容如下：

    class RoomChannel < ApplicationCable::Channel
      def subscribed
        stream_from 'room_channel'
      end
      def unsubscribed
        # Any cleanup needed when channel is unsubscribed
      end
    end

`steam_from` 新建一个流，如果前端在调用 App.cable.subscriptions.create 时第一个参数是对象，可以通过 `params` 来获取对象的内容：


    # 假设 第一个参数是对象
    # {
    #   channel: 'RoomChannel',
    #   label: '1st'
    # }

    def subscribed
      stream_from "room:#{params[:label]}"
    end

运行 `rails g controller room show` 生成控制器、路由和一个简单的 `show` 页面。

现在前后台都搭好了，得到一个最简单，什么都不能做的 Action Cable 。运行 `rails s` 启动服务器端，打开浏览器访问 `localhost:3000/room/show`

在浏览器的控制台可以看到类似以下的信息：


    [ActionCable] Opening WebSocket, current state is null, subprotocols: actioncable-v1-json,actioncable-unsupported 1470455374056 action_cable.self-1641ec3….js?body=1:50 
    [ActionCable] ConnectionMonitor started. pollInterval = 3000 ms 1470455374063 action_cable.self-1641ec3….js?body=1:50 
    [ActionCable] WebSocket onopen event, using 'actioncable-v1-json' subprotocol 1470455374081 action_cable.self-1641ec3….js?body=1:50 
    [ActionCable] ConnectionMonitor recorded connect 1470455374082

切换到控制台的 Network 标签，查看 WebSockets ，可以看到浏览器每隔 3 秒会收到服务器端发过来的 ping 包。

## 服务器主动向客户端推送消息

服务器可以主动通过广播向客户端推送消息。

为免阻塞正常的 http 响应，通常会采用 delayed job 来向客户端推送消息。

运行命令 `rails g job send_msg` 新建一个 delayed job ，在新建的 `send_room_msg_job.rb` 中的 `perform` 方法中添加：

    # 每 3 秒向客户端发送一条信息
    1.upto(10) do |i|
      sleep 3
      ActionCable.server.broadcast(
          'room_channel', # 这是流的名字，要跟在 stream_from 定义的保持一致
          title: 'the title',
          body: "server send #{i}"
      )
    end

然后在 `RoomController#show` 方法中添加：

    SendRoomMsgJob.perform_later


客户端接收部分，重写 `assets/javascripts/channels/room.js` 的 `received` 回调方法：

    //...

    received: function(data) {
      var msg = data['title'] + '\n' + data['body'] + '\n';
      //简单地打印接收到的信息
      console.log(msg);
    }


重启服务器、重新访问 `localhost:3000/room/show` ，每隔 3 秒就能看到打印信息。


## 客户端主动向服务器发送消息

客户端也可以主动调用服务器端在 channel 中定义的方法。

重写 `assets/javascripts/channels/room.js` 的 `connected` 回调方法：

    //...

    connected: function(){
      this.perform('print_log', { msg: 'send from client' });
    }

在 `room_channel.rb` 中添加一个 `print_log` 方法：

    #...

    def print_log(data)
      p ">>>> #{data['msg']}"
    end


只要连接一建立，就可以在服务器后台看到打印 `>>>> message from client`


以上就是简单的 Action Cable 试用记录，源码已经上传至 [github](https://github.com/yiyizym/try_action_cable) 。

参考文章：

- [Action Cable Overview](http://edgeguides.rubyonrails.org/action_cable_overview.html#broadcasting)
- [websocket序列文章](https://www.rails365.net/articles/websocket-xu-lie-wen-zhang-mu-lu)
- Action Cable Source Code ，我翻了两天的源码。。。。