"""第11课：命令行贪吃蛇。

运行：
  python3 snake.py --demo    # 自动走完能吃、能死，用于验收
  python3 snake.py           # 键盘输入 w/a/s/d 游玩
"""

from __future__ import annotations


class Map:
    def __init__(self, height=8, width=12):
        self.height = height
        self.width = width

    def empty_grid(self):
        return [["."] * self.width for _ in range(self.height)]

    def render(self, snake, food):
        grid = self.empty_grid()
        grid[food.row][food.col] = "*"
        for index, (row, col) in enumerate(snake.body):
            grid[row][col] = "O" if index == 0 else "o"
        lines = ["".join(row) for row in grid]
        return "\n".join(lines)


class Food:
    def __init__(self, row, col):
        self.row = row
        self.col = col


class Snake:
    DIRECTIONS = {
        "w": (-1, 0),
        "s": (1, 0),
        "a": (0, -1),
        "d": (0, 1),
    }

    def __init__(self, body):
        self.body = list(body)
        self.alive = True
        self.eaten = 0

    def next_head(self, key):
        dr, dc = self.DIRECTIONS[key]
        head_r, head_c = self.body[0]
        return head_r + dr, head_c + dc

    def move(self, key, food, arena):
        if key not in self.DIRECTIONS:
            return
        nr, nc = self.next_head(key)
        if nr < 0 or nr >= arena.height or nc < 0 or nc >= arena.width:
            self.alive = False
            return
        if (nr, nc) in self.body:
            self.alive = False
            return
        self.body.insert(0, (nr, nc))
        if (nr, nc) == (food.row, food.col):
            self.eaten += 1
        else:
            self.body.pop()


def play():
    arena = Map()
    snake = Snake([(3, 3), (3, 2), (3, 1)])
    food = Food(3, 6)
    print("方向：w上 s下 a左 d右；q退出")
    print(arena.render(snake, food))
    while snake.alive:
        key = input("方向> ").strip().lower()
        if key == "q":
            break
        snake.move(key, food, arena)
        if snake.eaten and (food.row, food.col) == snake.body[0]:
            food = Food(5, 8)
        print(arena.render(snake, food))
        if not snake.alive:
            print("撞墙或咬到自己，游戏结束。吃到食物:", snake.eaten)


def run_demo():
    """非交互验收：向右走到食物，再撞墙。"""
    arena = Map(height=6, width=8)
    snake = Snake([(2, 1), (2, 0)])
    food = Food(2, 3)
    print("=== 第11课 贪吃蛇（自动演示） ===")
    print(arena.render(snake, food))
    snake.move("d", food, arena)
    snake.move("d", food, arena)
    print("--- 吃到食物后 ---")
    print(arena.render(snake, food))
    print("身体长度:", len(snake.body), "已吃:", snake.eaten)
    assert snake.eaten == 1
    assert len(snake.body) == 3
    while snake.alive:
        snake.move("d", food, arena)
    print("撞墙后存活:", snake.alive)
    assert snake.alive is False
    print("本课验收通过：能动、能吃、能撞墙死")
    return snake.eaten, snake.alive


if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        run_demo()
    else:
        play()
