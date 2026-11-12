import asyncio
import time


# TS 写法：
# function example_1(): void {
#     console.log("例子 1：同步代码先跑完，回调后跑")
#     const loop = asyncio.new_event_loop()
#
#     loop.call_later(0.1, () => console.log("call_later：0.1 秒后跑"))
#     loop.call_soon(() => console.log("call_soon：排进 _ready，第一圈就跑"))
#     console.log("同步代码 A")
#     console.log("同步代码 B")
#
#     loop.call_later(0.2, () => loop.stop())
#     loop.run_forever()
#     loop.close()
# }
def example_1() -> None:
    print("例子 1：同步代码先跑完，回调后跑")
    loop = asyncio.new_event_loop() #初始化了一个 loop 实例

    # settimeout(print, 0.1, "call_later：0.1 秒后跑")
    loop.call_later(0.1, print, "call_later：0.1 秒后跑") # 0.1秒以后执行 - 取餐台
    # setimmediate setimeout(fn, 0) 
    loop.call_soon(print, "call_soon：排进 _ready，第一圈就跑") # 0秒 = 立刻执行 后厨 这里有个单你要帮我弄一下， 弄完以后放到取餐台 几乎是瞬间就放到取餐台
    # 前台也就是主线程什么时候去看取餐台？？ 等前面没人排队了再去看取餐台有没有送餐的
    print("同步代码 A")
    print("同步代码 B")

    loop.call_later(0.2, loop.stop) # ---> 交给后厨
    # yield <---ticker.stop 
    loop.run_forever() # 咖位很大 大明星 摆谱来的  所以到这里 后面的代码就被阻塞了， 那主线程没办法 前台没办法 就去看取餐台
    loop.close()

# 输出结果
# 例子 1：同步代码先跑完，回调后跑
# 同步代码 A
# 同步代码 B
# call_soon：排进 _ready，第一圈就跑
# call_later：0.1 秒后跑

# 调用loop.stop ： 家长来了 把大小姐给带走了
# clearinterval: 回收内存

# 取餐台有什么
# 第一格： callsoon的打印
# 第二格： calllater 的 0.1
# 第三格： 0.2 秒的 calllater


# 会不会打印  不会 异步代码



def example_2() -> None:
    print("例子 2：同步代码卡住，计时器到点了也跑不了")
    loop = asyncio.new_event_loop()
    start = time.time()

    # function timer(){
        # print(f"计时器：说好 0.5 秒，实际 {time.time() - start:.1f} 秒")
    # }

    def timer() -> None:
        print(f"计时器：说好 0.5 秒，实际 {time.time() - start:.1f} 秒")

    loop.call_later(0.5, timer) # 会执行 但是是交给后厨 后厨 0.5 秒以后放到取餐台
    print("同步代码：卡 2 秒")
    time.sleep(2) # 大小姐 等于是让主线程休息几秒钟 暂停几秒钟
    print("同步代码：跑完了")

    loop.call_later(0.1, loop.stop) # 会执行但是交给后厨 0.1秒以后 执行 loop.stop
    loop.run_forever() #又卡着了 
    loop.close()

# 输出
# 例子 2：同步代码卡住，计时器到点了也跑不了
# 同步代码：卡 2 秒
# 同步代码：跑完了
# 计时器：说好 0.5 秒，实际

# 执行stop

# 取餐台
# 第一格: 0.5的任务, 尽管后厨在 0.5秒以后就把东西放到取餐台了  但是因为主线程被强制暂停了 2 秒钟 所以当前台来取餐台看的时候已经是至少过了 2 秒钟了对吧
# loop.stop




def example_3() -> None:
    print("例子 3：计时器已经进了 _ready，前面的回调卡住，它也只能等")
    loop = asyncio.new_event_loop()
    start = time.time()


    def slow() -> None:
        print("slow 回调：卡 2 秒")
        time.sleep(2)

    def timer() -> None:
        print(f"计时器：说好 0.5 秒，实际 {time.time() - start:.1f} 秒")

    when = loop.time() + 0.5
    loop.call_at(when, slow) # 异步送后厨， 后厨发现是 0.5s 所以在 0.5s 以后会送到取餐台等待前台拿货
    loop.call_at(when, timer) # 异步送后厨， 后厨发现是0.5 ,所以在 0.5s 以后会送到取餐台等待前台拿货

    loop.call_later(3, loop.stop) # 异步送后厨 3 秒钟以后送取餐台
    loop.run_forever()
    loop.close()

# 无论是定时器还是网络请求等所有的异步任务： 只要主线程是被同步代码占线繁忙的， 你得异步就永远不可能被调用
# 输出
# 例子 3：计时器已经进了 _ready，前面的回调卡住，它也只能等
# slow 回调：卡 2 秒"
# 计时器：说好 0.5 秒，实际 2 秒 多少微秒

# TS 写法：
# function main(): void {
#     example_1()
#     console.log()
#     example_2()
#     console.log()
#     example_3()
# }
def main() -> None:
    # example_1()
    # print()
    # example_2()
    # print()
    example_3()
