using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Orchestration;
using Microsoft.SemanticKernel.SkillDefinition;
using SemanticKernelService.Database;
using SemanticKernelService.Skills.Native.StockDb;
using SemanticKernelService.Utils;

namespace SemanticKernelService.Skills.Native.Stock;

/// <summary>
/// 股票相关Skill
/// </summary>
public class StockSkill
{
    private readonly IKernel _kernel;
    private readonly ILogger _logger;
    private readonly StockDbSkill _stockDbSkill;
    /// <summary>
    /// 给定一条新闻，分析其情绪
    /// </summary>
    private readonly ISKFunction _newsEmotionAnalysisFunction;
    
    /// <summary>
    /// 给定一个新闻列表，返回它们的情绪列表
    /// </summary>
    private readonly ISKFunction _newsListEmotionAnalysisFunction;

    /// <summary>
    /// 给定一个新闻列表，总结其整体的情绪
    /// </summary>
    private readonly ISKFunction _summarizeNewsEmotionFunction;

    private const int TenDays = 10 * 24 * 60 * 60;
    private const int NewsListMaxToken = 500;
    private const int SummarizeNewsMaxToken = 2000;

    public StockSkill(IKernel kernel, StockDbSkill stockDbSkill, ILogger? logger)
    {
        _kernel = kernel;
        _stockDbSkill = stockDbSkill;
        _logger = logger ?? NullLogger.Instance;
        _newsEmotionAnalysisFunction = kernel.CreateSemanticFunction(
            StockSkillDefinition.NewsEmotionAnalysisDefinition,
            skillName: nameof(StockSkill),
            description: "Give a news, result its emotion",
            maxTokens: 500,
            temperature: 0.1,
            topP: 0.5
        );
        _newsListEmotionAnalysisFunction = kernel.CreateSemanticFunction(
            StockSkillDefinition.NewsListEmotionAnalysisDefinition,
            skillName: nameof(StockSkill),
            description: "Give news list, result their emotion list",
            maxTokens: NewsListMaxToken,
            temperature: 0.1,
            topP: 0.5
        );
        _summarizeNewsEmotionFunction = kernel.CreateSemanticFunction(
            StockSkillDefinition.SummarizeNewsEmotionDefinition,
            skillName: nameof(StockSkill),
            description: "Give news list, summarize their emotion",
            maxTokens: SummarizeNewsMaxToken,
            temperature: 0.7,
            topP: 0.5
        );
    }

    /// <summary>
    /// 给定股票代码，在数据库中查找对应的新闻，通过大模型分析对其情感打分，正向1，负向-1，无情感0。将结果存储到数据库中
    /// </summary>
    /// <param name="stockCode">股票代码</param>
    /// <param name="context"></param>
    [SKFunction("Analyzing the Emotions of News on Designated Stocks")]
    [SKFunctionName("AnalysisStockNews")]
    [SKFunctionInput(Description = "The code of the stock to be analyzed")]
    public async Task AnalysisStockNews(string stockCode, SKContext context)
    {
        var stockNewsList = _stockDbSkill.GetStockNewsList(stockCode, context);

        var builder = new StringBuilder();
        
        var stockNewsAnalysisItemList = new List<StockNews>();

        for (var i = 0; i < stockNewsList.Count; ++i)
        {
            //新闻已经分析过则不再分析
            if (stockNewsList[i].Emotion != -2 || stockNewsList[i].NewsTitle.Length == 0) continue;

            //token已经满或者已经到达最后一个新闻或者时间已经到达设定时间就向语言模型进行一次请求
            //注意第三个条件成立需要保证新闻列表按照时间顺序倒序排列
            //因为每次分析过多条数可能会导致GPT分解失败，所以不让每次分析的新闻条数大于10
            if (builder.Length > NewsListMaxToken - 100 ||
                i >= stockNewsList.Count - 1 ||
                DateTime.Now.ToLocalTime().GetTimeStamp() - stockNewsList[i].TimeStamp > TenDays || 
                stockNewsAnalysisItemList.Count > 10)

        {
                //如果当前的新闻列表为空，那么继续
                if (builder.Length == 0) continue;
                
                //如果因为token到了而去请求，则需要-1
                if (builder.Length > NewsListMaxToken - 100 && i > 0) --i;
                builder.Remove(builder.Length - 1, 1);
                
                //请求语言模型
                _logger.LogError($"执行中 {builder}");
                var result = await _kernel.RunAsync(builder.ToString(), _newsListEmotionAnalysisFunction);
                _logger.LogError($"执行完毕 {result.Result}");
                if (result.ErrorOccurred)
                {
                    _logger.LogError($"AnalysisStockNews Error {result.LastErrorDescription}");
                    throw new Exception($"AnalysisStockNews Error {result.LastErrorDescription}");
                }
                
                //分析语言模型返回的结果
                var emotionList = GetEmotionList(result.Result);
                _logger.LogError($"emotion {emotionList.Count} news {stockNewsAnalysisItemList.Count}");

                //如果两者长度不一致，则不要添加到数据库中
                if (emotionList.Count == stockNewsAnalysisItemList.Count)
                {
                    for (var j = 0; j < stockNewsAnalysisItemList.Count; ++j)
                    {
                        stockNewsAnalysisItemList[j].Emotion = emotionList[j];
                    }
                    //存储到数据库中
                    _stockDbSkill.UpdateStockNewsList(stockNewsAnalysisItemList, context);
                }

                builder.Clear();
                stockNewsAnalysisItemList.Clear();

                if (DateTime.Now.ToLocalTime().GetTimeStamp() - stockNewsList[i].TimeStamp > TenDays) break;

                Thread.Sleep(500);
            }
            else
            {
                stockNewsAnalysisItemList.Add(stockNewsList[i]);
                builder.Append("###NEWS###:").Append(stockNewsList[i].NewsTitle.ReplaceSpecialSymbol()).Append(" ###NEWS END###\n");
            }
        }
    }

    [SKFunction("Summarize news list emotion of a day")]
    [SKFunctionName("SummarizeNewsEmotion")]
    [SKFunctionInput(Description = "The code of the stock to be summarized")]
    [SKFunctionContextParameter(Name = "day",
        Description = "Which day need to summarized, format: yyyy-MM-dd")]
    public async Task<string> SummarizeNewsEmotion(string stockCode, SKContext context)
    {
        //获取交易时间范围内的新闻
        if (!context.Variables.Get("day", out string day) || string.IsNullOrEmpty(day))
        {
            day = "1970-01-01";
        }
        DateTime dateTime = DateTime.Parse(day);
        var timeStamp = dateTime.GetTimeStamp();
        //获取在昨天15点之后到今天15点之间的新闻
        var startTime = timeStamp - 9 * 60 * 60;
        var endTime = timeStamp + 15 * 60 * 60;
        var dailyNewsList = _stockDbSkill.GetStockDailyNewsList(stockCode, startTime, endTime);
        
        var builder = new StringBuilder();
        foreach (var stockNews in dailyNewsList)
        {
            if (builder.Length > SummarizeNewsMaxToken - 200) break;
            builder.Append("NEWS:'").Append(stockNews.NewsTitle).Append("',\n");
        }
        //请求语言模型
        _logger.LogError($"执行中 {builder}");
        var result = await _kernel.RunAsync(builder.ToString(), _summarizeNewsEmotionFunction);
        _logger.LogError($"执行完毕 {result.Result}");

        var newsEmotion = new NewsEmotion
        {
            NewsTime = day, StockCode = stockCode, Emotion = result.Result
        };
        _stockDbSkill.UpdateNewsEmotion(newsEmotion);

        return newsEmotion.Emotion;
    }

    private List<int> GetEmotionList(string llmResult)
    {
        try
        {
            var result = new List<int>();
            foreach (var s in llmResult.Split(","))
            {
                //对于出现以,结尾的特殊处理
                if (s == "")
                {
                    continue;
                }
                result.Add(int.Parse(s));
            }

            return result;
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            throw new Exception($"Parse {llmResult} error: {e.Message}");
        }
    }
    
}