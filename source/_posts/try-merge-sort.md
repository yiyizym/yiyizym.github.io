title: 写写归并排序
date: 2016-07-29 07:38:54
description: 为什么知道原理还是写不出正确的程序呢？(系列)
categories: tech
tags:
- algorithm
- merge sort
- ruby
---

## 原理

- 将待排序元素分为前后两部分，分别调用归并排序使它们有序
- 从头开始逐个比较前后两部分的元素，根据比较结果先后放进新数组，最终返回这个新数组

## 联想

- 归并排序用到了递归，递归终止的条件是待排序元素数量小于 2
- 归并排序比较之后不会交换元素，而是生成新的数组

## 用法

    #!/usr/bin/env ruby
    sorted_array = MS.sort(array)

## 大体结构

    module MS
      extend self
      def sort(arr)
        merge_sort(arr.dup)
      end

      def merge_sort(arr)
        return arr if arr.length < 2
        #将 arr 一分为二，分别调用归并排序
        #逐一比较这两部分的元素，根据比较结果生成新数组
      end
    end

## 将待排序元素一分为二，分别调用归并排序

    def merge_sort(arr)
      #...
      
      m_index = arr.length / 2
      #这两部分的命名真是头痛，原谅我英语不好
      low_part = merge_sort(arr[0...m_index]) # low_part 不包含位于 m_index 的元素
      high_part = merge_sort(arr[m_index..-1])

      #...
    end

## 逐一比较这两部分的元素，根据比较结果生成新数组

    def merge_sort(arr)
      #...
      
      l_index = 0
      h_index = 0
      new_arr = []

      while low_part[l_index] && high_part[h_index]
        if low_part[l_index] < high_part[h_index]
          new_arr << low_part[l_index]
          l_index += 1
        else
          new_arr << high_part[h_index]
          h_index += 1
        end
      end

      #如果第一部分还有未比较的元素，就放进新数组
      while low_part[l_index]
        new_arr << low_part[l_index]
        l_index += 1
      end
      
      #同上
      while high_part[h_index]
        new_arr << high_part[h_index]
        h_index += 1
      end

      new_arr

    end

## 完整的代码，加测试用例如下：

    #!usr/bin/env ruby

    module MS
     extend self
     def sort(arr)
       merge_sort(arr.dup) 
       end
     def merge_sort(arr)
       return arr if arr.length < 2
       m_index = arr.length / 2
       low_part = merge_sort(arr[0...m_index])
       high_part = merge_sort(arr[m_index..-1])

       l_index = 0
       h_index = 0
       new_arr = []

       while low_part[l_index] && high_part[h_index]
         if low_part[l_index] < high_part[h_index]
           new_arr << low_part[l_index]
           l_index += 1
         else
           new_arr << high_part[h_index]
           h_index += 1
         end
       end

       #如果第一部分还有未比较的元素，就放进新数组
       while low_part[l_index]
         new_arr << low_part[l_index]
         l_index += 1
       end

       #同上
       while high_part[h_index]
         new_arr << high_part[h_index]
         h_index += 1
       end

       new_arr

      end
    end

    if __FILE__ == $0
      require 'test/unit'
      class TestMS < Test::Unit::TestCase
        def test_0
          input = []
          expected = []
          assert_equal MS.sort(input), expected, 'empty array not equal'
        end
        def test_1_0
          input = [0]
          expected = [0]
          assert_equal MS.sort(input), expected, 'one item array not equal'    
        end
        def test_1_1
          input = [1]
          expected = [1]
          assert_equal MS.sort(input), expected, 'one item array not equal'    
        end
        def test_2_0
          input = [0,1]
          expected = [0,1]
          assert_equal MS.sort(input), expected, 'two items array not equal'    
        end
        def test_2_1
          input = [1,0]
          expected = [0,1]
          assert_equal MS.sort(input), expected, 'two items array not equal'    
        end
        def test_2_2
          input = [1,1]
          expected = [1,1]
          assert_equal MS.sort(input), expected, 'two items array not equal'    
        end
        def test_3_0
          input = [0,1,2]
          expected = [0,1,2]
          assert_equal MS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_1
          input = [0,2,1]
          expected = [0,1,2]
          assert_equal MS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_2
          input = [2,1,0]
          expected = [0,1,2]
          assert_equal MS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_3
          input = [2,1,1]
          expected = [1,1,2]
          assert_equal MS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_4
          input = [1,1,1]
          expected = [1,1,1]
          assert_equal MS.sort(input), expected, 'three items array not equal'    
        end
        def test_4_0
          input = [0,1,2,3]
          expected = [0,1,2,3]
          assert_equal MS.sort(input), expected, 'four items array not equal'    
        end
        def test_4_1
          input = [3,1,2,0]
          expected = [0,1,2,3]
          assert_equal MS.sort(input), expected, 'four items array not equal'    
        end
        def test_4_2
          input = [3,1,2,1]
          expected = [1,1,2,3]
          assert_equal MS.sort(input), expected, 'four items array not equal'    
        end
        def test_10_0
          input = [9,8,7,6,5,4,3,2,1,0]
          expected = [0,1,2,3,4,5,6,7,8,9]
          assert_equal MS.sort(input), expected, 'ten items array not equal'    
        end
        def test_10_1
          input = [9,5,7,3,8,4,6,1,2,0]
          expected = [0,1,2,3,4,5,6,7,8,9]
          assert_equal MS.sort(input), expected, 'ten items array not equal'    
        end
      end
    end

PS. 想要跑某个特定的测试，可以这样写： `ruby test.rb -n test_method_name`