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
    private readonly ILogger<StockDbSkill> _logger;

    public StockDbSkill(IKernel kernel, string mysqlConnectString, ILogger<StockDbSkill>? logger)
    {
        _kernel = kernel;
        _logger = logger ?? NullLogger<StockDbSkill>.Instance;

        var optionsBuilder = new DbContextOptionsBuilder<MySqlDatabaseContext>();
        var serverVersion = ServerVersion.AutoDetect(mysqlConnectString);
        optionsBuilder.UseMySql(mysqlConnectString, serverVersion);
        _dbContext = new MySqlDatabaseContext(optionsBuilder.Options);
    }

    [SKFunction("Given the stock code, obtain the news list in the database")]
    [SKFunctionName("GetStockNewsList")]
    [SKFunctionInput(Description = "The code of the stock")]
    public List<StockNews> GetStockNewsListAsync(string stockCode, SKContext context)
    {
        try
        {
            var result = _dbContext.StockNews.FromSql($"select * from stock_news where stock_code={stockCode} order by time_scamp desc").ToList();
            return result;
        }
        catch (Exception e)
        {
            Console.WriteLine(e);
            throw;
        }
    }
}