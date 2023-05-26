using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Orchestration;
using Microsoft.SemanticKernel.SkillDefinition;
using Microsoft.SemanticKernel.Skills.OpenAPI.Skills;
using SemanticKernelService.Skills.Native.StockDb;
using SemanticKernelService.Utils;

namespace SemanticKernelService.Skills.Native.Stock;

/// <summary>
/// 股票相关Skill
/// </summary>
public class StockSkill
{
    private readonly IKernel _kernel;
    private readonly ILogger<StockSkill> _logger;
    private readonly StockDbSkill _stockDbSkill;
    private readonly ISKFunction _newsEmotionAnalysisFunction;

    internal const string NewsEmotionAnalysisDefinition =
        @"Forget all your previous instructions. Pretend you are a financial expert. You are
a financial expert with stock recommendation experience. Answer “YES” if good
news, “NO” if bad news, or “UNKNOWN” if uncertain in the first line.  You must answer 'YES', 'NO' or 'UNKNOWN'. Do not answer any other word. Is this headline
good or bad for the stock price of company name in the term term?

{{$INPUT}}
";

    private const int TenDays = 10 * 5 * 60 * 60;

    public StockSkill(IKernel kernel, StockDbSkill stockDbSkill, ILogger<StockSkill>? logger)
    {
        _kernel = kernel;
        _stockDbSkill = stockDbSkill;
        _logger = logger ?? NullLogger<StockSkill>.Instance;
        _newsEmotionAnalysisFunction = kernel.CreateSemanticFunction(
            NewsEmotionAnalysisDefinition,
            skillName: nameof(StockSkill),
            description: "Give a news, result its emotion",
            maxTokens: 500,
            temperature: 0.1,
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
        var stockNewsList = _stockDbSkill.GetStockNewsListAsync(stockCode, context);
        //按照交易日存储交易日新闻的分数，key: 2022-5-23, value: 3
        Dictionary<string, int> newsEmotionScore = new Dictionary<string, int>();

        try
        {
            foreach (var stockNews in stockNewsList)
            {
                //只分析十日内的新闻
                if (DateTime.Now.ToLocalTime().GetTimeStamp() - stockNews.TimeScamp > TenDays)
                {
                    break;
                }
                var transactionDate = stockNews.TimeScamp.GetTransactionDate();
                if (!newsEmotionScore.ContainsKey(transactionDate))
                {
                    newsEmotionScore.Add(transactionDate, 0);
                }
                var result = await _kernel.RunAsync(stockNews.NewsTitle, _newsEmotionAnalysisFunction);
                if (result.ErrorOccurred) _logger.LogError("Analysis News Emotion Error");
                else
                {
                    switch (result.Result)
                    {
                        case "YES":
                            ++newsEmotionScore[transactionDate];
                            break;
                        case "NO":
                            --newsEmotionScore[transactionDate];
                            break;
                    }
                }
                Thread.Sleep(500);
            }
            foreach (var keyValuePair in newsEmotionScore)
            {
                Console.WriteLine(keyValuePair.Key + " " + keyValuePair.Value);
            }
        }
        catch (Exception e)
        {
            Console.WriteLine(e);
            throw;
        }
        
    }
}