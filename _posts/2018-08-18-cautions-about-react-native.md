---
layout: post
title: React Native 踩坑记
date: 2018-08-18 07:20:28
excerpt: 初次尝试 React Native 开发需要注意的几点
categories: tech
---

最近初次使用 React Native (以下简称 RN ) 开发了一个简单的应用，途中踩了几个坑，记录下来希望能给后来人一些帮助。

**推荐的入门资料**

初次接触一个框架，最重要的两点就是：搭建环境、运行最小的实例。

一般情况下，因为框架的官网是第一手资料来源，且一直保持更新，推荐直接到框架的官网查看上手文档。

但 RN 比较特殊，框架本身还处在开发阶段（没有发布稳定版本），最新的版本可能会有重大问题，比如 0.56.0 的版本在 windows 平台下根本跑不起来，详见 [issues/19953](https://github.com/facebook/react-native/issues/19953)；

而且 RN 的开发环境分为简易的沙盒环境和完整的原生环境。

前者不需要安装 Android Studio 或者 Xcode ，但需要通过一个叫做 [Expo](https://expo.io) 的应用以扫码或者打开链接的方式运行应用，而由于众所周知的原因，这个应用在国内非常难安装，从用户反馈来看，也非常难用。

后者需要安装 Android Studio 或 Xcode ，可以编译出平台原生代码，还可以通过模拟器或者连接真实设备运行代码。

综上，建议刚入门的朋友到 React Native 中文网查看[上手文档](https://reactnative.cn/docs/getting-started.html)。

**搭建环境**

以开发 Android 应用为例，JDK/Node/react-native-cli 都不难对付（现在安装 SDK 不需要翻墙，如果你下载 SDK 失败，可以用站长工具反查 `SDK Update Sites` 中网站的 ip ，然后设置相应的 host ）。

需要特别注意的是在 windows 平台下 Android 开发环境的搭建。

中文网的文档已经更新到 0.56.0 版本的 RN ，而这个版本有致命问题，在选择 Android Studio 的 SDK 时，得安装与 0.55.0 的相应版本：

- 需要指定 `SDK Platform` 为 `Android 6.0 (Marshmallow)`
- 如果你使用自带的模拟器，还需要安装 `Intel x86 Atom_64 System Image`
- 需要安装版本为 `23.0.1` 的 `Android SDK Build-Tools`

**一个最小的应用实例**

按照中文网的文档，运行 `react-native init AwesomeProject` ，等待一段时间之后就可以初始化一个最小的应用。要注意的是，整个应用的入口不是 `App.js` 文件，而是 `index.js` 文件，在 `index.js` 文件中可以看到有这样一行：

```javascript
AppRegistry.registerComponent(appName, () => App);
```

RN 需要调用 `AppRegistry.registerComponent` 注册作为应用根组件的 `App` ，其他组件是不需要注册的。

在 `App.js` 文件中可以看到，RN 的代码书写跟 react 是非常相似的，不一样的就是 RN 的 JSX 不支持所有的原生标签，在 RN 可以近似把 `View` 组件比作 `div` 标签。

因为 Android Studio 使用 gradle 编译 Android 代码、打包资源、安装应用，初次运行 `react-native run android` 启动应用时，都需要安装 gradle ，而国内安装 gradle 速度非常慢，常常导致这一步耗时严重（你还看不到进度条！）。

解决办法是人工下载相应的 gradle 版本，然后放到合适的目录下，具体方法可以看[这里](https://blog.csdn.net/lxmy2012/article/details/72869397)。

**使用模拟器**

如果你使用 Android 模拟器运行代码，在创建模拟器，选择 `Emulated Performance` 时建议尽量选择硬件，这样会快很多。所有的模拟器在启用硬件加速时都需要显卡支持 OpenGL 2.0 ，如果你的显卡不支持，设法更新驱动。

在 Android 模拟器上连按两下键盘的 `r` 键，会刷新代码；在 windows 下按下 `Ctrl + m` 会调出设置菜单，在 macOS 下对应的是 `Cmd + m` 。在菜单中可以设置 自动刷新、开启元素查看器、 JS 远程调试器。

开启 JS 远程调试时需要特别注意的是，模拟器会在浏览器自动打开一个预设的网址，但这个网址显然是没有运行着 debug 服务器的，这时你需要再次打开设置菜单，点击 `Dev Settings`，在 `Debug server host & port for device` 中设置本机的 ip 和端口，具体来说填写的是：`localhost:8081`。

`8081` 端口号是 `react-native run-android` 这个命令决定的，因为是在本机调试，理论上填 `127.0.0.1` 或者 `localhost` 都行，但实际上 `127.0.0.1` 会连接不上。

**一些技巧**

- 屏幕适配问题

原生应用不像网页，一般来说就算 view 的尺寸过长也不会自动出现滚动条的，而是被截断。所以开发前尽量先明确要适配的屏幕大小，对其他尺寸的屏幕大体来说采用固定某个维度，按一定比例缩放另一维度的方式适配。

本人对这方面研究不多，所说不一定正确，可以参考[这个实现](https://github.com/TerranTian/rn_resolution)。

- 使用 svg

RN 官方不支持 svg ，而第三方对 svg 的支持又很有限。暂时能找到比较好的实现在[这里](https://www.jianshu.com/p/7db2bc62c5ed)。原理大致上是通过 react-native-svg-uri 组件的 svgXmlData 属性加载以 xml 形式保存下来的 svg 文件。

**一些坑**

- 修改后的代码不生效

如果你发现修改后的代码不生效，先看终端里打印的编译信息，很多时候代码不生效是因为编译时遇到语法错误。

- 避免使用 console.error

与 javascript 开发不一样，RN 在开发环境中，一旦执行这句 console.error ，会显示 `red screen error` ，让你误以为应用崩溃了。

- Modal

Modal 是官方弹窗组件。在使用模拟器开发时要注意，不要在 Modal 弹出时按两下 `r` 刷新应用，一定要先关闭 Modal 再刷新应用，否则 Modal 刷新后也不会消失。

- AsyncStorage.getItem

当你需要使用本地持久化功能时，就会使用到 AsyncStorage 这个模块。而在调用  AsyncStorage.getItem 获取之前保存的信息时，非常有意思的是，写在这行代码的下一行代码不生效。如下：

```javascript
let info = AsyncStorage.getItem('key')
console.log('info: ', info) // 这行代码不会执行
console.log('funny!') // 而这行代码会执行
```

这个[问题](https://github.com/facebook/react-native/issues/18372)目前无解。或许可以这样做：

```javascript
let info = AsyncStorage.getItem('key')
// 别手欠删掉这行注释，否则后果自负！https://github.com/facebook/react-native/issues/18372
console.log('info: ', info)
```

**TO Be Continued / つづく / 未完待续**