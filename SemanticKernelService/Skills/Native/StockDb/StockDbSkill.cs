using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Orchestration;
using Microsoft.SemanticKernel.SkillDefinition;
using SemanticKernelService.Database;

namespace SemanticKernelService.Skills.Native.StockDb;

/// <summary>
/// 股票数据库相关Skill
/// </summary>
public class StockDbSkill
{
    private readonly IKernel _kernel;
    private readonly MySqlDatabaseContext _dbContext;
    private readonly ILogger _logger;

    public StockDbSkill(IKernel kernel, string mysqlConnectString, ILogger? logger)
    {
        _kernel = kernel;
        _logger = logger ?? NullLogger.Instance;

        var optionsBuilder = new DbContextOptionsBuilder<MySqlDatabaseContext>();
        var serverVersion = ServerVersion.AutoDetect(mysqlConnectString);
        optionsBuilder.UseMySql(mysqlConnectString, serverVersion);
        _dbContext = new MySqlDatabaseContext(optionsBuilder.Options);
    }

    [SKFunction("Given the stock code, obtain the news list in the database")]
    [SKFunctionName("GetStockNewsList")]
    [SKFunctionInput(Description = "The code of the stock")]
    public List<StockNews> GetStockNewsList(string stockCode, SKContext context)
    {
        try
        {
            var result = _dbContext.StockNews.FromSql($"select * from stock_news where stock_code={stockCode} order by time_stamp desc").ToList();
            return result;
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            throw;
        }
    }

    [SKFunction("Update stock news list")]
    [SKFunctionName("UpdateStockNewsList")]
    [SKFunctionInput(Description = "The stock news list which need update")]
    public void UpdateStockNewsList(List<StockNews> stockNewsList, SKContext context)
    {
        try
        {
            foreach (var stockNews in stockNewsList)
            {
                UpdateStockNews(stockNews, context);
            }
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            throw;
        }
    }
    
    [SKFunction("Update stock news")]
    [SKFunctionName("UpdateStockNews")]
    [SKFunctionInput(Description = "The stock news list which need update")]
    public void UpdateStockNews(StockNews stockNews, SKContext context)
    {
        try
        {
            _dbContext.StockNews.Update(stockNews);
            _dbContext.SaveChanges();
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            throw;
        }
    }
    
    /// <summary>
    /// 获取交易日内的新闻
    /// </summary>
    /// <param name="stockCode"></param>
    /// <param name="startTime"></param>
    /// <param name="endTime"></param>
    /// <returns></returns>
    public List<StockNews> GetStockDailyNewsList(string stockCode, long startTime, long endTime)
    {
        try
        {
            var result = _dbContext.StockNews.FromSql($"select * from stock_news where stock_code={stockCode} and time_stamp >= {startTime} and time_stamp <= {endTime} order by time_stamp desc").ToList();
            return result;
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            throw;
        }
    }

    public void UpdateNewsEmotion(NewsEmotion newsEmotion)
    {
        try
        {
            _dbContext.NewsEmotion.Update(newsEmotion);
            _dbContext.SaveChanges();
        }
        catch (Exception e)
        {
            _logger.LogError($"Update news emotion error {e.Message} {e.InnerException?.Message}");
            throw;
        }
    }
}