"""第2课：变量、类型与字符串。"""


def main():
    print("=== 第2课 变量、类型与字符串 ===")
    data = 36
    print("第一次赋值:", data)
    data = 18
    print("覆盖之后:", data)

    print("3 / 2 =", 3 / 2, type(3 / 2))
    print("int(3.9) =", int(3.9), "（截断，不是四舍五入）")
    print('float("8.8") =', float("8.8"))

    first = "Python"
    second = "实践课"
    print("拼接:", first + second)

    try:
        result = "1" + 1
        print(result)
    except TypeError as exc:
        print("数字加字符串报错（预期）:", type(exc).__name__)

    print("本课验收通过")


if __name__ == "__main__":
    main()
