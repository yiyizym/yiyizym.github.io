---
layout: post
title: width属性取100%时与inherit的区别
description: "width属性取100%时与inherit的区别"
keywords: width, CSS, inherit, specified value, 继承
categories: frontend
---
width属性不可继承，默认值是auto。

元素的width属性值为percentage时，width是根据其包含块的width计算的，如果其包含块的width反而是根据此元素的width计算出来的，这种情况CSS2.1未定义。

元素的width属性值为inherit时(inherit可用于那些不可继承的属性上)，其继承的是父元素width属性的声明值(specified value)。

声明值(specified value)按以下三个原则取值：
1. 如果元素样式表中有定义（无论是由作者、用户、还是浏览器定义）属性及其值，则其为声明值；
2. 否则，如果元素并非文档树的根，且属性是可继承的，则从其父元素继承声明值（继承父元素相应属性的计算后的值(computed value)）；
3. 否则，声明值为元素对应属性的默认值。

借用知乎上的一个例子：

	<style>
		#d0{width:300px;}
		#d1{width:100%;padding:10px;background:#ddd;}
		#d2{width:inherit;padding:10px;background:#ccc;}
	</style>
	<div id="d0">
		<div>
			<div id="d1"></div>
			<div id="d2"></div>
		</div>
	</div>

没有id的那个div，其width值为auto，d2的width实际上也是auto。因为width取值为auto时，margin及padding将向内压缩内容,所以d2的width只有280px。而d1的width根据div算出是300px，因为还有20px的padding，所以d1会溢出。

###参考文献
- [容易理解的对specified value的解释](https://developer.mozilla.org/en-US/docs/Web/CSS/specified_value)
- [更准确的specified value解释](http://www.w3.org/TR/CSS2/cascade.html#specified-value)
- [visual formatting model details中width属性值的说明](http://www.w3.org/TR/CSS21/visudet.html#the-width-property)
- [Assigning property values, Cascading, and Inheritance中对inherit值的说明](http://www.w3.org/TR/CSS21/cascade.html#value-def-inherit)