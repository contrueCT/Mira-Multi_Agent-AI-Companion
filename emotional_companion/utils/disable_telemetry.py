"""
遥测数据禁用模块
禁用各种库的遥测数据收集功能，包括PostHog等服务
"""

import os
import sys
import warnings
from unittest.mock import Mock, patch


def disable_all_telemetry():
    """禁用所有已知的遥测功能"""
    print("🛡️ 正在禁用遥测数据收集...")
    
    # 禁用PostHog遥测
    disable_posthog_telemetry()
    
    # 禁用AutoGen遥测
    disable_autogen_telemetry()
    
    # 禁用其他常见遥测
    disable_common_telemetry()
    
    # 禁用网络请求到遥测服务
    disable_telemetry_requests()
    
    print("✅ 遥测数据收集已禁用")


def disable_posthog_telemetry():
    """禁用PostHog遥测"""
    # 设置环境变量禁用PostHog
    os.environ['POSTHOG_DISABLED'] = 'true'
    os.environ['POSTHOG_DEBUG'] = 'false'
    os.environ['DO_NOT_TRACK'] = '1'
    
    # 尝试Mock PostHog客户端
    try:
        import posthog
        # 禁用PostHog
        posthog.disabled = True
        print("  ✓ PostHog遥测已禁用")
    except ImportError:
        # PostHog未安装，尝试预防性Mock
        sys.modules['posthog'] = Mock()
        print("  ✓ PostHog已预防性Mock")


def disable_autogen_telemetry():
    """禁用AutoGen相关遥测"""
    # AutoGen相关环境变量
    os.environ['AUTOGEN_TELEMETRY_OPT_OUT'] = '1'
    os.environ['AUTOGEN_DISABLE_TELEMETRY'] = 'true'
    os.environ['AUTOGEN_NO_ANALYTICS'] = '1'
    
    # 尝试禁用autogen遥测
    try:
        import autogen
        if hasattr(autogen, 'disable_telemetry'):
            autogen.disable_telemetry()
        print("  ✓ AutoGen遥测已禁用")
    except (ImportError, AttributeError):
        print("  ✓ AutoGen遥测预防性禁用")


def disable_common_telemetry():
    """禁用常见的遥测功能"""
    # 通用遥测禁用环境变量
    telemetry_vars = {
        'TELEMETRY_DISABLED': 'true',
        'DISABLE_TELEMETRY': '1',
        'NO_ANALYTICS': '1',
        'NO_TELEMETRY': '1',
        'ANALYTICS_DISABLED': 'true',
        'METRICS_DISABLED': 'true',
        'TRACKING_DISABLED': 'true',
        'DO_NOT_TRACK': '1',
        'DNT': '1',
        
        # Microsoft相关
        'DOTNET_CLI_TELEMETRY_OPTOUT': '1',
        'AZURE_CORE_COLLECT_TELEMETRY': 'false',
        
        # OpenAI相关
        'OPENAI_DISABLE_TELEMETRY': '1',
        
        # Hugging Face相关
        'HF_HUB_DISABLE_TELEMETRY': '1',
        'HUGGINGFACE_HUB_DISABLE_TELEMETRY': '1',
        
        # 其他AI库
        'LANGCHAIN_TELEMETRY_DISABLED': 'true',
        'ANTHROPIC_DISABLE_TELEMETRY': '1',
    }
    
    for var, value in telemetry_vars.items():
        os.environ[var] = value
    
    print(f"  ✓ 已设置 {len(telemetry_vars)} 个遥测禁用环境变量")


def disable_telemetry_requests():
    """通过Mock requests禁用到遥测服务的网络请求"""
    import requests
    import urllib3
    
    # 需要阻止的遥测域名
    blocked_domains = [
        'posthog.com',
        'us.i.posthog.com',
        'app.posthog.com',
        'eu.i.posthog.com',
        'analytics.google.com',
        'google-analytics.com',
        'mixpanel.com',
        'segment.com',
        'amplitude.com',
        'telemetry.microsoft.com',
        'dc.services.visualstudio.com',
        'api.segment.io',
        'track.customer.io',
        'analytics.openai.com',
        'telemetry.openai.com',
        'huggingface.co/api/telemetry',
        'api.anthropic.com/telemetry',
    ]
    
    # 保存原始的requests方法
    original_request = requests.request
    original_get = requests.get
    original_post = requests.post
    original_put = requests.put
    original_patch = requests.patch
    
    def blocked_request(method, url, *args, **kwargs):
        """检查请求URL是否包含遥测域名，如果是则阻止"""
        url_str = str(url)
        
        if any(domain in url_str for domain in blocked_domains):
            print(f"  🛡️ 已阻止遥测请求: {method.upper()} {url_str}")
            # 返回一个Mock响应而不是实际请求
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.text = ""
            mock_response.content = b""
            mock_response.headers = {}
            return mock_response
        
        # 对于非遥测请求，使用原始方法
        return original_request(method, url, *args, **kwargs)
    
    def blocked_get(url, *args, **kwargs):
        """阻止GET请求到遥测服务"""
        return blocked_request('GET', url, *args, **kwargs)
    
    def blocked_post(url, *args, **kwargs):
        """阻止POST请求到遥测服务"""
        return blocked_request('POST', url, *args, **kwargs)
    
    def blocked_put(url, *args, **kwargs):
        """阻止PUT请求到遥测服务"""
        return blocked_request('PUT', url, *args, **kwargs)
    
    def blocked_patch(url, *args, **kwargs):
        """阻止PATCH请求到遥测服务"""
        return blocked_request('PATCH', url, *args, **kwargs)
    
    # 应用补丁
    requests.request = blocked_request
    requests.get = blocked_get
    requests.post = blocked_post
    requests.put = blocked_put
    requests.patch = blocked_patch
    
    # 也阻止urllib3直接请求
    try:
        original_urlopen = urllib3.poolmanager.PoolManager.urlopen
        
        def blocked_urlopen(self, method, url, *args, **kwargs):
            url_str = str(url)
            if any(domain in url_str for domain in blocked_domains):
                print(f"  🛡️ 已阻止urllib3遥测请求: {method.upper()} {url_str}")
                # 创建一个假的响应
                from urllib3._collections import HTTPHeaderDict
                from urllib3.response import HTTPResponse
                mock_response = HTTPResponse(
                    body=b'{}',
                    headers=HTTPHeaderDict({'content-type': 'application/json'}),
                    status=200,
                    preload_content=False
                )
                return mock_response
            return original_urlopen(self, method, url, *args, **kwargs)
        
        urllib3.poolmanager.PoolManager.urlopen = blocked_urlopen
        print("  ✓ urllib3请求遥测阻止器已激活")
    except Exception as e:
        print(f"  ⚠️ 无法拦截urllib3请求: {e}")
    
    print("  ✓ 网络请求遥测阻止器已激活")


def disable_urllib3_warnings():
    """禁用urllib3的SSL警告"""
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.disable_warnings()
        print("  ✓ urllib3警告已禁用")
    except ImportError:
        pass


def suppress_ssl_warnings():
    """抑制SSL相关警告"""
    import ssl
    import warnings
    
    # 忽略SSL相关警告
    warnings.filterwarnings('ignore', message='.*SSL.*')
    warnings.filterwarnings('ignore', message='.*certificate.*')
    warnings.filterwarnings('ignore', message='.*urllib3.*')
    
    # 设置SSL上下文以避免某些错误
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    
    print("  ✓ SSL警告已抑制")


# 在模块导入时自动执行
if __name__ == "__main__":
    disable_all_telemetry()
    disable_urllib3_warnings()
    suppress_ssl_warnings()