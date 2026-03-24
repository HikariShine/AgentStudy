#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "yt-dlp>=2024.01.01",
#     "requests>=2.31.0",
# ]
# ///
"""
Enhanced video analyzer supporting both local and remote videos (YouTube, URL, etc.).
Supports multiple modes for YouTube: prompt-based, file_uri, and inline.
Auto-downloads and converts videos using yt-dlp and FFmpeg.

Usage:
    # Local video
    uv run analyze_video_enhanced.py -v "video.mp4" -p "Summarize the video."
    
    # YouTube video (default: inline mode)
    uv run analyze_video_enhanced.py -v "https://www.youtube.com/watch?v=xxx" -p "Summarize the video." --mode inline
    
    # YouTube video with file_uri mode
    uv run analyze_video_enhanced.py -v "https://www.youtube.com/watch?v=xxx" -p "Summarize the video." --mode file_uri
    
    # YouTube video with prompt mode (URL appended to prompt)
    uv run analyze_video_enhanced.py -v "https://www.youtube.com/watch?v=xxx" -p "Summarize the video." --mode prompt
    
    # With proxy support
    uv run analyze_video_enhanced.py -v "https://youtube.com/watch?v=xxx" -p "Summarize the video." --proxy "http://proxy.example.com:8080"
"""

import argparse
import os
import sys
import time
import base64
import subprocess
import shutil
import tempfile
import re
import json
import requests
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

# 严格的硬性限制 (Bytes)
MAX_PRE_B64_BYTES = 14 * 1024 * 1024  # 压缩后文件不能超过 14MB
MAX_POST_B64_BYTES = 20 * 1024 * 1024 # Base64 字符串不能超过 20MB

# 目标分辨率
TARGET_RESOLUTION = 360


def get_api_key(provided_key: str | None) -> str | None:
    """获取 API Key"""
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY")


def is_youtube_url(url: str) -> bool:
    """判断是否是 YouTube 链接"""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com',
        r'(?:https?://)?(?:www\.)?youtu\.be',
    ]
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)


def is_url(path: str) -> bool:
    """判断是否是 URL"""
    try:
        result = urlparse(path)
        return result.scheme in ('http', 'https')
    except:
        return False


def download_video(url: str, output_dir: Path, proxy: Optional[str] = None, 
                  cookies_browser: str = "chrome", timeout: int = 300) -> Path:
    """
    使用 yt-dlp 下载视频到 360p h.265 格式
    
    Args:
        url: 视频 URL
        output_dir: 输出目录
        proxy: 代理地址（可选）
        cookies_browser: 获取 cookie 的浏览器
        timeout: 超时时间（秒）
    
    Returns:
        下载后的视频路径
    """
    print(f"📥 正在使用 yt-dlp 下载视频...", file=sys.stderr)
    
    # 先获取视频信息，检查时长
    info_command = [
        "yt-dlp",
        "--dump-json",
    ]
    
    if is_youtube_url(url):
        info_command.extend(["--cookies-from-browser", cookies_browser])
    
    if proxy:
        info_command.extend(["--proxy", proxy])
    
    info_command.append(url)
    
    try:
        print(f"🔍 正在获取视频信息...", file=sys.stderr)
        result = subprocess.run(info_command, timeout=60, capture_output=True, text=True)
        if result.returncode == 0:
            info = json.loads(result.stdout)
            duration = info.get("duration", 0)
            
            if duration and duration > 7200:
                hours = duration / 7200
                print(f"❌ Error: 视频时长 {hours:.1f} 小时，超过限制，不支持下载。", file=sys.stderr)
                raise RuntimeError(f"视频时长超过{hours:.1f}小时，不支持分析")
            
            print(f"✅ 视频时长检查通过: {duration:.0f} 秒（{duration/60:.1f} 分钟）", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"⚠️ 无法解析视频信息，继续下载...", file=sys.stderr)
    except RuntimeError:
        raise
    except Exception as e:
        print(f"⚠️ 获取视频信息失败: {e}，继续下载...", file=sys.stderr)
    
    # 构建 yt-dlp 下载命令
    command = [
        "yt-dlp",
        "-P", str(output_dir),
        "-o", "%(title)s.%(ext)s",
        # 360p h.265 (HEVC) 格式
        "-f", "30011+30280/bestvideo[height<=360][vcodec^=hevc]+bestaudio/bestvideo[height<=360]+bestaudio/best[height<=360]",
        # 如果是 YouTube，使用 cookie 避免 403 错误
    ]
    
    if is_youtube_url(url):
        command.extend(["--cookies-from-browser", cookies_browser])
    
    # 如果指定了代理
    if proxy:
        command.extend(["--proxy", proxy])
    
    command.append(url)
    
    try:
        print(f"🚀 执行 yt-dlp 命令: {' '.join(command)}", file=sys.stderr)
        result = subprocess.run(command, timeout=timeout, capture_output=True, text=True)
        return_code = result.returncode
        
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"yt-dlp 下载超时 (超过 {timeout} 秒)")
    
    # 查找下载的视频文件
    video_files = list(output_dir.glob("*"))
    video_files = [f for f in video_files if f.suffix.lower() in ['.mp4', '.mkv', '.webm', '.mov']]
    
    # 成功判定逻辑：
    # 1. 返回码为 0 表示成功，或
    # 2. 返回码不为 0，但找到了视频文件且大小 > 1KB（说明下载确实完成了）
    success = False
    error_msg = ""
    
    if return_code == 0:
        success = True
    elif video_files:
        # 检查下载的文件大小
        valid_files = [f for f in video_files if f.stat().st_size > 1024]  # > 1KB
        if valid_files:
            success = True
            print(f"⚠️ yt-dlp 返回码非零，但检测到有效的视频文件，视为下载成功", file=sys.stderr)
        else:
            error_msg = "找到视频文件但大小过小（< 1KB）"
    else:
        error_msg = "未找到视频文件"
    
    if not success:
        if return_code != 0:
            print(f"yt-dlp stderr: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"yt-dlp 下载失败: {error_msg}")
    
    # 返回最新的有效文件
    valid_video_files = [f for f in video_files if f.stat().st_size > 1024]
    video_path = max(valid_video_files, key=lambda f: f.stat().st_mtime)
    print(f"✅ 下载完成: {video_path.name} ({video_path.stat().st_size / (1024*1024):.2f} MB)", file=sys.stderr)
    
    return video_path


def get_video_resolution(video_path: Path) -> Tuple[int, int]:
    """
    获取视频分辨率
    
    Returns:
        (width, height) 元组
    """
    command = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        str(video_path)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            width, height = map(int, result.stdout.strip().split(','))
            return width, height
    except Exception as e:
        print(f"⚠️ 获取视频分辨率失败: {e}", file=sys.stderr)
    
    return 0, 0


def downscale_video(input_path: Path, output_path: Path, target_height: int = 360, 
                   timeout: int = 120) -> None:
    """
    使用 FFmpeg 将视频缩放到指定分辨率
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        target_height: 目标高度
        timeout: 超时时间（秒）
    """
    print(f"🎬 正在使用 FFmpeg 缩放视频到 {target_height}P...", file=sys.stderr)
    
    command = [
        "ffmpeg", "-loglevel", "error", "-stats", "-y",
        "-i", str(input_path),
        "-vf", f"scale=-2:'min({target_height},ih)'",  # 保持宽高比
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "64k",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(command, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError("FFmpeg 缩放失败")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"FFmpeg 缩放超时 (超过 {timeout} 秒)")
    
    print(f"✅ 缩放完成: {output_path.name} ({output_path.stat().st_size / (1024*1024):.2f} MB)", file=sys.stderr)


def compress_video(input_path: Path, output_path: Path, fps: int, timeout: int) -> None:
    """
    使用 FFmpeg 压缩视频，带超时控制
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        fps: 目标帧率
        timeout: 超时时间（秒）
    """
    print(f"🎬 正在使用 FFmpeg 极限压缩 (目标: {fps} fps, 超时限制: {timeout}s)...", file=sys.stderr)
    
    command = [
        "ffmpeg", "-loglevel", "error", "-stats", "-y",
        "-i", str(input_path),
        "-vf", "scale=-2:'min(360,ih)'",
        "-r", str(fps),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "35", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "32k",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(command, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError("FFmpeg 压缩失败")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"FFmpeg 压缩超时 (超过 {timeout} 秒)")


def get_video_duration(video_path: Path) -> float:
    """
    获取视频时长（秒）
    """
    command = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1:noprint_wrappers=1",
        str(video_path)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception as e:
        print(f"⚠️ 获取视频时长失败: {e}", file=sys.stderr)
    
    return 0


def trim_video_to_size(input_path: Path, output_path: Path, target_size_mb: int = 42,
                      fps: int = 1, timeout: int = 120) -> None:
    """
    快速截断视频到指定大小（使用 stream copy，不转码）
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        target_size_mb: 目标大小（MB）
        fps: 帧率（此参数用于 trim_video_to_target_bitrate，此函数中未使用）
        timeout: 超时时间（秒）
    """
    duration = get_video_duration(input_path)
    
    if duration <= 0:
        raise RuntimeError("无法获取视频时长，无法进行截断")
    
    # 粗略估计：根据目标大小计算保留时长
    # 从原文件大小推断：如果整个视频是 target_size_mb MB，则正好保留所有时长
    # 使用 stream copy 方式，文件大小约等于原文件的按时长比例缩放
    target_size_bytes = target_size_mb * 1024 * 1024
    original_size_bytes = input_path.stat().st_size
    
    # 直接根据大小比例计算时长
    size_ratio = target_size_bytes / original_size_bytes if original_size_bytes > 0 else 0.8
    target_duration = max(5, duration * min(size_ratio, 0.95))  # 保留 95% 以内
    
    print(f"✂️ 正在快速截断视频到 ~{target_size_mb}MB (原时长: {duration:.1f}s, 新时长: {target_duration:.1f}s, 使用 stream copy)...", file=sys.stderr)
    
    # 使用 stream copy 方式，无需转码，速度快得多
    command = [
        "ffmpeg", "-loglevel", "error", "-stats", "-y",
        "-i", str(input_path),
        "-t", str(target_duration),
        "-c", "copy",  # 流复制，不转码
        str(output_path)
    ]
    
    try:
        result = subprocess.run(command, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError("FFmpeg 截断失败")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"FFmpeg 截断超时 (超过 {timeout} 秒)")


def trim_video_to_target_bitrate(input_path: Path, output_path: Path, target_size_mb: int = 14,
                                fps: int = 1, timeout: int = 120) -> None:
    """
    快速裁切视频到目标大小（使用 stream copy，无需转码）
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径
        target_size_mb: 目标大小（MB）
        fps: 帧率（此参数保留但未使用，为兼容性）
        timeout: 超时时间（秒）
    """
    duration = get_video_duration(input_path)
    
    if duration <= 0:
        raise RuntimeError("无法获取视频时长，无法进行裁切")
    
    # 根据目标大小和时长估计保留的新时长
    # 假设每秒产生的数据量相对固定，按比例缩放
    target_size_bytes = target_size_mb * 1024 * 1024
    estimated_size = input_path.stat().st_size
    
    # 根据原始文件大小和时长估计每秒字节数
    bytes_per_second = estimated_size / duration if duration > 0 else 0
    
    if bytes_per_second > 0:
        new_duration = min(duration, target_size_bytes / bytes_per_second * 0.9)  # 留 10% 的裕度
    else:
        new_duration = duration * 0.5
    
    new_duration = max(5, new_duration)  # 至少保留 5 秒
    
    print(f"✂️ 正在快速裁切视频到 ~{target_size_mb}MB (原时长: {duration:.1f}s, 新时长: {new_duration:.1f}s, 使用 stream copy)...", file=sys.stderr)
    
    # 使用 stream copy 方式，无需转码，速度快得多
    command = [
        "ffmpeg", "-loglevel", "error", "-stats", "-y",
        "-i", str(input_path),
        "-t", str(new_duration),
        "-c", "copy",  # 流复制，不转码
        str(output_path)
    ]
    
    try:
        result = subprocess.run(command, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError("FFmpeg 裁切失败")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"FFmpeg 裁切超时 (超过 {timeout} 秒)")


def process_local_video(video_path: Path, work_dir: Path, exec_timeout: int) -> Tuple[Path, bool]:
    """
    处理本地视频，应用压缩策略
    
    Args:
        video_path: 原始视频路径
        work_dir: 临时工作目录
        exec_timeout: 执行超时时间
    
    Returns:
        (处理后的视频路径, 是否是新创建的临时文件)
    """
    input_size_mb = video_path.stat().st_size / (1024 * 1024)
    print(f"📊 原始视频体积: {input_size_mb:.2f} MB", file=sys.stderr)
    
    # 1. 检查分辨率，如果大于 360P 则先缩放
    width, height = get_video_resolution(video_path)
    downscaled_video = None
    
    if height > TARGET_RESOLUTION:
        print(f"⚠️ 视频分辨率 {width}x{height} > {TARGET_RESOLUTION}P，需要先缩放", file=sys.stderr)
        downscaled_video = work_dir / f"downscaled_{video_path.name}"
        downscale_timeout = int(max(10, exec_timeout - 120))
        downscale_video(video_path, downscaled_video, TARGET_RESOLUTION, timeout=downscale_timeout)
        
        # 使用缩放后的视频作为后续处理的源
        video_to_process = downscaled_video
        source_size_mb = downscaled_video.stat().st_size / (1024 * 1024)
    else:
        video_to_process = video_path
        source_size_mb = input_size_mb
    
    # 2. 根据文件大小决定是否压缩
    skip_compression = False
    target_fps = 6
    
    if source_size_mb < 14:
        print("⚡ 体积 < 14MB，触发绿色通道，直接跳过 FFmpeg 压缩！", file=sys.stderr)
        skip_compression = True
    elif source_size_mb <= 32:
        target_fps = 6
        print("✅ 体积 14~32MB，采用 6 fps 保留较好流畅度。", file=sys.stderr)
    elif source_size_mb <= 42:
        target_fps = 1
        print("⚠️ 体积 32~42MB，触发极限求生模式，采用 1 fps 确保压缩达标。", file=sys.stderr)
    else:
        # 需要先截断
        print(f"🔪 体积 > 42MB ({source_size_mb:.2f}MB)，需要先截断再压缩...", file=sys.stderr)
        trimmed_video = work_dir / f"trimmed_{video_to_process.name}"
        trim_timeout = int(max(20, exec_timeout - 120))
        trim_video_to_size(video_to_process, trimmed_video, target_size_mb=42, fps=1, timeout=trim_timeout)
        
        # 删除原始缩放文件（如果之前缩放过）
        if downscaled_video and downscaled_video.exists():
            downscaled_video.unlink()
        
        video_to_process = trimmed_video
        source_size_mb = trimmed_video.stat().st_size / (1024 * 1024)
        target_fps = 1
    
    # 3. 执行压缩（如果需要）
    if skip_compression:
        final_video = video_to_process
        is_temp = False  # 如果是原始视频或缩放视频，标记为非临时
    else:
        final_video = work_dir / f"compressed_{video_to_process.name}"
        ffmpeg_timeout = int(max(10, exec_timeout - 120))
        compress_video(video_to_process, final_video, target_fps, timeout=ffmpeg_timeout)
        
        # 检查压缩后大小
        compressed_size = final_video.stat().st_size
        print(f"📦 压缩后体积: {compressed_size / (1024*1024):.2f} MB", file=sys.stderr)
        
        # 4. 如果压缩后仍然超过 14MB，进行精确裁切
        if compressed_size > MAX_PRE_B64_BYTES:
            print(f"⚠️ 压缩后仍超过 14MB ({compressed_size/(1024*1024):.2f}MB)，进行精确裁切...", file=sys.stderr)
            trimmed_video = work_dir / f"trimmed_{final_video.name}"
            trim_timeout = int(max(20, exec_timeout - 120))
            trim_video_to_target_bitrate(final_video, trimmed_video, target_size_mb=14, fps=target_fps, timeout=trim_timeout)
            
            # 验证裁切后大小
            trimmed_size = trimmed_video.stat().st_size
            print(f"✂️ 裁切后体积: {trimmed_size / (1024*1024):.2f} MB", file=sys.stderr)
            
            if trimmed_size > MAX_PRE_B64_BYTES:
                print(f"❌ Error: 即使裁切后仍然超过 14MB (当前 {trimmed_size/(1024*1024):.2f}MB)。", file=sys.stderr)
                raise RuntimeError("视频经过压缩和裁切后仍然过大，无法处理")
            
            # 删除压缩版本，使用裁切版本
            final_video.unlink()
            final_video = trimmed_video
        
        # 删除中间文件
        if downscaled_video and downscaled_video.exists():
            downscaled_video.unlink()
        if video_to_process != video_path and video_to_process.exists():
            video_to_process.unlink()
        
        is_temp = True
    
    return final_video, is_temp


def call_gemini_inline(client, model: str, prompt: str, video_path: Path) -> str:
    """
    使用 inline 模式调用 Gemini（Base64 编码）
    """
    print("🔄 正在转为 Base64...", file=sys.stderr)
    
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    b64_size = len(video_b64.encode("utf-8"))
    print(f"🔤 Base64 载荷体积: {b64_size / (1024*1024):.2f} MB", file=sys.stderr)
    
    if b64_size > MAX_POST_B64_BYTES:
        raise RuntimeError(f"Base64 编码后超过了 Gemini 20MB 的 Payload 上限。")
    
    from google.genai import types
    
    print(f"🚀 正在发送至 Gemini 进行解析 (inline 模式)...", file=sys.stderr)
    
    response = client.models.generate_content(
        model=model,
        contents=[
            prompt,
            types.Part(
                inline_data=types.Blob(
                    mime_type="video/mp4",
                    data=video_b64
                )
            )
        ]
    )
    
    return response.text if response.text else "⚠️ 模型返回了空文本。"


def call_gemini_file_uri(client, model: str, prompt: str, file_uri: str, remaining_api_time: int,
                         base_url: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """
    使用 file_uri 模式调用 Gemini（仅限 YouTube）
    """
    
    print(f"🚀 正在发送至 Gemini 进行解析 (file_uri 模式)...", file=sys.stderr)
    
    
    # 用 HTTP 请求绕过 SDK 验证，等待new-api修复bug https://github.com/QuantumNous/new-api/issues/3385
    url = f"{base_url}/v1beta/models/{model}:generateContent"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "fileData": {"fileUri": file_uri},
                        "file_data": {"file_uri": file_uri}
                    }
                ]
            }
        ]
    }
    
    max_retries = 3
    retry_interval = 30
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 尝试第 {attempt}/{max_retries} 次...", file=sys.stderr)
            response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {api_key}"}, timeout=remaining_api_time)
            response.raise_for_status()
            result = response.json()
            
            # 提取返回的文本
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        print(f"✅ 第 {attempt} 次尝试成功", file=sys.stderr)
                        return parts[0]["text"]
            
            print(f"✅ 第 {attempt} 次尝试成功", file=sys.stderr)
            return "⚠️ 模型返回了空文本。"
        except Exception as e:
            if attempt < max_retries:
                print(f"⚠️ 第 {attempt} 次尝试失败: {e}，{retry_interval}秒后重试...", file=sys.stderr)
                time.sleep(retry_interval)
            else:
                print(f"❌ 第 {attempt} 次尝试失败: {e}，所有重试已耗尽", file=sys.stderr)
                raise RuntimeError("调用 Gemini 失败")


def main():
    parser = argparse.ArgumentParser(description="Enhanced Video Analyzer with URL support")
    parser.add_argument("--video", "-v", required=True, 
                       help="Path to local video file or video URL (YouTube, etc.)")
    parser.add_argument("--prompt", "-p", default="Describe the video.", 
                       help="Prompt for the model")
    parser.add_argument("--model", "-m", default="gemini-3-flash-preview", 
                       help="Model to use")
    parser.add_argument("--api-key", help="Gemini API key", 
                       default=os.environ.get("GEMINI_API_KEY"))
    parser.add_argument("--base-url", help="Proxy Base URL", 
                       default=os.environ.get("GEMINI_BASE_URL"))
    parser.add_argument("--mode", choices=["url", "inline"], default="prompt",
                       help="Mode for YouTube videos: uri (Google URI), or inline (Base64)")
    parser.add_argument("--proxy", help="HTTP proxy for video download (e.g., http://proxy.example.com:8080)")
    parser.add_argument("--cookies-browser", default="chrome",
                       help="Browser to extract cookies from for YouTube (chrome, firefox, safari, etc.)")
    parser.add_argument("--exec-timeout", type=int, default=300, 
                       help="Total execution timeout in seconds")
    parser.add_argument("--no-keep-temp", action="store_false", dest="keep_temp",
                       help="Delete temporary files after analysis (default: keep)")

    args = parser.parse_args()

    start_time = time.time()

    # 检查 API Key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("❌ Error: 缺少 API Key。请设置 GEMINI_API_KEY 环境变量。", file=sys.stderr)
        sys.exit(1)

    # 创建临时工作目录
    # 如果输入的是文件，且这个文件来自于符合下面格式的临时目录，则work_dir直接使用这个文件所在的目录，避免不必要的复制和空间占用
    work_dir = None
    if not is_url(args.video):
        input_path = Path(args.video)
        if input_path.exists() and input_path.is_file():
            parent_dir = input_path.parent
            # 这个判断要求严格满足在临时文件目录，这里是判断了文件夹名，修复一下
            if parent_dir.parent.resolve() == Path(tempfile.gettempdir()).resolve() and re.match(r"video_analysis_\w+", parent_dir.name):
                work_dir = parent_dir
                print(f"📂 输入文件位于临时目录 {work_dir}，将直接使用该目录作为工作目录。", file=sys.stderr)
        else:
            print(f"❌ Error: 找不到视频文件 {input_path}", file=sys.stderr)
            sys.exit(1)
    if work_dir is None:
        work_dir = Path(tempfile.mkdtemp(prefix="video_analysis_"))
        print(f"📂 临时工作目录: {work_dir}", file=sys.stderr)

    video_to_analyze = None
    is_url_input = is_url(args.video)
    is_youtube = is_youtube_url(args.video) if is_url_input else False

    try:
        # ============ 处理输入 ============
        video_path = None
        if is_url_input:
            print(f"🔗 检测到 URL 输入: {args.video}", file=sys.stderr)
            
            if is_youtube and args.mode == "url":
                # 如果是 url 模式，直接使用 URL
                print(f"📌 这是 YouTube 链接, 使用 {args.mode} 模式，无需下载视频", file=sys.stderr)
            else:
                print(f"🔗 使用 inline 模式下载", file=sys.stderr)
                video_path = download_video(args.video, work_dir, proxy=args.proxy,
                                           timeout=int(max(30, args.exec_timeout - 60)))
        else:
            # 本地视频
            video_path = Path(args.video)
        
        # 只在需要时检查视频文件存在性
        if video_path:
            if not video_path.exists():
                print(f"❌ Error: 找不到视频文件 {video_path}", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"📁 检测到视频: {video_path}", file=sys.stderr)
                # 处理视频（下载或本地）
                video_to_analyze, is_temp = process_local_video(video_path, work_dir, args.exec_timeout)

        # ============ 调用 Gemini ============
        elapsed = time.time() - start_time
        remaining_api_time = int(max(60, args.exec_timeout - elapsed))

        from google import genai

        client_kwargs = {"api_key": api_key}
        if args.base_url:
            client_kwargs["http_options"] = {"base_url": args.base_url, "timeout": remaining_api_time * 1000}
            print(f"🌐 目标代理接口: {args.base_url}", file=sys.stderr)
        else:
            client_kwargs["http_options"] = {"timeout": remaining_api_time * 1000}
            print("🌐 直连 Google 官方接口。", file=sys.stderr)

        client = genai.Client(**client_kwargs)
        
        # ============ 保存最终分析文件 ============
        if video_to_analyze:
            # 将最终文件重命名为 final_原文件名 格式
            original_name = video_path.name
            final_filename = f"final_{original_name}"
            final_video_path = work_dir / final_filename
            
            # 如果 video_to_analyze 不是原始视频或者下载下来的视频，直接重命名；否则复制一份到 final_ 前缀的文件
            # 这里的video_path有两个可能：1. 原始输入的本地文件。2. yt-dlp下载下来的文件。
            # video_to_analyze 是经过处理后的文件，可能是原始视频、缩放后的视频、压缩后的视频或裁切后的视频。
            # 如果不是原始视频，直接重命名为final_前缀的文件
            # 对于是原始视频的情况，我们要特殊处理：
            # 如果原视频不在临时目录，则直接复制一份到工作目录
            # 如果在临时目录，是下载下来的文件，且不是final_开头，则复制一份，文件名添加 final_前缀。
            # 如果是以final_开头的文件且文件在临时目录，表示已经是最终分析文件了，无需复制或重命名，是再次分析的时候指定的文件
            if video_to_analyze != video_path:
                video_to_analyze.rename(final_video_path)
                video_to_analyze = final_video_path  # 更新 video_to_analyze 指向 final_ 文件
            elif video_to_analyze.parent != work_dir or not video_to_analyze.name.startswith("final_"):
                shutil.copy2(video_to_analyze, final_video_path)
                video_to_analyze = final_video_path  # 更新 video_to_analyze 指向 final_ 文件
            
            print(f"\n💾 最终分析文件已保存: {video_to_analyze}", file=sys.stderr)

        # 根据模式调用
        if is_youtube and args.mode == "url":
            response_text = call_gemini_file_uri(client, args.model, args.prompt, args.video, remaining_api_time, 
                                               base_url=args.base_url, api_key=api_key)
        elif video_to_analyze:
            # inline 模式（已下载并处理）
            response_text = call_gemini_inline(client, args.model, args.prompt, video_to_analyze)
        else:
            raise RuntimeError("无法确定调用模式，缺少有效的视频文件或 URL 输入")

        if response_text:
            print("\n" + "="*50, file=sys.stderr)
            print(response_text)
        else:
            print("⚠️ 模型返回空文本。", file=sys.stderr)

    except Exception as e:
        import traceback
        print(f"\n❌ 执行过程中发生错误: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    finally:
        # ============ 清理临时文件 ============
        if not args.keep_temp:
            if work_dir.exists():
                shutil.rmtree(work_dir)
                print(f"🧹 已删除临时目录: {work_dir}", file=sys.stderr)
        else:
            print(f"📂 临时目录已保留（包含 final_ 前缀的分析文件）: {work_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()

