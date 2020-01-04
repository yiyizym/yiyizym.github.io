---
layout: post
title: 写写插入排序
date: 2016-07-05 08:06:17
excerpt: 为什么知道原理还是写不出正确的程序呢？(系列)
categories: tech
tags:
- algorithm
- insertion sort
- ruby

---

这是一个基础算法系列，主题是：为什么知道原理还是写不出正确的程序呢？

第一篇已经写好，叫做[我尝试去写快排，结果。。。]()。文章结构都差不多：原理、联想、用法、框架、分步实现、完整代码及测试用例。

## 原理

插入排序的原理是：
- 将集合分为两个部分：已排好的部分和待排序的部分
- 每次从待排序部分抽一个元素跟已排好部分中的元素逐一比较，直到找到合适的位置，插入待排序元素
- 合适的位置可以是第一个比待排序元素小（大）的，也可能是已排好部分的下界

## 联想
- 可以用一个数组下标将集合分成两部分，比下标小的是已排好部分，比下标大的是待排序部分
- 整个排序过程可以用嵌套两层循环，外层遍历待排序部分，内层遍历已排好部分
- 每次比较都有可能发生一次元素交换

## 用法

    #!/usr/bin/env ruby
    sorted_array = IS.sort(array)

## 大致框架

    #!/usr/bin/env ruby
    class IS
      class << self
        def sort array
          while condition1
            while condition2

            end
          end
        end
        def exchange array, i, j
          array[i], array[j] = array[j], array[i]
        end
      end
    end

## 外层循环的上下界

容易想到外层循环的下界小于数组的大小，但上界是什么呢？选 0 是可以的，只是会浪费一次外层循环（因为它前面没有可比较元素），出于不浪费的考虑，选 1 。源码：

    #!/usr/bin/env ruby
    class IS
      class << self
        def sort array
          # 外层循环
          index = 1
          len = array.size
          while index < len
            #inner loop
          index += 1
          end
        end
      end
    end

## 内层循环要做什么？

内层循环要做的就是把待排序元素的第一个元素通过一次次比较，放到已排序集合中合适的位置。循环的上界是外层循环中的 index ，下界是什么呢？ 因为每次都是与索引值小 1 的元素比较，为免数组越界，当前索引值最小是 1 。源码：

    #!/usr/bin/env ruby
    class IS
      class << self
        def sort array
          index = 1
          len = array.size
          while index < len
            inner_index = index
            # 内层循环
            while inner_index >= 1 && array[inner_index] < array[inner_index - 1]
              exchange(array, inner_index, inner_index - 1)
              inner_index -= 1
            end
            index += 1
          end
        end
      end
    end

## 完整的代码，加测试用例如下：

    #!/usr/bin/env ruby
    class IS
      class << self
        def sort array
          index = 1
          len = array.size
          while index < len
            inner_index = index
            while inner_index >= 1 && array[inner_index] < array[inner_index-1]
              exchange(array, inner_index, inner_index-1)
              inner_index -= 1
            end
            index += 1
          end
          array
        end
        def exchange array, i, j
          array[i], array[j] = array[j], array[i]
        end
      end
    end

    if __FILE__ == $0

      require 'test/unit'

      class TestIS < Test::Unit::TestCase
        def test_0
          input = []
          expected = []
          assert_equal IS.sort(input), expected, 'empty array not equal'
        end
        def test_1_0
          input = [0]
          expected = [0]
          assert_equal IS.sort(input), expected, 'one item array not equal'    
        end
        def test_1_1
          input = [1]
          expected = [1]
          assert_equal IS.sort(input), expected, 'one item array not equal'    
        end
        def test_2_0
          input = [0,1]
          expected = [0,1]
          assert_equal IS.sort(input), expected, 'two items array not equal'    
        end
        def test_2_1
          input = [1,0]
          expected = [0,1]
          assert_equal IS.sort(input), expected, 'two items array not equal'    
        end
        def test_2_2
          input = [1,1]
          expected = [1,1]
          assert_equal IS.sort(input), expected, 'two items array not equal'    
        end
        def test_3_0
          input = [0,1,2]
          expected = [0,1,2]
          assert_equal IS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_1
          input = [0,2,1]
          expected = [0,1,2]
          assert_equal IS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_2
          input = [2,1,0]
          expected = [0,1,2]
          assert_equal IS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_3
          input = [2,1,1]
          expected = [1,1,2]
          assert_equal IS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_4
          input = [1,1,1]
          expected = [1,1,1]
          assert_equal IS.sort(input), expected, 'three items array not equal'    
        end
        def test_4_0
          input = [0,1,2,3]
          expected = [0,1,2,3]
          assert_equal IS.sort(input), expected, 'four items array not equal'    
        end
        def test_4_1
          input = [3,1,2,0]
          expected = [0,1,2,3]
          assert_equal IS.sort(input), expected, 'four items array not equal'    
        end
        def test_4_2
          input = [3,1,2,1]
          expected = [1,1,2,3]
          assert_equal IS.sort(input), expected, 'four items array not equal'    
        end
      end
    end