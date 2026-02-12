import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_outdoor_news_summary import (
    get_outdoor_news_config,
    run_outdoor_news_summary_task,
    DEFAULT_DAYS_BACK
)
from newsletter_tools import NewsConfig


class TestRunOutdoorNewsSummary(unittest.TestCase):
    """测试 run_outdoor_news_summary.py 模块"""
    
    def test_default_days_back(self):
        """测试默认回溯天数"""
        self.assertEqual(DEFAULT_DAYS_BACK, 14)
    
    def test_get_outdoor_news_config(self):
        """测试获取户外运动新闻配置"""
        original_target_sites = os.environ.get('TARGET_SITES')
        original_rss_feeds = os.environ.get('RSS_FEEDS')
        original_openids = os.environ.get('FEISHU_COLLABORATOR_OPENIDS')
        
        try:
            os.environ['TARGET_SITES'] = 'https://example.com, https://test.com'
            os.environ['RSS_FEEDS'] = 'https://example.com=https://example.com/rss, https://test.com=https://test.com/rss'
            os.environ['FEISHU_COLLABORATOR_OPENIDS'] = 'openid1, openid2'
            
            config = get_outdoor_news_config()
            
            self.assertEqual(config.name, "户外运动")
            self.assertEqual(config.target_sites, ["https://example.com", "https://test.com"])
            self.assertEqual(config.rss_feeds, {
                "https://example.com": "https://example.com/rss",
                "https://test.com": "https://test.com/rss"
            })
            self.assertEqual(config.feishu_collaborator_openids, ["openid1", "openid2"])
            self.assertIn("户外运动新闻汇总", config.report_title_template)
            self.assertEqual(config.report_header, "# 户外运动新闻汇总\n")
            self.assertEqual(config.cache_prefix, "outdoor_")
            
        finally:
            if original_target_sites:
                os.environ['TARGET_SITES'] = original_target_sites
            else:
                del os.environ['TARGET_SITES']
            
            if original_rss_feeds:
                os.environ['RSS_FEEDS'] = original_rss_feeds
            else:
                del os.environ['RSS_FEEDS']
            
            if original_openids:
                os.environ['FEISHU_COLLABORATOR_OPENIDS'] = original_openids
            else:
                del os.environ['FEISHU_COLLABORATOR_OPENIDS']
    
    def test_get_outdoor_news_config_empty_env(self):
        """测试环境变量为空时的默认配置"""
        original_target_sites = os.environ.get('TARGET_SITES')
        original_rss_feeds = os.environ.get('RSS_FEEDS')
        original_openids = os.environ.get('FEISHU_COLLABORATOR_OPENIDS')
        
        try:
            if 'TARGET_SITES' in os.environ:
                del os.environ['TARGET_SITES']
            if 'RSS_FEEDS' in os.environ:
                del os.environ['RSS_FEEDS']
            if 'FEISHU_COLLABORATOR_OPENIDS' in os.environ:
                del os.environ['FEISHU_COLLABORATOR_OPENIDS']
            
            config = get_outdoor_news_config()
            
            self.assertEqual(config.name, "户外运动")
            self.assertEqual(config.target_sites, [])
            self.assertEqual(config.rss_feeds, {})
            self.assertEqual(config.feishu_collaborator_openids, [])
            self.assertIn("户外运动新闻汇总", config.report_title_template)
            self.assertEqual(config.report_header, "# 户外运动新闻汇总\n")
            self.assertEqual(config.cache_prefix, "outdoor_")
            
        finally:
            if original_target_sites:
                os.environ['TARGET_SITES'] = original_target_sites
            if original_rss_feeds:
                os.environ['RSS_FEEDS'] = original_rss_feeds
            if original_openids:
                os.environ['FEISHU_COLLABORATOR_OPENIDS'] = original_openids
    
    @patch('run_outdoor_news_summary.get_outdoor_news_config')
    @patch('run_outdoor_news_summary.run_newsletter_task')
    def test_run_outdoor_news_summary_task_with_days_back(self, mock_run_task, mock_get_config):
        """测试使用 days_back 参数运行任务"""
        mock_config = Mock(spec=NewsConfig)
        mock_config.name = "户外运动"
        mock_get_config.return_value = mock_config
        
        mock_doc_url = 'https://feishu.cn/docx/test_doc_id'
        mock_run_task.return_value = mock_doc_url
        
        result = run_outdoor_news_summary_task(chat_id="test_chat_id", days_back=7)
        
        self.assertEqual(result, mock_doc_url)
        mock_get_config.assert_called_once()
        mock_run_task.assert_called_once_with(mock_config, chat_id="test_chat_id", days_back=7)
    
    @patch('run_outdoor_news_summary.get_outdoor_news_config')
    @patch('run_outdoor_news_summary.run_newsletter_task')
    def test_run_outdoor_news_summary_task_with_date_range(self, mock_run_task, mock_get_config):
        """测试使用日期范围参数运行任务"""
        mock_config = Mock(spec=NewsConfig)
        mock_config.name = "户外运动"
        mock_get_config.return_value = mock_config
        
        mock_doc_url = 'https://feishu.cn/docx/test_doc_id'
        mock_run_task.return_value = mock_doc_url
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 14)
        
        result = run_outdoor_news_summary_task(
            chat_id="test_chat_id", 
            start_date=start_date, 
            end_date=end_date
        )
        
        self.assertEqual(result, mock_doc_url)
        mock_get_config.assert_called_once()
        mock_run_task.assert_called_once_with(
            mock_config, 
            chat_id="test_chat_id", 
            start_date=start_date, 
            end_date=end_date
        )
    
    @patch('run_outdoor_news_summary.get_outdoor_news_config')
    @patch('run_outdoor_news_summary.run_newsletter_task')
    def test_run_outdoor_news_summary_task_default(self, mock_run_task, mock_get_config):
        """测试使用默认参数运行任务"""
        mock_config = Mock(spec=NewsConfig)
        mock_config.name = "户外运动"
        mock_get_config.return_value = mock_config
        
        mock_doc_url = 'https://feishu.cn/docx/test_doc_id'
        mock_run_task.return_value = mock_doc_url
        
        result = run_outdoor_news_summary_task(chat_id="test_chat_id")
        
        self.assertEqual(result, mock_doc_url)
        mock_get_config.assert_called_once()
        mock_run_task.assert_called_once_with(
            mock_config, 
            chat_id="test_chat_id", 
            days_back=DEFAULT_DAYS_BACK
        )
    
    def test_run_outdoor_news_summary_task_parameter_conflict(self):
        """测试参数冲突时抛出异常"""
        with self.assertRaises(ValueError) as context:
            run_outdoor_news_summary_task(
                days_back=7,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 14)
            )
        
        self.assertIn("不能同时使用", str(context.exception))


if __name__ == "__main__":
    unittest.main()
