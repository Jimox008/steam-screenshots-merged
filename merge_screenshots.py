'''
Author: Nemo
LastEditors: Nemo
Description: 
岁月终将流逝，唯有美人不朽
'''
#!/usr/bin/env python3
"""
合并两个Steam截图VDF文件（screenshots.vdf格式）。
用法：
    python merge_screenshots.py <输入文件1> <输入文件2> <输出文件>
示例：
    python merge_screenshots.py screenshots1.vdf screenshots2.vdf merged.vdf
"""

import vdf
import sys
import argparse
from pathlib import Path

def load_vdf(path):
    """读取VDF文件并返回VDFDict对象"""
    with open(path, 'r', encoding='utf-8') as f:
        return vdf.load(f, mapper=vdf.VDFDict)

def dump_vdf(data, path):
    """将VDFDict写入文件"""
    with open(path, 'w', encoding='utf-8') as f:
        vdf.dump(data, f, pretty=True)

def merge_screenshots(target, source):
    """
    将源文件中的截图条目追加到目标文件中。
    target 和 source 都是已加载的 VDFDict 对象。
    """
    # 获取两个文件的 "screenshots" 块
    target_sc = target.get('screenshots', vdf.VDFDict())
    source_sc = source.get('screenshots', vdf.VDFDict())

    # 遍历源文件中的每个游戏ID
    for game_id, game_screenshots in source_sc.items():
        # 如果目标中已有该游戏ID，则进行追加（重新编号）
        if game_id in target_sc:
            # 获取目标中该游戏ID下现有的数字索引
            existing_nums = [int(k) for k in target_sc[game_id].keys() if k.isdigit()]
            next_index = max(existing_nums) + 1 if existing_nums else 0

            # 将源中的截图条目逐个重新编号后添加到目标
            for screenshot_index, screenshot_data in game_screenshots.items():
                # 只处理数字键（即真正的截图条目）
                if screenshot_index.isdigit():
                    # 重新编号
                    new_index = str(next_index)
                    target_sc[game_id][new_index] = screenshot_data
                    next_index += 1
                else:
                    # 如果有非数字键（如注释或特殊字段），直接覆盖（可根据需求调整）
                    target_sc[game_id][screenshot_index] = screenshot_data
        else:
            # 目标中不存在该游戏ID，直接复制整个游戏ID块
            target_sc[game_id] = game_screenshots

    # 将更新后的 screenshots 块放回 target
    target['screenshots'] = target_sc
    return target

def main():
    parser = argparse.ArgumentParser(
        description='合并两个Steam截图VDF文件，将第二个文件中的截图追加到第一个文件中。',
        epilog='示例：%(prog)s base.vdf extra.vdf merged.vdf'
    )
    parser.add_argument('input1', help='第一个输入VDF文件（基础文件）')
    parser.add_argument('input2', help='第二个输入VDF文件（要追加的文件）')
    parser.add_argument('output', help='合并后的输出文件')
    args = parser.parse_args()

    # 检查输入文件是否存在
    for f in [args.input1, args.input2]:
        if not Path(f).is_file():
            print(f"错误：文件不存在 - {f}", file=sys.stderr)
            sys.exit(1)

    try:
        print(f"正在读取 {args.input1} ...")
        target_data = load_vdf(args.input1)
        print(f"正在读取 {args.input2} ...")
        source_data = load_vdf(args.input2)

        print("正在合并...")
        merged = merge_screenshots(target_data, source_data)

        print(f"正在写入 {args.output} ...")
        dump_vdf(merged, args.output)
        print("合并完成！")
    except Exception as e:
        print(f"处理过程中出错：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
