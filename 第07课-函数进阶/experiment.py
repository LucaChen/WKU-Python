"""第7课：默认参数、多返回值、作用域。"""


def add_sub(a, b=1):
    return a + b, a - b


def demo_scope():
    x = 10

    def change():
        x = 1
        return x

    inner = change()
    return x, inner


def shadow_builtin_print():
    """故意把自定义函数命名为 print，体会覆盖内置名。"""
    real_print = __builtins__.print if not isinstance(__builtins__, dict) else __builtins__["print"]

    def print(msg):  # noqa: A001
        real_print("被覆盖的 print 收到:", msg)

    print("hello")
    real_print("调用真正的打印函数才恢复输出")


def main():
    print("=== 第7课 函数进阶 ===")
    shadow_builtin_print()

    both = add_sub(8)
    s, d = add_sub(8, 3)
    print("默认参数 add_sub(8) =", both, type(both).__name__)
    print("拆包 add_sub(8, 3) =", s, d)

    outside, inside = demo_scope()
    print("函数外 x =", outside, "函数内 x =", inside)
    assert outside == 10
    print("本课验收通过")
    return both, (s, d), (outside, inside)


if __name__ == "__main__":
    main()
