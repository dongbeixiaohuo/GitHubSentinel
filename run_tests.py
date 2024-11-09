import unittest
import sys
import os
from loguru import logger
import coverage

def setup_test_logger():
    """配置测试专用的日志记录器"""
    logger.remove()  # 移除所有默认处理程序
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    logger.add(
        "logs/tests.log",
        rotation="1 MB",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

def run_all_tests():
    """运行所有测试用例"""
    # 设置测试环境
    setup_test_logger()
    
    # 确保在正确的目录中运行测试
    project_root = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(project_root, 'tests')
    
    # 将项目根目录添加到 Python 路径
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    
    # 发现并加载测试
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 添加覆盖率阈值检查
    if result.wasSuccessful():
        coverage_threshold = 80
        coverage_score = coverage.report()
        if coverage_score < coverage_threshold:
            print(f"Warning: Coverage {coverage_score}% is below threshold {coverage_threshold}%")
            return 1
    
    # 返回测试结果
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests()) 