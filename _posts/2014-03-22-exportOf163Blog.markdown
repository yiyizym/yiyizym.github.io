---
layout: post
title: "导出网易博客"
excerpt: "折腾了一下，把之前在网易的博客文章导出成md格式"
date: 2014-03-22 16:47:38
keywords: 博客迁出, 网易, xml, python, 正则
lang: zh_CN
categories: life
---

最近想把在网易上写的博客迁移过来，也动手做了。但网易博客貌似只有迁进没有迁出的功能。

google了一下，发现可以xml格式导出博客内容。具体方法是在 ++个人博客中心++个人博客中心 页面的最下方，点RSS按钮，再保存这个弹出的页面就OK了。

之后的工作就是从这个文件提取内容，我只会用python做这种事。

关于XML格式相关基础知识，可以看 [这里](http://www.w3schools.com/xml/)（w3school）。处理导出的XML文件所用到的XML知识都可以从中找到。

python有处理XML的包（package）：xml，xml包里有好几个子模块：
> xml.etree.ElementTree,
> xml.dom,
> xml.dom.minidom,
> xml.dom.pulldom,
> xml.sax,
> xml.parsers.expat

我没有深入了解它们的差别，有兴趣可以看 [这里](http://docs.python.org/2/library/xml.html)（官方文档）。官方建议若对DOM不熟悉就使用xml.etree.ElementTre：
>Users who are not already proficient with the DOM should consider using the xml.etree.ElementTree module for their XML processing instead

使用 xml.etree.ElementTree 的确比较方便。只是xml.etree.ElementTree 对CDATA节点的支持不好，可以说是无视。对以下节点：

`<title><![CDATA[title]]></title>`

应用`node.txt`得到的是`title`。不过在这次的xml文档处理正好可以利用这个特性。


回过头来说说从网易导出的xml文档，文章标题、发表日期、修改日期、作者都可以轻易解决，唯独 正文 中夹杂着很多html标签，不能直接用。

我用正则表达式来对付正文。只要用空字符串替换匹配的所有html标签就OK。要匹配html标签也很简单，用这个字符串`'</?[^>]+>'`就行。

剩下就只有把读取到的内容写进新文件。原本打算用读取得来的title作为写文件的文件名，但python提示错误：

`IOError: [Errno 22] invalid mode ('w') or filename`

没找到解决的办法，这个问题就先留着吧。

废话不多说，上代码：

```
#encoding:UTF-8
import xml.etree.ElementTree as ET
import re

tree = ET.parse('blog163.xml')
root = tree.getroot()
i = 0
for item in root.iter('item'):
	#.text方法得到的字符串是Unicode编码，需要转换成UTF-8编码
    title = item.find('title').text.encode('UTF-8')
    pubDate = item.find('pubDate').text.encode('UTF-8')
    postContent = item.find('description').text.encode('UTF-8')
    pattern = re.compile(r'</?[^>]+>')
    patternNBSP = re.compile(r'&nbsp;')
    result = re.sub(pattern, '', postContent)
    resultReplaceNBSP = re.sub(patternNBSP,'\n',result)
    fileName = str(i)
    i += 1
    newFile = file('blog163/' + fileName + '.md' ,'w')
    newFile.write(title + '\n\n')
    newFile.write(pubDate + '\n\n')
    newFile.write(removResultNBSP)
    newFile.close()
```