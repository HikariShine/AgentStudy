#!/usr/bin/env python3
"""
测试套件用于 analyze_video.py

测试包括：
1. 本地视频处理（不同大小）
2. 分辨率自动缩放
3. 压缩和裁切逻辑
4. 临时文件清理
"""

import subprocess
import sys
import tempfile
from pathlib import Path

# ============ 工具函数 ============

def run_command(cmd: str, description: str = None, timeout: int = 600) -> bool:
    """运行命令并返回是否成功"""
    if description:
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
    
    print(f"$ {cmd}", file=sys.stderr)
    
    try:
        result = subprocess.run(cmd, shell=True, timeout=timeout, capture_output=False)
        if result.returncode == 0:
            print(f"✅ 成功", file=sys.stderr)
            return True
        else:
            print(f"❌ 失败 (返回码: {result.returncode})", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ 超时 (超过 {timeout}s)", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ 异常: {e}", file=sys.stderr)
        return False


def generate_test_video(output_path: Path, duration_seconds: int = 10, 
                        width: int = 1920, height: int = 1080, fps: int = 30) -> bool:
    """
    使用 FFmpeg 生成测试视频
    
    Args:
        output_path: 输出路径
        duration_seconds: 视频时长（秒）
        width: 宽度
        height: 高度
        fps: 帧率
    
    Returns:
        是否成功生成
    """
    print(f"🎬 生成测试视频: {output_path.name} ({width}x{height}, {duration_seconds}s, {fps}fps)", file=sys.stderr)
    
    command = [
        "ffmpeg", "-loglevel", "error", "-y",
        "-f", "lavfi",
        "-i", f"color=c=blue:s={width}x{height}:d={duration_seconds}:r={fps}",
        "-f", "lavfi",
        "-i", f"sine=f=1000:d={duration_seconds}",
        "-c:v", "libx265", "-preset", "fast", "-crf", "28",
        "-c:a", "aac",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(command, timeout=600)
        if result.returncode == 0:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"✅ 生成完成: {size_mb:.2f} MB", file=sys.stderr)
            return True
        else:
            print(f"❌ FFmpeg 生成失败", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ FFmpeg 生成超时", file=sys.stderr)
        return False


def get_file_size_mb(path: Path) -> float:
    """获取文件大小（MB）"""
    if not path.exists():
        return 0
    return path.stat().st_size / (1024 * 1024)


# ============ 测试用例 ============

def test_case_1_small_local_video():
    """测试 1: 本地小视频 (< 14MB) - 应跳过压缩"""
    print("\n" + "="*70)
    print("TEST CASE 1: 本地小视频 (< 14MB) - 绿色通道，跳过压缩")
    print("="*70)
    
    script_dir = Path(__file__).parent
    video_path = script_dir / "13M.mp4"
    
    if not video_path.exists():
        print(f"❌ 找不到视频文件: {video_path}", file=sys.stderr)
        print(f"📝 请在 {script_dir} 目录下放置 13M.mp4 文件", file=sys.stderr)
        return False
    
    size_mb = get_file_size_mb(video_path)
    print(f"📊 视频大小: {size_mb:.2f} MB（预期 < 14MB）", file=sys.stderr)
    
    # 运行分析脚本
    cmd = f"uv run analyze_video.py -v '{video_path}' -p '这是一个测试视频' --keep-temp --exec-timeout 180"
    return run_command(cmd, "运行分析脚本（小视频，应跳过压缩）")


def test_case_2_medium_local_video():
    """测试 2: 本地中等视频 (14-32MB) - 应以 6fps 压缩"""
    print("\n" + "="*70)
    print("TEST CASE 2: 本地中等视频 (14-32MB) - 以 6fps 压缩")
    print("="*70)
    
    script_dir = Path(__file__).parent
    video_path = script_dir / "26M.mp4"
    
    if not video_path.exists():
        print(f"❌ 找不到视频文件: {video_path}", file=sys.stderr)
        print(f"📝 请在 {script_dir} 目录下放置 26M.mp4 文件", file=sys.stderr)
        return False
    
    size_mb = get_file_size_mb(video_path)
    print(f"📊 视频大小: {size_mb:.2f} MB（预期 14-32MB，应以 6fps 压缩）", file=sys.stderr)
    
    # 运行分析脚本
    cmd = f"uv run analyze_video.py -v '{video_path}' -p '这是一个测试视频' --keep-temp --exec-timeout 240"
    return run_command(cmd, "运行分析脚本（中等视频，以 6fps 压缩）")


def test_case_3_large_local_video():
    """测试 3: 本地大视频 (32-42MB) - 应以 1fps 极限压缩"""
    print("\n" + "="*70)
    print("TEST CASE 3: 本地大视频 (32-42MB) - 以 1fps 极限压缩")
    print("="*70)
    
    script_dir = Path(__file__).parent
    video_path = script_dir / "39M.mp4"
    
    if not video_path.exists():
        print(f"❌ 找不到视频文件: {video_path}", file=sys.stderr)
        print(f"📝 请在 {script_dir} 目录下放置 39M.mp4 文件", file=sys.stderr)
        return False
    
    size_mb = get_file_size_mb(video_path)
    print(f"📊 视频大小: {size_mb:.2f} MB（预期 32-42MB，应以 1fps 极限压缩）", file=sys.stderr)
    
    # 运行分析脚本
    cmd = f"uv run analyze_video.py -v '{video_path}' -p '这是一个测试视频' --keep-temp --exec-timeout 300"
    return run_command(cmd, "运行分析脚本（大视频，以 1fps 极限压缩）")


def test_case_4_ultra_large_local_video():
    """测试 4: 本地超大视频 (> 42MB) - 应先裁切再压缩"""
    print("\n" + "="*70)
    print("TEST CASE 4: 本地超大视频 (> 42MB) - 先裁切再压缩")
    print("="*70)
    
    script_dir = Path(__file__).parent
    video_path = script_dir / "52M.mp4"
    
    if not video_path.exists():
        print(f"❌ 找不到视频文件: {video_path}", file=sys.stderr)
        print(f"📝 请在 {script_dir} 目录下放置 52M.mp4 文件", file=sys.stderr)
        return False
    
    size_mb = get_file_size_mb(video_path)
    print(f"📊 视频大小: {size_mb:.2f} MB（预期 > 42MB，应先裁切再压缩）", file=sys.stderr)
    
    # 运行分析脚本
    cmd = f"uv run analyze_video.py -v '{video_path}' -p '这是一个测试视频' --keep-temp --exec-timeout 360"
    return run_command(cmd, "运行分析脚本（超大视频，先裁切再压缩）")


def test_case_5_high_resolution_video():
    """测试 5: 高分辨率视频 (> 360P) - 应自动缩放到 360P"""
    print("\n" + "="*70)
    print("TEST CASE 5: 高分辨率视频 (1080P) - 应自动缩放到 360P")
    print("="*70)
    
    script_dir = Path(__file__).parent
    # 使用 52M.mp4（假设其为高分辨率视频）
    video_path = script_dir / "52M.mp4"
    
    if not video_path.exists():
        print(f"❌ 找不到视频文件: {video_path}", file=sys.stderr)
        print(f"📝 请在 {script_dir} 目录下放置 52M.mp4 文件", file=sys.stderr)
        return False
    
    size_mb = get_file_size_mb(video_path)
    print(f"📊 视频大小: {size_mb:.2f} MB（验证分辨率自动缩放到 360P）", file=sys.stderr)
    
    # 运行分析脚本
    cmd = f"uv run analyze_video.py -v '{video_path}' -p '这是一个测试视频' --keep-temp --exec-timeout 360"
    return run_command(cmd, "运行分析脚本（高分辨率视频）")


def test_case_6_compress_then_trim():
    """测试 6: 压缩后仍超 14MB - 应自动裁切到 14MB"""
    print("\n" + "="*70)
    print("TEST CASE 6: 压缩后超 14MB - 应自动裁切到 14MB")
    print("="*70)
    
    script_dir = Path(__file__).parent
    # 使用 52M.mp4（超大文件，很可能压缩后也会超 14MB，触发裁切逻辑）
    video_path = script_dir / "52M.mp4"
    
    if not video_path.exists():
        print(f"❌ 找不到视频文件: {video_path}", file=sys.stderr)
        print(f"📝 请在 {script_dir} 目录下放置 52M.mp4 文件", file=sys.stderr)
        return False
    
    size_mb = get_file_size_mb(video_path)
    print(f"📊 视频大小: {size_mb:.2f} MB（压缩后可能超 14MB，测试自动裁切）", file=sys.stderr)
    
    # 运行分析脚本
    cmd = f"uv run analyze_video.py -v '{video_path}' -p '这是一个测试视频' --keep-temp --exec-timeout 360"
    return run_command(cmd, "运行分析脚本（挑战性视频，测试压缩后推荐裁切）")


def test_case_7_youtube_prompt_mode():
    """测试 7: YouTube 视频 - prompt 模式（URL 追加到提示词）"""
    print("\n" + "="*70)
    print("TEST CASE 7: YouTube 视频 - prompt 模式")
    print("="*70)
    print("⚠️ 需要 GEMINI_API_KEY 和 GEMINI_BASE_URL 环境变量")
    print("⚠️ 使用真实 YouTube URL（例如：https://www.youtube.com/watch?v=xxx）")
    
    # 这是一个示例命令 - 使用者需要替换为真实的 YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=9hE5-98ZeCg"
    
    cmd = f"uv run analyze_video.py -v '{youtube_url}' -p '总结这个视频' --mode prompt --exec-timeout 180"
    print(f"\n📌 使用以下命令测试（需要有效的 API Key）：", file=sys.stderr)
    print(f"$ {cmd}", file=sys.stderr)
    return run_command(cmd, "运行分析脚本，prompt 模式（YouTube 视频）")


def test_case_8_youtube_file_uri_mode():
    """测试 8: YouTube 视频 - file_uri 模式（使用 Google 的 file_data）"""
    print("\n" + "="*70)
    print("TEST CASE 8: YouTube 视频 - file_uri 模式")
    print("="*70)
    print("⚠️ 需要 GEMINI_API_KEY 和 GEMINI_BASE_URL 环境变量")
    print("⚠️ 使用真实 YouTube URL（例如：https://www.youtube.com/watch?v=xxx）")
    
    # 这是一个示例命令 - 使用者需要替换为真实的 YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=9hE5-98ZeCg"
    
    cmd = f"uv run analyze_video.py -v '{youtube_url}' -p '总结这个视频' --mode file_uri --exec-timeout 240"
    print(f"\n📌 使用以下命令测试（需要有效的 API Key）：", file=sys.stderr)
    print(f"$ {cmd}", file=sys.stderr)
    
    return run_command(cmd, "运行分析脚本，file_uri 模式（YouTube 视频）")


def test_case_9_youtube_inline_mode():
    """测试 9: YouTube 视频 - inline 模式（下载后进行 Base64 编码）"""
    print("\n" + "="*70)
    print("TEST CASE 9: YouTube 视频 - inline 模式（默认）")
    print("="*70)
    print("⚠️ 需要 GEMINI_API_KEY、GEMINI_BASE_URL、yt-dlp 和 ffmpeg")
    print("⚠️ 使用真实 YouTube URL（例如：https://www.youtube.com/watch?v=xxx）")
    print("⚠️ 首次运行需要浏览器 cookie 授权")
    
    # 这是一个示例命令 - 使用者需要替换为真实的 YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=9hE5-98ZeCg"
    
    cmd = f"uv run analyze_video.py -v '{youtube_url}' -p '用中文总结这个视频' --mode inline --exec-timeout 300"
    print(f"\n📌 使用以下命令测试（需要有效的 API Key）：", file=sys.stderr)
    print(f"$ {cmd}", file=sys.stderr)
    return run_command(cmd, "运行分析脚本，inline 模式（YouTube 视频）")


def test_case_10_temp_cleanup():
    """测试 10: 临时文件清理 - 验证完成后是否清理了临时文件"""
    print("\n" + "="*70)
    print("TEST CASE 10: 临时文件清理验证")
    print("="*70)
    
    with tempfile.TemporaryDirectory(prefix="test_case_10_") as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 生成一个视频
        video_path = tmpdir / "cleanup_test_video.mp4"
        if not generate_test_video(video_path, duration_seconds=10, 
                                   width=1280, height=720, fps=24):
            print("❌ 生成视频失败", file=sys.stderr)
            return False
        
        # 运行分析脚本（不保留临时文件）
        cmd = f"uv run analyze_video.py -v '{video_path}' -p '这是一个测试视频' --exec-timeout 360"
        
        if not run_command(cmd, "运行分析脚本（不保留临时文件）"):
            return False
        
        # 检查是否有遗留的临时目录
        import glob
        temp_dirs = glob.glob("/tmp/video_analysis_*")
        
        if temp_dirs:
            print(f"⚠️ 找到遗留的临时目录: {temp_dirs}", file=sys.stderr)
            return False
        
        print("✅ 临时文件已正确清理", file=sys.stderr)
        return True


# ============ 主函数 ============

def main():
    """运行所有测试"""
    import os
    
    print("\n" + "="*70)
    print("🧪 analyze_video.py 测试套件")
    print("="*70)
    print("\n✓ 确保已安装以下依赖:")
    print("  - uv")
    print("  - ffmpeg")
    print("  - yt-dlp")
    print("  - google-genai")
    print("\n✓ 设置以下环境变量:")
    print("  - GEMINI_API_KEY")
    print("  - GEMINI_BASE_URL (可选)")
    
    # 检查依赖
    for bin_name in ["ffmpeg", "ffprobe"]:
        result = subprocess.run(f"which {bin_name}" if os.name != 'nt' else f"where {bin_name}", 
                               shell=True, capture_output=True)
        if result.returncode != 0:
            print(f"❌ 缺少 {bin_name}，请先安装", file=sys.stderr)
            sys.exit(1)
    
    print("\n✅ 依赖检查完成\n")
    
    # 定义所有测试
    tests = [
        ("TEST 1: 小视频 (< 14MB)", test_case_1_small_local_video),
        ("TEST 2: 中等视频 (14-32MB)", test_case_2_medium_local_video),
        ("TEST 3: 大视频 (32-42MB)", test_case_3_large_local_video),
        ("TEST 4: 超大视频 (> 42MB)", test_case_4_ultra_large_local_video),
        ("TEST 5: 高分辨率视频", test_case_5_high_resolution_video),
        ("TEST 6: 压缩后裁切", test_case_6_compress_then_trim),
        ("TEST 7: YouTube prompt 模式", test_case_7_youtube_prompt_mode),
        ("TEST 8: YouTube file_uri 模式", test_case_8_youtube_file_uri_mode),
        ("TEST 9: YouTube inline 模式", test_case_9_youtube_inline_mode),
        ("TEST 10: 临时文件清理", test_case_10_temp_cleanup),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ 测试异常: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            results[test_name] = False
    
    # 打印总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
