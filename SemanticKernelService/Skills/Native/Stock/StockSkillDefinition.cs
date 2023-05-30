namespace SemanticKernelService.Skills.Native.Stock;

public static class StockSkillDefinition
{
    internal const string NewsEmotionAnalysisDefinition =
        @"Forget all your previous instructions. Pretend you are a financial expert. You are
a financial expert with stock recommendation experience. Answer “YES” if good
news, “NO” if bad news, or “UNKNOWN” if uncertain in the first line.  You must answer 'YES', 'NO' or 'UNKNOWN'. Do not answer any other word. Is this headline
good or bad for the stock price of company name in the term term?

{{$INPUT}}
";
    
    internal const string NewsListEmotionAnalysisDefinition =
        @"Forget all your previous instructions. Pretend you are a financial expert. You are
a financial expert with stock recommendation experience. Answer “1” if good
news, “-1” if bad news, or “0” if uncertain in the first line. You receive a news list, please follow the example to return an emotional list.

[START EXAMPLE]
[INPUT]
NEWS: 'news1',
NEWS: 'news2',
NEWS: 'news3',
[RESULT] 
1,-1,0
[END EXAMPLE]

[INPUT]
{{$INPUT}}
[RESULT]
";

    internal const string SummarizeNewsEmotionDefinition = @"
[SUMMARIZATION RULES]
不要浪费词汇
使用简短、清晰、完整的句子
尽可能地详细
总结的最后必须要根据新闻整体情绪分析有关股票的涨跌情况

Summarize:
NEWS: '长城正面“硬刚”比亚迪，其实是开了一个好头！',
NEWS: '长城举报比亚迪事件发酵 股价双双下跌',
NEWS: '长城跟比亚迪掀桌子，究竟为什么',
+++++
今天的新闻主要围绕”长城举报比亚迪“这一事件。整体新闻呈消极状态。股市可能会呈下跌趋势。

Summarize this:
{{$INPUT}}
+++++
";
}