import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Set
import re


class GitHubTrendingBot:
    def __init__(self):
        self.github_token = os.getenv("GIT_TOKEN", "")
        self.feishu_webhook = os.getenv("FEISHU_WEBHOOK", "")
        self.history_file = ".pushed_history.json"
        self.history_days = 90  # 跨日去重天数
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-AI-Trending-Bot",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    def load_pushed_history(self) -> Set[str]:
        """加载已推送过的仓库历史（90天内）"""
        if not os.path.exists(self.history_file):
            return set()

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

            # 过滤掉超过90天的记录
            cutoff_date = (datetime.now() - timedelta(days=self.history_days)).strftime("%Y-%m-%d")
            valid_history = {
                repo_id for repo_id, date in history.items()
                if date >= cutoff_date
            }

            # 保存过滤后的历史
            filtered_history = {
                repo_id: date for repo_id, date in history.items()
                if date >= cutoff_date
            }
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(filtered_history, f, ensure_ascii=False, indent=2)

            return valid_history
        except Exception as e:
            print(f"⚠️ 加载历史记录失败: {e}")
            return set()

    def save_pushed_history(self, repos: List[Dict]):
        """保存本次推送的仓库到历史记录"""
        history = {}
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                pass

        today = datetime.now().strftime("%Y-%m-%d")
        for repo in repos:
            repo_id = repo.get("full_name")
            if repo_id:
                history[repo_id] = today

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def fetch_trending_repos(self, per_page: int = 10) -> List[Dict]:
        """获取最近活跃的AI项目，按star增速排序，并过滤已推送过的"""
        # 搜索最近90天内更新过的AI项目
        ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # 加载已推送历史（90天内去重）
        pushed_history = self.load_pushed_history()
        print(f"📚 已推送历史: {len(pushed_history)} 个仓库")

        # 扩展关键词列表
        queries = [
            "AI", "LLM", "machine learning", "deep learning",
            "MCP", "RAG", "agent", "GPT", "transformer", "neural network"
        ]

        all_repos = []

        for query in queries:
            url = f"https://api.github.com/search/repositories"
            params = {
                "q": f"{query} pushed:>{ninety_days_ago}",
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
            }

            try:
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    all_repos.extend(data.get("items", []))
            except Exception as e:
                print(f"Error fetching {query}: {e}")
                continue

        # 去重（单日内）并过滤已推送过的
        seen = set()
        unique_repos = []
        skipped_count = 0
        for repo in all_repos:
            repo_id = repo.get("full_name")
            if repo_id and repo_id not in seen:
                seen.add(repo_id)
                # 检查是否已在90天内推送过
                if repo_id in pushed_history:
                    skipped_count += 1
                    continue
                unique_repos.append(repo)

        print(f"🔄 跳过已推送: {skipped_count} 个仓库")

        # 计算star增速并排序
        def calc_velocity(repo):
            stars = repo.get("stargazers_count", 0)
            created_at = repo.get("created_at", "")
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    days_since_created = max(1, (datetime.now(created_date.tzinfo) - created_date).days)
                    return stars / days_since_created
                except:
                    pass
            return stars  # 如果无法计算，按stars总数

        unique_repos.sort(key=calc_velocity, reverse=True)
        return unique_repos[:5]

    def fetch_trending_from_web(self) -> List[Dict]:
        """从网页抓取 GitHub Trending（备用方案）"""
        try:
            # 使用 trending 页面
            url = "https://github.com/trending/python?since=daily"
            response = requests.get(
                url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30
            )

            if response.status_code == 200:
                # 简单的正则提取
                pattern = r'href="/([^/]+/[^/]+)"'
                repos = re.findall(pattern, response.text)

                # 获取前5个仓库的详细信息
                result = []
                for repo_name in list(dict.fromkeys(repos))[:5]:  # 去重
                    repo_info = self.fetch_repo_details(repo_name)
                    if repo_info:
                        result.append(repo_info)
                return result
        except Exception as e:
            print(f"Error fetching trending page: {e}")

        return []

    def fetch_repo_details(self, repo_name: str) -> Dict:
        """获取单个仓库的详细信息"""
        url = f"https://api.github.com/repos/{repo_name}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching {repo_name}: {e}")
        return None

    def calculate_velocity(self, repo: Dict) -> float:
        """计算仓库的star增速（每天获得的stars数）"""
        stars = repo.get("stargazers_count", 0)
        created_at = repo.get("created_at", "")
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                days_since_created = max(1, (datetime.now(created_date.tzinfo) - created_date).days)
                return round(stars / days_since_created, 1)
            except:
                pass
        return stars

    def generate_report(self, repos: List[Dict]) -> str:
        """生成 Markdown 格式的报告"""
        today = datetime.now().strftime("%Y年%m月%d日")

        report = f"# 🔥 GitHub AI 热门项目 TOP 5\n\n"
        report += f"📅 **{today}** | 🤖 自动推送\n\n"
        report += "---\n\n"

        for i, repo in enumerate(repos, 1):
            name = repo.get("full_name", "Unknown")
            stars = repo.get("stargazers_count", 0)
            velocity = self.calculate_velocity(repo)
            desc = repo.get("description", "暂无描述") or "暂无描述"
            lang = repo.get("language", "Unknown") or "Unknown"
            url = repo.get("html_url", "")
            created = repo.get("created_at", "")[:10] if repo.get("created_at") else ""

            report += f"## {i}. {name}\n\n"
            report += f"⭐ **{stars:,}** stars | 📈 **{velocity}** stars/天 | 📝 {lang} | 📅 {created}\n\n"
            report += f"💡 {desc}\n\n"
            report += f"🔗 [查看项目]({url})\n\n"
            report += "---\n\n"

        # 添加趋势分析
        report += "## 📊 今日趋势\n\n"
        report += f"*共追踪 {len(repos)} 个热门 AI 项目*\n\n"
        report += "**关键词**：AI、LLM、Machine Learning、Deep Learning、MCP、RAG、Agent、GPT、Transformer\n\n"

        return report

    def send_to_feishu(self, report: str):
        """发送到飞书机器人"""
        if not self.feishu_webhook:
            print("Error: FEISHU_WEBHOOK not configured")
            return False

        # 构建飞书卡片消息
        today = datetime.now().strftime("%Y-%m-%d")

        card_data = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🔥 GitHub AI 热门项目 TOP 5 - {today}",
                    },
                    "template": "orange",
                },
                "elements": [],
            },
        }

        # 添加项目列表
        for i, line in enumerate(report.split("\n")):
            if line.startswith("## ") and not line.startswith("## 📊"):
                # 提取项目信息
                title = line.replace("## ", "").strip()
                card_data["card"]["elements"].append(
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": f"**{title}**"},
                    }
                )
            elif line.startswith("⭐ "):
                card_data["card"]["elements"].append(
                    {"tag": "div", "text": {"tag": "lark_md", "content": line}}
                )
            elif line.startswith("💡 "):
                card_data["card"]["elements"].append(
                    {"tag": "div", "text": {"tag": "lark_md", "content": line}}
                )
            elif line.startswith("🔗 "):
                url = line.replace("🔗 [查看项目](", "").replace(")", "")
                card_data["card"]["elements"].append(
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "查看项目"},
                                "type": "primary",
                                "url": url,
                            }
                        ],
                    }
                )
                card_data["card"]["elements"].append({"tag": "hr"})

        # 发送请求
        try:
            response = requests.post(
                self.feishu_webhook,
                json=card_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("✅ 飞书消息发送成功")
                    return True
                else:
                    print(f"❌ 飞书API错误: {result}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 发送失败: {e}")

        return False

    def run(self):
        """主运行流程"""
        print("🚀 开始获取 GitHub AI 热门项目...")

        # 获取数据
        repos = self.fetch_trending_repos()

        # 如果去重后不足5个，清空历史重新获取
        if len(repos) < 5:
            print(f"⚠️ 去重后仅剩 {len(repos)} 个项目，清空历史重新获取...")
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            repos = self.fetch_trending_repos()

        if not repos:
            print("⚠️ 使用备用方案获取...")
            repos = self.fetch_trending_from_web()

        if not repos:
            print("❌ 无法获取数据")
            return False

        print(f"✅ 获取到 {len(repos)} 个项目")

        # 保存推送历史（用于跨日去重）
        self.save_pushed_history(repos)

        # 生成报告
        report = self.generate_report(repos)

        # 保存到文件
        filename = f"report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ 报告已保存: {filename}")

        # 发送到飞书
        if self.feishu_webhook:
            self.send_to_feishu(report)
        else:
            print("⚠️ 未配置飞书 Webhook，跳过发送")

        return True


if __name__ == "__main__":
    bot = GitHubTrendingBot()
    bot.run()
