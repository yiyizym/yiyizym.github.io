---
layout: post
title: 用 webpack 打包多个 html 
date: 2017-09-09 03:20:09
excerpt: 一个简单的使用样例
categories: frontend
---

## 更新

项目基于 webpack 2.X 版本，对应的源码在 master 分支；如果想使用 webpack 4.X ，请切换到 webpack4 分支。 webpack 4.X 大致思路不变，但配置 webpack 时的写法有变，同时可能要升级一些依赖。当控制台提示某个包缺少相应版本的 webpack 时，直接 `npm install 包名` 升级那个包就行。

## 序
通常我们只会用 webpack 把多个入口文件打包成一个出口文件，然后用一个 html 引用这个出口文件，做成单页应用。

本文要满足的是另一种场景：把多个入口文件打包成多个出口文件，用多个 html 文件分别引用这些出口文件。

具体的目标如下：
- 最终生成 pageA.html 和 pageB.html 两个页面
- 两个页面共用相同的样式，且样式都是嵌入在页面里（有必要的话可以提取成单独的样式文件，只是样式不是这个例子的重点）
- 两个页面有共用的脚本文件 common.js ，也有各自的脚本文件 pageA.js 和 pageB.js ，页面不会引用与自己无关的脚本文件。

使用到的 webpack 插件有 HtmlWebpackPlugin 和 WebpackCleanupPlugin

## 生成项目信息

首先，新建一个目录，并跳转进去：`md webpack_muti_html && cd webpack_muti_html`

运行 `npm init` ，一路`enter`

这样会生成一个 `package.json` 文件

## 安装依赖

然后安装项目所需依赖，这个项目是以 2.0 版本以上的 webpack 为基础的，所以得安装 2.X 版本的 webpack ，运行下面的命令：
```bash
npm install webpack@2 -D
# -D 选项表明 webpack 只作为开发时的依赖包，用户在使用时并不需要这个包
# 如果用户在访问页面时也要使用到这个依赖包，需要用 -S 选项
```
这样会在 package.json 文件中生成一项：
```javascript
//...
"devDependencies": {
    "webpack": "^2.7.0"
}
//...
```
同理，把其它需要的依赖也安装好：
```bash
npm install -D css-loader style-loader html-webpack-plugin webpack-cleanup-plugin
```
## 编写源文件
- 新建目录 `src/tpl` ，在此目录下新建文件 pageA.html ，内容如下：
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>Page A</title>
    </head>
    <body>
        
    </body>
    </html>
    ```
    新建文件 pageB.html ，内容与此类似

- 新建目录 `src/js` ，新建文件 common.js ，内容如下：
    ```javascript
    const common = {
        print: function(){
            document.body.innerHTML = 'common script goes here !';
        }
    }
    module.exports = common; 
    ```
    新建文件 pageA.js ，内容如下：
    ```javascript
    import common from './common.js';
    import a from './a.js';
    import '../css/common.css';

    common.print();
    a.alert();
    ```

    新建文件 a.js ，内容如下：
    ```javascript
    const a = {
        alert: function(){
            alert('pageA script goes here !')
        }
    }
    module.exports = a;
    ```

    新建文件 pageB.js ，内容如下：
    ```javascript
    import common from './common.js';
    import b from './b.js';
    import '../css/common.css';

    common.print();
    b.alert();
    ```

    新建文件 b.js ，内容如下：
    ```javascript
    const b = {
        alert: function(){
            alert('pageB script goes here !')
        }
    }
    module.exports = b;
    ```

- 新建目录 `src/css` ，新建文件 common.css ，内容如下：
    ```css
    body {
        color: blue;
    }
    ```

## 编写脚本文件
我们希望能使用 npm script 打包，比如在根目录下运行以下命令就能打包：
```bash
npm run build 
```
在 package.json 文件中的 `scirpts` 字段加上这样一行 `"build": "node build.js"`，于是 `scripts` 变成这样：
```javascript
//...
"scirpts": {
    "test": "echo \"Error: no test specified\" && exit 1",
    "build": "node build.js"
}
//...
```
接下来在根目录新建一个 `build.js` 文件，这个文件会调用 webpack 实现打包，内容如下：
```javascript
'use strict';
const fs = require('fs');
const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const WebpackCleanupPlugin  = require('webpack-cleanup-plugin');
const outputRoot = path.resolve(__dirname, './output');
const srcRoot = path.resolve(__dirname, './src');

var webpackConfig = {
    entry: {},//具体内容由后面编写的脚本填充
    output: {
        path: outputRoot,
        filename: '[name].js'
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                loader: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: [
        // 用于清空 output 目录
        new WebpackCleanupPlugin(),
    ],
    // devtool 更详细的资料：https://segmentfault.com/a/1190000008315937
    devtool: '#eval-source-map-inline'
}


let filenames = fs.readdirSync(path.resolve(srcRoot, 'tpl'));

filenames.forEach(function(filename){
    let stats = fs.statSync(path.resolve(srcRoot, 'tpl', filename));
    if(stats.isFile()){
        let extension = path.extname(filename);
        let name = filename.substring(0,filename.lastIndexOf(extension));
        webpackConfig.entry[name] = path.resolve(srcRoot, 'js', name + '.js')
        webpackConfig.plugins.push(new HtmlWebpackPlugin({
            filename: name + '.html',
            template: path.resolve(srcRoot, 'tpl', name + '.html'),
            inject: true,
            chunks: ['common', name] //这个设置使得每个 html 只包含 common 以及与自己命名相同的那一个 chunk
        }));
    }
});

webpack(webpackConfig, function (err, stats) {
  if (err) throw err
  process.stdout.write(stats.toString({
    colors: true,
    modules: false,
    children: false,
    chunks: false,
    chunkModules: false
  }) + '\n')
})

```

最后，双击把开 output 目录的 html 文件就能看到效果。

## 补充

以上只是一个简单的 demo ，更复杂的例子，比如支持 babel 编译、提取样式文件、区分环境、支持 webpack server 等等功能，可见[这里](https://github.com/yiyizym/webpack_from_scratch)。